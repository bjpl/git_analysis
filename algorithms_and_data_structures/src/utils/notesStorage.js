/**
 * LocalStorage Manager for Notes
 * Handles persistent storage with compression, versioning, and quota management
 */

import { compressData, decompressData } from './compression.js';
import { generateBackupKey, validateStorageData } from './storageHelpers.js';

class NotesStorage {
  constructor() {
    this.storageKey = 'notes_data';
    this.metaKey = 'notes_meta';
    this.backupPrefix = 'notes_backup_';
    this.version = '1.0.0';
    this.maxBackups = 5;
    this.compressionThreshold = 1024; // bytes
  }

  /**
   * Save a single note to storage
   */
  async saveNote(note) {
    try {
      const existingNotes = await this.loadNotes();
      const noteIndex = existingNotes.findIndex(n => n.id === note.id);
      
      if (noteIndex >= 0) {
        existingNotes[noteIndex] = note;
      } else {
        existingNotes.push(note);
      }

      await this.saveNotes(existingNotes);
      return true;
    } catch (error) {
      console.error('Failed to save note:', error);
      throw new Error(`Failed to save note: ${error.message}`);
    }
  }

  /**
   * Save all notes to storage with compression and backup
   */
  async saveNotes(notes) {
    try {
      await this.checkStorageQuota();
      await this.createBackup();

      const dataToSave = {
        notes: notes,
        version: this.version,
        savedAt: new Date().toISOString(),
        checksum: this.calculateChecksum(notes)
      };

      const serializedData = JSON.stringify(dataToSave);
      let finalData = serializedData;

      // Compress if data is large enough
      if (serializedData.length > this.compressionThreshold) {
        try {
          finalData = await compressData(serializedData);
          await this.setStorageMeta({ compressed: true, originalSize: serializedData.length });
        } catch (compressionError) {
          console.warn('Compression failed, saving uncompressed:', compressionError);
          await this.setStorageMeta({ compressed: false });
        }
      } else {
        await this.setStorageMeta({ compressed: false });
      }

      localStorage.setItem(this.storageKey, finalData);
      
      // Clean up old backups
      await this.cleanupOldBackups();

      return true;
    } catch (error) {
      console.error('Failed to save notes:', error);
      
      // Try to restore from backup if save fails
      await this.restoreFromBackup();
      throw new Error(`Failed to save notes: ${error.message}`);
    }
  }

  /**
   * Load all notes from storage
   */
  async loadNotes() {
    try {
      const data = localStorage.getItem(this.storageKey);
      if (!data) {
        return [];
      }

      const meta = await this.getStorageMeta();
      let parsedData;

      if (meta.compressed) {
        try {
          const decompressed = await decompressData(data);
          parsedData = JSON.parse(decompressed);
        } catch (decompressionError) {
          console.error('Decompression failed:', decompressionError);
          throw new Error('Failed to decompress notes data');
        }
      } else {
        parsedData = JSON.parse(data);
      }

      // Validate data structure
      const validation = validateStorageData(parsedData);
      if (!validation.isValid) {
        console.warn('Invalid storage data:', validation.errors);
        return await this.handleCorruptedData();
      }

      // Check version compatibility
      if (parsedData.version !== this.version) {
        return await this.migrateData(parsedData);
      }

      // Verify checksum
      const calculatedChecksum = this.calculateChecksum(parsedData.notes);
      if (calculatedChecksum !== parsedData.checksum) {
        console.warn('Checksum mismatch, data may be corrupted');
        return await this.handleCorruptedData();
      }

      return parsedData.notes || [];
    } catch (error) {
      console.error('Failed to load notes:', error);
      
      // Try to restore from backup
      const backupNotes = await this.restoreFromBackup();
      if (backupNotes) {
        return backupNotes;
      }
      
      return [];
    }
  }

