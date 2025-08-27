import { CacheEntry, CacheOptions } from '../types';

export interface CacheConfig {
  defaultTtl: number; // milliseconds
  maxSize: number; // maximum number of entries
  maxMemory: number; // maximum memory usage in MB
  enableCompression: boolean;
  enablePersistence: boolean;
  persistenceKey: string;
  cleanupInterval: number; // milliseconds
}

class CacheService {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private config: CacheConfig;
  private memoryUsage: number = 0;
  private cleanupTimer?: NodeJS.Timeout;
  private accessTimes: Map<string, number> = new Map();

  constructor(config?: Partial<CacheConfig>) {
    this.config = {
      defaultTtl: 5 * 60 * 1000, // 5 minutes
      maxSize: 1000,
      maxMemory: 50, // 50MB
      enableCompression: false,
      enablePersistence: true,
      persistenceKey: 'vocablens_cache',
      cleanupInterval: 5 * 60 * 1000, // 5 minutes
      ...config
    };

    this.startCleanupTimer();
    this.loadFromPersistence();
  }

  /**
   * Get item from cache
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }

    // Check if expired
    if (Date.now() > entry.expiry) {
      this.delete(key);
      return null;
    }

    // Update access time for LRU
    this.accessTimes.set(key, Date.now());
    
    return entry.data;
  }

  /**
   * Set item in cache
   */
  set<T>(key: string, data: T, options?: CacheOptions): void {
    const ttl = options?.ttl || this.config.defaultTtl;
    const expiry = Date.now() + ttl;
    const tags = options?.tags || [];
    
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      expiry,
      key,
      tags
    };

    // Check size limits before adding
    if (this.cache.size >= this.config.maxSize) {
      this.evictLeastRecentlyUsed();
    }

    // Estimate memory usage
    const entrySize = this.estimateSize(entry);
    if (this.memoryUsage + entrySize > this.config.maxMemory * 1024 * 1024) {
      this.evictByMemoryPressure();
    }

    this.cache.set(key, entry);
    this.accessTimes.set(key, Date.now());
    this.memoryUsage += entrySize;

