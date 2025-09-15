/**
 * Storage Helper Utilities
 * Helper functions for storage operations and data management
 */

/**
 * Generate backup key with timestamp
 */
export function generateBackupKey(prefix = 'backup_') {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const randomSuffix = Math.random().toString(36).substring(2, 8);
  return `${prefix}${timestamp}_${randomSuffix}`;
}

/**
 * Validate storage data structure
 */
export function validateStorageData(data) {
  const errors = [];

  if (!data || typeof data !== 'object') {
    return { isValid: false, errors: ['Storage data must be an object'] };
  }

  // Check required fields
  if (!data.notes) {
    errors.push('Missing notes array');
  } else if (!Array.isArray(data.notes)) {
    errors.push('Notes must be an array');
  }

  if (!data.version) {
    errors.push('Missing version field');
  } else if (typeof data.version !== 'string') {
    errors.push('Version must be a string');
  }

  if (!data.savedAt) {
    errors.push('Missing savedAt field');
  } else {
    const savedDate = new Date(data.savedAt);
    if (isNaN(savedDate.getTime())) {
      errors.push('savedAt must be a valid date');
    }
  }

  // Validate notes structure
  if (Array.isArray(data.notes)) {
    data.notes.forEach((note, index) => {
      if (!note || typeof note !== 'object') {
        errors.push(`Note at index ${index} is not an object`);
        return;
      }

      if (!note.id) {
        errors.push(`Note at index ${index} missing id field`);
      }

      if (!note.title) {
        errors.push(`Note at index ${index} missing title field`);
      }

      if (note.createdAt) {
        const createdDate = new Date(note.createdAt);
        if (isNaN(createdDate.getTime())) {
          errors.push(`Note at index ${index} has invalid createdAt date`);
        }
      }

      if (note.updatedAt) {
        const updatedDate = new Date(note.updatedAt);
        if (isNaN(updatedDate.getTime())) {
          errors.push(`Note at index ${index} has invalid updatedAt date`);
        }
      }
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
    noteCount: Array.isArray(data.notes) ? data.notes.length : 0
  };
}

/**
 * Calculate storage size in bytes
 */
export function calculateStorageSize(data) {
  if (typeof data === 'string') {
    return data.length * 2; // UTF-16 encoding
  }
  
  try {
    const jsonString = JSON.stringify(data);
    return jsonString.length * 2;
  } catch (error) {
    console.error('Failed to calculate storage size:', error);
    return 0;
  }
}

/**
 * Get available storage space
 */
export async function getAvailableStorage() {
  try {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      const estimate = await navigator.storage.estimate();
      return {
        quota: estimate.quota,
        usage: estimate.usage,
        available: estimate.quota - estimate.usage,
        usagePercentage: (estimate.usage / estimate.quota) * 100
      };
    }
  } catch (error) {
    console.error('Failed to get storage estimate:', error);
  }

  // Fallback: estimate based on localStorage
  try {
    const testKey = '_storage_test_';
    const testValue = 'x'.repeat(1024); // 1KB test
    let availableSpace = 0;

    // Try to find localStorage limit
    for (let i = 0; i < 10000; i++) { // Max 10MB test
      try {
        localStorage.setItem(testKey + i, testValue);
        availableSpace += 1024;
      } catch (e) {
        // Clean up test data
        for (let j = 0; j <= i; j++) {
          localStorage.removeItem(testKey + j);
        }
        break;
      }
    }

    return {
      quota: availableSpace + getCurrentStorageUsage(),
      usage: getCurrentStorageUsage(),
      available: availableSpace,
      usagePercentage: null,
      estimated: true
    };
  } catch (error) {
    console.error('Failed to estimate storage:', error);
    return null;
  }
}

/**
 * Get current localStorage usage
 */
function getCurrentStorageUsage() {
  let totalSize = 0;
  
  try {
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        totalSize += (localStorage[key].length + key.length) * 2;
      }
    }
  } catch (error) {
    console.error('Failed to calculate localStorage usage:', error);
  }
  
  return totalSize;
}

/**
 * Clean up old or orphaned storage entries
 */