  /**
   * Delete a specific note from storage
   */
  async deleteNote(noteId) {
    try {
      const notes = await this.loadNotes();
      const filteredNotes = notes.filter(note => note.id !== noteId);
      
      if (filteredNotes.length === notes.length) {
        throw new Error(`Note with id ${noteId} not found`);
      }

      await this.saveNotes(filteredNotes);
      return true;
    } catch (error) {
      console.error('Failed to delete note:', error);
      throw error;
    }
  }

  /**
   * Create a backup of current notes
   */
  async createBackup() {
    try {
      const existingData = localStorage.getItem(this.storageKey);
      if (!existingData) return;

      const backupKey = generateBackupKey(this.backupPrefix);
      const backupData = {
        data: existingData,
        meta: await this.getStorageMeta(),
        createdAt: new Date().toISOString(),
        version: this.version
      };

      localStorage.setItem(backupKey, JSON.stringify(backupData));
      
      // Update backup list
      const backups = this.getBackupList();
      backups.push(backupKey);
      localStorage.setItem(`${this.backupPrefix}list`, JSON.stringify(backups));

      return backupKey;
    } catch (error) {
      console.error('Failed to create backup:', error);
    }
  }

  /**
   * Restore notes from the most recent backup
   */
  async restoreFromBackup() {
    try {
      const backups = this.getBackupList();
      if (backups.length === 0) return null;

      // Try backups from most recent to oldest
      for (let i = backups.length - 1; i >= 0; i--) {
        const backupKey = backups[i];
        const backupDataStr = localStorage.getItem(backupKey);
        
        if (!backupDataStr) continue;

        try {
          const backupData = JSON.parse(backupDataStr);
          
          // Restore main data
          localStorage.setItem(this.storageKey, backupData.data);
          await this.setStorageMeta(backupData.meta);

          // Load and return the restored notes
          const restoredNotes = await this.loadNotes();
          console.log(`Successfully restored from backup: ${backupKey}`);
          return restoredNotes;
        } catch (backupError) {
          console.error(`Failed to restore from backup ${backupKey}:`, backupError);
          continue;
        }
      }

      return null;
    } catch (error) {
      console.error('Failed to restore from backup:', error);
      return null;
    }
  }

  /**
   * Handle corrupted data by attempting recovery
   */
  async handleCorruptedData() {
    console.warn('Attempting to recover from corrupted data');
    
    // Try to restore from backup
    const backupNotes = await this.restoreFromBackup();
    if (backupNotes) {
      return backupNotes;
    }

    // If no backup available, try to parse partial data
    try {
      const rawData = localStorage.getItem(this.storageKey);
      if (rawData) {
        // Attempt to extract notes array from corrupted JSON
        const notesMatch = rawData.match(/"notes":\s*(\[.*?\])/s);
        if (notesMatch) {
          const notesArray = JSON.parse(notesMatch[1]);
          if (Array.isArray(notesArray)) {
            console.log('Partially recovered notes from corrupted data');
            return notesArray;
          }
        }
      }
    } catch (recoveryError) {
      console.error('Failed to recover corrupted data:', recoveryError);
    }

    return [];
  }

  /**
   * Migrate data between versions
   */
  async migrateData(oldData) {
    try {
      let migratedNotes = oldData.notes || [];

      // Add migration logic here for future versions
      switch (oldData.version) {
        case undefined:
        case '0.9.0':
          // Migrate from pre-1.0 format
          migratedNotes = migratedNotes.map(note => ({
            ...note,
            metadata: note.metadata || {
              wordCount: this.countWords(note.content || ''),
              readingTime: this.calculateReadingTime(note.content || '')
            }
          }));
          break;
        
        default:
          console.warn(`Unknown version ${oldData.version}, attempting direct migration`);
      }

      // Save migrated data
      await this.saveNotes(migratedNotes);
      console.log(`Successfully migrated data from version ${oldData.version} to ${this.version}`);
      
      return migratedNotes;
    } catch (error) {
      console.error('Data migration failed:', error);
      throw new Error(`Failed to migrate data: ${error.message}`);
    }
  }