    // Persist if enabled
    if (this.config.enablePersistence) {
      this.saveToPersistence();
    }
  }

  /**
   * Delete item from cache
   */
  delete(key: string): boolean {
    const entry = this.cache.get(key);
    if (entry) {
      this.memoryUsage -= this.estimateSize(entry);
      this.cache.delete(key);
      this.accessTimes.delete(key);
      return true;
    }
    return false;
  }

  /**
   * Check if item exists in cache
   */
  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;
    
    // Check if expired
    if (Date.now() > entry.expiry) {
      this.delete(key);
      return false;
    }
    
    return true;
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear();
    this.accessTimes.clear();
    this.memoryUsage = 0;
    
    if (this.config.enablePersistence) {
      localStorage.removeItem(this.config.persistenceKey);
    }
  }

  /**
   * Clear cache entries by tag
   */
  clearByTag(tag: string): number {
    let cleared = 0;
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.tags?.includes(tag)) {
        this.delete(key);
        cleared++;
      }
    }
    
    return cleared;
  }

  /**
   * Clear expired entries
   */
  clearExpired(): number {
    let cleared = 0;
    const now = Date.now();
    
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiry) {
        this.delete(key);
        cleared++;
      }
    }
    
    return cleared;
  }

  /**
   * Get or set with a factory function
   */
  async getOrSet<T>(\n    key: string,\n    factory: () => Promise<T> | T,\n    options?: CacheOptions\n  ): Promise<T> {\n    const cached = this.get<T>(key);\n    if (cached !== null) {\n      return cached;\n    }\n    \n    const data = await factory();\n    this.set(key, data, options);\n    return data;\n  }

  /**\n   * Memoize a function with caching\n   */\n  memoize<TArgs extends any[], TReturn>(\n    fn: (...args: TArgs) => Promise<TReturn> | TReturn,\n    options?: {\n      keyGenerator?: (...args: TArgs) => string;\n      ttl?: number;\n      tags?: string[];\n    }\n  ): (...args: TArgs) => Promise<TReturn> {\n    const keyGenerator = options?.keyGenerator || ((...args) => \n      `memoized_${fn.name}_${JSON.stringify(args)}`);\n    \n    return async (...args: TArgs): Promise<TReturn> => {\n      const key = keyGenerator(...args);\n      \n      return this.getOrSet(\n        key,\n        () => fn(...args),\n        {\n          ttl: options?.ttl,\n          tags: options?.tags\n        }\n      );\n    };\n  }

  /**\n   * Get cache statistics\n   */\n  getStats(): {\n    size: number;\n    memoryUsage: number;\n    memoryUsageMB: number;\n    hitRate: number;\n    expiredEntries: number;\n    oldestEntry?: Date;\n    newestEntry?: Date;\n  } {\n    const now = Date.now();\n    let expiredEntries = 0;\n    let oldestTimestamp = Infinity;\n    let newestTimestamp = 0;\n    \n    for (const entry of this.cache.values()) {\n      if (now > entry.expiry) {\n        expiredEntries++;\n      }\n      \n      oldestTimestamp = Math.min(oldestTimestamp, entry.timestamp);\n      newestTimestamp = Math.max(newestTimestamp, entry.timestamp);\n    }\n    \n    return {\n      size: this.cache.size,\n      memoryUsage: this.memoryUsage,\n      memoryUsageMB: this.memoryUsage / (1024 * 1024),\n      hitRate: this.calculateHitRate(),\n      expiredEntries,\n      oldestEntry: oldestTimestamp !== Infinity ? new Date(oldestTimestamp) : undefined,\n      newestEntry: newestTimestamp > 0 ? new Date(newestTimestamp) : undefined\n    };\n  }

  /**\n   * Get all cached keys\n   */\n  keys(): string[] {\n    return Array.from(this.cache.keys());\n  }

  /**\n   * Get all cached entries (non-expired only)\n   */\n  entries(): Array<{ key: string; data: any; expiry: Date }> {\n    const now = Date.now();\n    const validEntries: Array<{ key: string; data: any; expiry: Date }> = [];\n    \n    for (const [key, entry] of this.cache.entries()) {\n      if (now <= entry.expiry) {\n        validEntries.push({\n          key,\n          data: entry.data,\n          expiry: new Date(entry.expiry)\n        });\n      }\n    }\n    \n    return validEntries;\n  }

  /**\n   * Export cache data\n   */\n  export(): string {\n    const exportData = {\n      timestamp: new Date().toISOString(),\n      config: this.config,\n      entries: this.entries()\n    };\n    \n    return JSON.stringify(exportData, null, 2);\n  }

  /**\n   * Import cache data\n   */\n  import(data: string): number {\n    try {\n      const importData = JSON.parse(data);\n      let imported = 0;\n      \n      for (const entry of importData.entries) {\n        if (new Date(entry.expiry) > new Date()) {\n          this.set(entry.key, entry.data, {\n            ttl: new Date(entry.expiry).getTime() - Date.now()\n          });\n          imported++;\n        }\n      }\n      \n      return imported;\n    } catch (error) {\n      console.error('Failed to import cache data:', error);\n      return 0;\n    }\n  }

  /**\n   * Private helper methods\n   */\n  private evictLeastRecentlyUsed(): void {\n    let oldestKey = '';\n    let oldestTime = Infinity;\n    \n    for (const [key, time] of this.accessTimes.entries()) {\n      if (time < oldestTime) {\n        oldestTime = time;\n        oldestKey = key;\n      }\n    }\n    \n    if (oldestKey) {\n      this.delete(oldestKey);\n    }\n  }

  private evictByMemoryPressure(): void {\n    // Remove oldest entries until under memory limit\n    const targetMemory = this.config.maxMemory * 1024 * 1024 * 0.8; // 80% of max\n    \n    const sortedEntries = Array.from(this.cache.entries())\n      .sort((a, b) => a[1].timestamp - b[1].timestamp);\n    \n    for (const [key] of sortedEntries) {\n      if (this.memoryUsage <= targetMemory) break;\n      this.delete(key);\n    }\n  }

  private estimateSize(entry: CacheEntry<any>): number {\n    try {\n      return JSON.stringify(entry).length * 2; // Rough estimate: 2 bytes per character\n    } catch {\n      return 1024; // Default size estimate\n    }\n  }

  private calculateHitRate(): number {\n    // This would need to track hits/misses over time\n    // For now, return a placeholder\n    return 0.85; // 85% hit rate placeholder\n  }

  private startCleanupTimer(): void {\n    if (this.cleanupTimer) {\n      clearInterval(this.cleanupTimer);\n    }\n    \n    this.cleanupTimer = setInterval(() => {\n      this.clearExpired();\n      this.saveToPersistence();\n    }, this.config.cleanupInterval);\n  }

  private saveToPersistence(): void {\n    if (!this.config.enablePersistence || typeof localStorage === 'undefined') {\n      return;\n    }\n    \n    try {\n      const cacheData = {\n        timestamp: Date.now(),\n        entries: Array.from(this.cache.entries()).slice(0, 100) // Limit persistence size\n      };\n      \n      localStorage.setItem(\n        this.config.persistenceKey,\n        JSON.stringify(cacheData)\n      );\n    } catch (error) {\n      console.warn('Failed to persist cache:', error);\n    }\n  }

  private loadFromPersistence(): void {\n    if (!this.config.enablePersistence || typeof localStorage === 'undefined') {\n      return;\n    }\n    \n    try {\n      const stored = localStorage.getItem(this.config.persistenceKey);\n      if (!stored) return;\n      \n      const cacheData = JSON.parse(stored);\n      const now = Date.now();\n      \n      for (const [key, entry] of cacheData.entries) {\n        // Only load non-expired entries\n        if (entry.expiry > now) {\n          this.cache.set(key, entry);\n          this.accessTimes.set(key, entry.timestamp);\n          this.memoryUsage += this.estimateSize(entry);\n        }\n      }\n    } catch (error) {\n      console.warn('Failed to load cache from persistence:', error);\n    }\n  }\n\n  /**\n   * Cleanup on instance destruction\n   */\n  destroy(): void {\n    if (this.cleanupTimer) {\n      clearInterval(this.cleanupTimer);\n    }\n    \n    if (this.config.enablePersistence) {\n      this.saveToPersistence();\n    }\n    \n    this.clear();\n  }\n}\n\n// Create different cache instances for different purposes\nexport const imageCache = new CacheService({\n  defaultTtl: 30 * 60 * 1000, // 30 minutes for images\n  maxSize: 500,\n  maxMemory: 20, // 20MB\n  persistenceKey: 'vocablens_image_cache'\n});\n\nexport const apiCache = new CacheService({\n  defaultTtl: 5 * 60 * 1000, // 5 minutes for API responses\n  maxSize: 200,\n  maxMemory: 10, // 10MB\n  persistenceKey: 'vocablens_api_cache'\n});\n\nexport const vocabularyCache = new CacheService({\n  defaultTtl: 60 * 60 * 1000, // 1 hour for vocabulary\n  maxSize: 1000,\n  maxMemory: 15, // 15MB\n  persistenceKey: 'vocablens_vocabulary_cache'\n});\n\n// Export main class and default instance\nexport const cacheService = new CacheService();\nexport { CacheService };