export function cleanupStorage(options = {}) {
  const {
    maxAge = 30 * 24 * 60 * 60 * 1000, // 30 days in ms
    keyPatterns = [],
    dryRun = false,
    maxEntries = null
  } = options;

  const now = Date.now();
  const keysToDelete = [];
  const storageEntries = [];

  // Collect all storage entries
  try {
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        const value = localStorage[key];
        let timestamp = null;
        let shouldCheck = false;

        // Check if key matches any pattern
        if (keyPatterns.length === 0) {
          shouldCheck = true;
        } else {
          shouldCheck = keyPatterns.some(pattern => {
            if (typeof pattern === 'string') {
              return key.includes(pattern);
            } else if (pattern instanceof RegExp) {
              return pattern.test(key);
            }
            return false;
          });
        }

        if (!shouldCheck) continue;

        // Try to extract timestamp from value
        try {
          const parsed = JSON.parse(value);
          if (parsed && typeof parsed === 'object') {
            timestamp = parsed.savedAt || parsed.createdAt || parsed.timestamp;
          }
        } catch {
          // Not JSON, try to extract from key
          const match = key.match(/(\d{4}-\d{2}-\d{2})/);
          if (match) {
            timestamp = new Date(match[1]).toISOString();
          }
        }

        storageEntries.push({
          key,
          value,
          timestamp,
          age: timestamp ? now - new Date(timestamp).getTime() : null,
          size: (key.length + value.length) * 2
        });
      }
    }

    // Sort by age (oldest first)
    storageEntries.sort((a, b) => {
      if (!a.timestamp && !b.timestamp) return 0;
      if (!a.timestamp) return 1;
      if (!b.timestamp) return -1;
      return new Date(b.timestamp) - new Date(a.timestamp);
    });

    // Identify entries to delete
    storageEntries.forEach(entry => {
      let shouldDelete = false;

      // Delete by age
      if (maxAge && entry.age && entry.age > maxAge) {
        shouldDelete = true;
      }

      // Delete by count (keep only most recent maxEntries)
      if (maxEntries && storageEntries.indexOf(entry) >= maxEntries) {
        shouldDelete = true;
      }

      if (shouldDelete) {
        keysToDelete.push(entry.key);
      }
    });

    // Perform deletion
    if (!dryRun) {
      keysToDelete.forEach(key => {
        try {
          localStorage.removeItem(key);
        } catch (error) {
          console.error(`Failed to delete storage key ${key}:`, error);
        }
      });
    }

    return {
      totalEntries: storageEntries.length,
      deletedKeys: keysToDelete,
      deletedCount: keysToDelete.length,
      freedSpace: keysToDelete.reduce((total, key) => {
        const entry = storageEntries.find(e => e.key === key);
        return total + (entry ? entry.size : 0);
      }, 0),
      remainingEntries: storageEntries.length - keysToDelete.length
    };

  } catch (error) {
    console.error('Storage cleanup failed:', error);
    return null;
  }
}

/**
 * Export storage data
 */
export function exportStorageData(keyPatterns = []) {
  const exportData = {};
  const metadata = {
    exportedAt: new Date().toISOString(),
    version: '1.0.0',
    entries: 0,
    totalSize: 0
  };

  try {
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        let shouldExport = false;

        if (keyPatterns.length === 0) {
          shouldExport = true;
        } else {
          shouldExport = keyPatterns.some(pattern => {
            if (typeof pattern === 'string') {
              return key.includes(pattern);
            } else if (pattern instanceof RegExp) {
              return pattern.test(key);
            }
            return false;
          });
        }

        if (shouldExport) {
          const value = localStorage[key];
          exportData[key] = value;
          metadata.entries++;
          metadata.totalSize += (key.length + value.length) * 2;
        }
      }
    }

    return {
      metadata,
      data: exportData
    };

  } catch (error) {
    console.error('Failed to export storage data:', error);
    throw new Error(`Storage export failed: ${error.message}`);
  }
}

/**
 * Import storage data
 */
export function importStorageData(importData, options = {}) {
  const {
    overwrite = false,
    keyPrefix = '',
    validate = true
  } = options;

  const results = {
    imported: 0,
    skipped: 0,
    errors: [],
    importedKeys: []
  };

  try {
    // Validate import data structure
    if (validate) {
      if (!importData || typeof importData !== 'object') {
        throw new Error('Invalid import data structure');
      }

      if (!importData.data || typeof importData.data !== 'object') {
        throw new Error('Import data missing data field');
      }
    }

    const dataToImport = importData.data || importData;

    Object.entries(dataToImport).forEach(([key, value]) => {
      const importKey = keyPrefix + key;

      try {
        // Check if key already exists
        if (!overwrite && localStorage.getItem(importKey) !== null) {
          results.skipped++;
          return;
        }

        // Validate value
        if (typeof value !== 'string') {
          throw new Error(`Value for key ${key} must be a string`);
        }

        // Import the item
        localStorage.setItem(importKey, value);
        results.imported++;
        results.importedKeys.push(importKey);

      } catch (error) {
        results.errors.push({
          key,
          error: error.message
        });
      }
    });

    return results;

  } catch (error) {
    console.error('Failed to import storage data:', error);
    throw new Error(`Storage import failed: ${error.message}`);
  }
}