  /**
   * Check storage quota and clean up if needed
   */
  async checkStorageQuota() {
    try {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        const usedPercentage = (estimate.usage / estimate.quota) * 100;

        if (usedPercentage > 80) {
          console.warn(`Storage usage high: ${usedPercentage.toFixed(1)}%`);
          await this.cleanupOldBackups();
          
          if (usedPercentage > 90) {
            throw new Error('Storage quota exceeded');
          }
        }
      }
    } catch (error) {
      console.error('Storage quota check failed:', error);
    }
  }

  /**
   * Clean up old backups to free storage space
   */
  async cleanupOldBackups() {
    try {
      const backups = this.getBackupList();
      
      if (backups.length <= this.maxBackups) return;

      const backupsToDelete = backups.slice(0, backups.length - this.maxBackups);
      
      backupsToDelete.forEach(backupKey => {
        localStorage.removeItem(backupKey);
      });

      const remainingBackups = backups.slice(backupsToDelete.length);
      localStorage.setItem(`${this.backupPrefix}list`, JSON.stringify(remainingBackups));

      console.log(`Cleaned up ${backupsToDelete.length} old backups`);
    } catch (error) {
      console.error('Failed to cleanup old backups:', error);
    }
  }

  /**
   * Clear all notes and related data
   */
  async clearAll() {
    try {
      // Remove main data
      localStorage.removeItem(this.storageKey);
      localStorage.removeItem(this.metaKey);

      // Remove all backups
      const backups = this.getBackupList();
      backups.forEach(backupKey => {
        localStorage.removeItem(backupKey);
      });
      localStorage.removeItem(`${this.backupPrefix}list`);

      return true;
    } catch (error) {
      console.error('Failed to clear all data:', error);
      throw error;
    }
  }

  /**
   * Get storage usage statistics
   */
  async getStorageInfo() {
    try {
      const notes = await this.loadNotes();
      const rawData = localStorage.getItem(this.storageKey);
      const meta = await this.getStorageMeta();
      const backups = this.getBackupList();

      let totalSize = 0;
      let backupSize = 0;

      // Calculate main data size
      if (rawData) {
        totalSize += rawData.length * 2; // UTF-16 encoding
      }

      // Calculate backup sizes
      backups.forEach(backupKey => {
        const backupData = localStorage.getItem(backupKey);
        if (backupData) {
          backupSize += backupData.length * 2;
        }
      });

      totalSize += backupSize;

      let quotaInfo = null;
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        quotaInfo = await navigator.storage.estimate();
      }

      return {
        notesCount: notes.length,
        dataSize: rawData ? rawData.length * 2 : 0,
        backupCount: backups.length,
        backupSize,
        totalSize,
        compressed: meta.compressed,
        quota: quotaInfo,
        usagePercentage: quotaInfo ? (quotaInfo.usage / quotaInfo.quota) * 100 : null
      };
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return null;
    }
  }

  // Helper methods
  getBackupList() {
    try {
      const backupListStr = localStorage.getItem(`${this.backupPrefix}list`);
      return backupListStr ? JSON.parse(backupListStr) : [];
    } catch {
      return [];
    }
  }

  async getStorageMeta() {
    try {
      const metaStr = localStorage.getItem(this.metaKey);
      return metaStr ? JSON.parse(metaStr) : { compressed: false };
    } catch {
      return { compressed: false };
    }
  }

  async setStorageMeta(meta) {
    try {
      localStorage.setItem(this.metaKey, JSON.stringify(meta));
    } catch (error) {
      console.error('Failed to set storage meta:', error);
    }
  }

  calculateChecksum(data) {
    const str = JSON.stringify(data);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(16);
  }

  countWords(text) {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  }

  calculateReadingTime(text) {
    const wordsPerMinute = 200;
    const wordCount = this.countWords(text);
    return Math.ceil(wordCount / wordsPerMinute);
  }
}

// Create singleton instance
export const notesStorage = new NotesStorage();
export default NotesStorage;