/**
 * Create storage snapshot
 */
export function createStorageSnapshot(keyPatterns = []) {
  const snapshot = {
    timestamp: new Date().toISOString(),
    entries: {},
    metadata: {
      totalKeys: 0,
      totalSize: 0,
      patterns: keyPatterns
    }
  };

  try {
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        let shouldInclude = false;

        if (keyPatterns.length === 0) {
          shouldInclude = true;
        } else {
          shouldInclude = keyPatterns.some(pattern => {
            if (typeof pattern === 'string') {
              return key.includes(pattern);
            } else if (pattern instanceof RegExp) {
              return pattern.test(key);
            }
            return false;
          });
        }

        if (shouldInclude) {
          const value = localStorage[key];
          snapshot.entries[key] = {
            value,
            size: (key.length + value.length) * 2,
            timestamp: snapshot.timestamp
          };
          snapshot.metadata.totalKeys++;
          snapshot.metadata.totalSize += snapshot.entries[key].size;
        }
      }
    }

    return snapshot;

  } catch (error) {
    console.error('Failed to create storage snapshot:', error);
    throw new Error(`Snapshot creation failed: ${error.message}`);
  }
}

/**
 * Compare storage snapshots
 */
export function compareStorageSnapshots(snapshot1, snapshot2) {
  const comparison = {
    added: [],
    removed: [],
    modified: [],
    unchanged: [],
    summary: {
      totalChanges: 0,
      sizeDifference: 0
    }
  };

  try {
    const keys1 = new Set(Object.keys(snapshot1.entries));
    const keys2 = new Set(Object.keys(snapshot2.entries));
    const allKeys = new Set([...keys1, ...keys2]);

    allKeys.forEach(key => {
      const entry1 = snapshot1.entries[key];
      const entry2 = snapshot2.entries[key];

      if (!entry1 && entry2) {
        // Added
        comparison.added.push({
          key,
          value: entry2.value,
          size: entry2.size
        });
        comparison.summary.totalChanges++;
        comparison.summary.sizeDifference += entry2.size;

      } else if (entry1 && !entry2) {
        // Removed
        comparison.removed.push({
          key,
          value: entry1.value,
          size: entry1.size
        });
        comparison.summary.totalChanges++;
        comparison.summary.sizeDifference -= entry1.size;

      } else if (entry1 && entry2) {
        if (entry1.value !== entry2.value) {
          // Modified
          comparison.modified.push({
            key,
            oldValue: entry1.value,
            newValue: entry2.value,
            oldSize: entry1.size,
            newSize: entry2.size,
            sizeDifference: entry2.size - entry1.size
          });
          comparison.summary.totalChanges++;
          comparison.summary.sizeDifference += entry2.size - entry1.size;
        } else {
          // Unchanged
          comparison.unchanged.push({
            key,
            size: entry1.size
          });
        }
      }
    });

    return comparison;

  } catch (error) {
    console.error('Failed to compare snapshots:', error);
    throw new Error(`Snapshot comparison failed: ${error.message}`);
  }
}

/**
 * Monitor storage usage
 */
export function createStorageMonitor(callback, interval = 5000) {
  let isMonitoring = false;
  let intervalId = null;
  let lastUsage = null;

  const monitor = {
    start() {
      if (isMonitoring) return;
      
      isMonitoring = true;
      intervalId = setInterval(async () => {
        try {
          const currentUsage = await getAvailableStorage();
          
          if (lastUsage && callback) {
            const changes = {
              usageChange: currentUsage.usage - lastUsage.usage,
              percentageChange: currentUsage.usagePercentage - lastUsage.usagePercentage,
              current: currentUsage,
              previous: lastUsage
            };
            
            callback(changes);
          }
          
          lastUsage = currentUsage;
        } catch (error) {
          console.error('Storage monitoring error:', error);
        }
      }, interval);
    },

    stop() {
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
      isMonitoring = false;
    },

    isRunning() {
      return isMonitoring;
    }
  };

  return monitor;
}