// Data Management and Persistence System
export class DataManager {
    constructor() {
        this.storagePrefix = 'number_sense_3s_';
        this.currentUser = null;
        this.db = null;
        this.initializeStorage();
    }

    initializeStorage() {
        // Check for IndexedDB support
        if ('indexedDB' in window) {
            this.initIndexedDB();
        } else {
            console.log('IndexedDB not supported, falling back to localStorage');
            this.useLocalStorage = true;
        }
    }

    async initIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('NumberSense3sDB', 1);

            request.onerror = () => {
                console.error('IndexedDB error:', request.error);
                this.useLocalStorage = true;
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('IndexedDB initialized');
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Users store
                if (!db.objectStoreNames.contains('users')) {
                    const userStore = db.createObjectStore('users', { keyPath: 'id' });
                    userStore.createIndex('username', 'username', { unique: true });
                    userStore.createIndex('email', 'email', { unique: false });
                }

                // Sessions store
                if (!db.objectStoreNames.contains('sessions')) {
                    const sessionStore = db.createObjectStore('sessions', { keyPath: 'id' });
                    sessionStore.createIndex('userId', 'userId', { unique: false });
                    sessionStore.createIndex('date', 'date', { unique: false });
                }

                // Progress store
                if (!db.objectStoreNames.contains('progress')) {
                    const progressStore = db.createObjectStore('progress', { keyPath: 'id' });
                    progressStore.createIndex('userId', 'userId', { unique: false });
                    progressStore.createIndex('mode', 'mode', { unique: false });
                }

                // Achievements store
                if (!db.objectStoreNames.contains('achievements')) {
                    const achievementStore = db.createObjectStore('achievements', { keyPath: 'id' });
                    achievementStore.createIndex('userId', 'userId', { unique: false });
                }

                // Analytics store
                if (!db.objectStoreNames.contains('analytics')) {
                    const analyticsStore = db.createObjectStore('analytics', { keyPath: 'id' });
                    analyticsStore.createIndex('userId', 'userId', { unique: false });
                    analyticsStore.createIndex('type', 'type', { unique: false });
                    analyticsStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };
        });
    }

    // User Management
    async createUser(userData) {
        const user = {
            id: this.generateId(),
            username: userData.username,
            email: userData.email || '',
            createdAt: new Date().toISOString(),
            lastActive: new Date().toISOString(),
            preferences: {
                difficulty: 'intermediate',
                soundEnabled: true,
                animationsEnabled: true,
                theme: 'light',
                ...userData.preferences
            },
            stats: {
                totalScore: 0,
                totalQuestions: 0,
                totalCorrect: 0,
                totalTime: 0,
                level: 1,
                experience: 0,
                streakDays: 0,
                lastPlayedDate: null
            },
            progress: {},
            achievements: []
        };

        if (this.useLocalStorage) {
            localStorage.setItem(`${this.storagePrefix}user_${user.id}`, JSON.stringify(user));
            return user;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['users'], 'readwrite');
            const store = transaction.objectStore('users');
            const request = store.add(user);

            request.onsuccess = () => resolve(user);
            request.onerror = () => reject(request.error);
        });
    }

    async getUser(userId) {
        if (this.useLocalStorage) {
            const userData = localStorage.getItem(`${this.storagePrefix}user_${userId}`);
            return userData ? JSON.parse(userData) : null;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['users'], 'readonly');
            const store = transaction.objectStore('users');
            const request = store.get(userId);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async updateUser(userId, updates) {
        const user = await this.getUser(userId);
        if (!user) return null;

        const updatedUser = {
            ...user,
            ...updates,
            lastActive: new Date().toISOString()
        };

        if (this.useLocalStorage) {
            localStorage.setItem(`${this.storagePrefix}user_${userId}`, JSON.stringify(updatedUser));
            return updatedUser;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['users'], 'readwrite');
            const store = transaction.objectStore('users');
            const request = store.put(updatedUser);

            request.onsuccess = () => resolve(updatedUser);
            request.onerror = () => reject(request.error);
        });
    }

    // Session Management
    async createSession(userId) {
        const session = {
            id: this.generateId(),
            userId: userId,
            startTime: new Date().toISOString(),
            endTime: null,
            duration: 0,
            questionsAttempted: 0,
            questionsCorrect: 0,
            score: 0,
            modes: [],
            achievements: [],
            performance: {
                accuracy: 0,
                averageResponseTime: 0,
                streakMax: 0
            }
        };

        if (this.useLocalStorage) {
            const sessions = this.getLocalStorageArray('sessions');
            sessions.push(session);
            this.setLocalStorageArray('sessions', sessions);
            return session;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['sessions'], 'readwrite');
            const store = transaction.objectStore('sessions');
            const request = store.add(session);

            request.onsuccess = () => resolve(session);
            request.onerror = () => reject(request.error);
        });
    }

    async updateSession(sessionId, updates) {
        if (this.useLocalStorage) {
            const sessions = this.getLocalStorageArray('sessions');
            const index = sessions.findIndex(s => s.id === sessionId);
            if (index !== -1) {
                sessions[index] = { ...sessions[index], ...updates };
                this.setLocalStorageArray('sessions', sessions);
                return sessions[index];
            }
            return null;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['sessions'], 'readwrite');
            const store = transaction.objectStore('sessions');
            const getRequest = store.get(sessionId);

            getRequest.onsuccess = () => {
                const session = getRequest.result;
                if (session) {
                    const updatedSession = { ...session, ...updates };
                    const putRequest = store.put(updatedSession);
                    putRequest.onsuccess = () => resolve(updatedSession);
                    putRequest.onerror = () => reject(putRequest.error);
                } else {
                    resolve(null);
                }
            };

            getRequest.onerror = () => reject(getRequest.error);
        });
    }

    // Progress Tracking
    async saveProgress(userId, mode, progressData) {
        const progress = {
            id: this.generateId(),
            userId: userId,
            mode: mode,
            timestamp: new Date().toISOString(),
            level: progressData.level,
            score: progressData.score,
            accuracy: progressData.accuracy,
            questionsAttempted: progressData.questionsAttempted,
            questionsCorrect: progressData.questionsCorrect,
            averageResponseTime: progressData.averageResponseTime,
            concepts: progressData.concepts || [],
            mistakes: progressData.mistakes || []
        };

        if (this.useLocalStorage) {
            const progressArray = this.getLocalStorageArray('progress');
            progressArray.push(progress);
            this.setLocalStorageArray('progress', progressArray);
            return progress;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['progress'], 'readwrite');
            const store = transaction.objectStore('progress');
            const request = store.add(progress);

            request.onsuccess = () => resolve(progress);
            request.onerror = () => reject(request.error);
        });
    }

    async getProgress(userId, mode = null) {
        if (this.useLocalStorage) {
            const progressArray = this.getLocalStorageArray('progress');
            let userProgress = progressArray.filter(p => p.userId === userId);
            if (mode) {
                userProgress = userProgress.filter(p => p.mode === mode);
            }
            return userProgress;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['progress'], 'readonly');
            const store = transaction.objectStore('progress');
            const index = store.index('userId');
            const request = index.getAll(userId);

            request.onsuccess = () => {
                let results = request.result;
                if (mode) {
                    results = results.filter(p => p.mode === mode);
                }
                resolve(results);
            };

            request.onerror = () => reject(request.error);
        });
    }

    // Achievement Management
    async unlockAchievement(userId, achievementId, achievementData) {
        const achievement = {
            id: this.generateId(),
            userId: userId,
            achievementId: achievementId,
            unlockedAt: new Date().toISOString(),
            ...achievementData
        };

        if (this.useLocalStorage) {
            const achievements = this.getLocalStorageArray('achievements');
            achievements.push(achievement);
            this.setLocalStorageArray('achievements', achievements);
            return achievement;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['achievements'], 'readwrite');
            const store = transaction.objectStore('achievements');
            const request = store.add(achievement);

            request.onsuccess = () => resolve(achievement);
            request.onerror = () => reject(request.error);
        });
    }

    async getAchievements(userId) {
        if (this.useLocalStorage) {
            const achievements = this.getLocalStorageArray('achievements');
            return achievements.filter(a => a.userId === userId);
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['achievements'], 'readonly');
            const store = transaction.objectStore('achievements');
            const index = store.index('userId');
            const request = index.getAll(userId);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // Analytics
    async logAnalytics(userId, type, data) {
        const analytics = {
            id: this.generateId(),
            userId: userId,
            type: type,
            timestamp: new Date().toISOString(),
            data: data
        };

        if (this.useLocalStorage) {
            const analyticsArray = this.getLocalStorageArray('analytics');
            analyticsArray.push(analytics);
            
            // Keep only last 1000 entries
            if (analyticsArray.length > 1000) {
                analyticsArray.splice(0, analyticsArray.length - 1000);
            }
            
            this.setLocalStorageArray('analytics', analyticsArray);
            return analytics;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['analytics'], 'readwrite');
            const store = transaction.objectStore('analytics');
            const request = store.add(analytics);

            request.onsuccess = () => resolve(analytics);
            request.onerror = () => reject(request.error);
        });
    }

    async getAnalytics(userId, type = null, startDate = null, endDate = null) {
        if (this.useLocalStorage) {
            let analyticsArray = this.getLocalStorageArray('analytics');
            analyticsArray = analyticsArray.filter(a => a.userId === userId);
            
            if (type) {
                analyticsArray = analyticsArray.filter(a => a.type === type);
            }
            
            if (startDate) {
                analyticsArray = analyticsArray.filter(a => new Date(a.timestamp) >= new Date(startDate));
            }
            
            if (endDate) {
                analyticsArray = analyticsArray.filter(a => new Date(a.timestamp) <= new Date(endDate));
            }
            
            return analyticsArray;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['analytics'], 'readonly');
            const store = transaction.objectStore('analytics');
            const index = store.index('userId');
            const request = index.getAll(userId);

            request.onsuccess = () => {
                let results = request.result;
                
                if (type) {
                    results = results.filter(a => a.type === type);
                }
                
                if (startDate) {
                    results = results.filter(a => new Date(a.timestamp) >= new Date(startDate));
                }
                
                if (endDate) {
                    results = results.filter(a => new Date(a.timestamp) <= new Date(endDate));
                }
                
                resolve(results);
            };

            request.onerror = () => reject(request.error);
        });
    }

    // Export/Import Data
    async exportUserData(userId) {
        const user = await this.getUser(userId);
        const sessions = await this.getSessions(userId);
        const progress = await this.getProgress(userId);
        const achievements = await this.getAchievements(userId);
        const analytics = await this.getAnalytics(userId);

        return {
            version: '2.0.0',
            exportDate: new Date().toISOString(),
            user: user,
            sessions: sessions,
            progress: progress,
            achievements: achievements,
            analytics: analytics
        };
    }

    async importUserData(data) {
        if (data.version !== '2.0.0') {
            throw new Error('Incompatible data version');
        }

        // Import user
        if (data.user) {
            await this.createUser(data.user);
        }

        // Import sessions
        if (data.sessions && Array.isArray(data.sessions)) {
            for (const session of data.sessions) {
                await this.createSession(session.userId);
            }
        }

        // Import progress
        if (data.progress && Array.isArray(data.progress)) {
            for (const progress of data.progress) {
                await this.saveProgress(progress.userId, progress.mode, progress);
            }
        }

        // Import achievements
        if (data.achievements && Array.isArray(data.achievements)) {
            for (const achievement of data.achievements) {
                await this.unlockAchievement(achievement.userId, achievement.achievementId, achievement);
            }
        }

        // Import analytics
        if (data.analytics && Array.isArray(data.analytics)) {
            for (const analytic of data.analytics) {
                await this.logAnalytics(analytic.userId, analytic.type, analytic.data);
            }
        }

        return true;
    }

    // Helper Methods
    generateId() {
        return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getLocalStorageArray(key) {
        const data = localStorage.getItem(`${this.storagePrefix}${key}`);
        return data ? JSON.parse(data) : [];
    }

    setLocalStorageArray(key, array) {
        localStorage.setItem(`${this.storagePrefix}${key}`, JSON.stringify(array));
    }

    async getSessions(userId) {
        if (this.useLocalStorage) {
            const sessions = this.getLocalStorageArray('sessions');
            return sessions.filter(s => s.userId === userId);
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['sessions'], 'readonly');
            const store = transaction.objectStore('sessions');
            const index = store.index('userId');
            const request = index.getAll(userId);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // Clear all data
    async clearAllData() {
        if (this.useLocalStorage) {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(this.storagePrefix)) {
                    localStorage.removeItem(key);
                }
            });
            return true;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(
                ['users', 'sessions', 'progress', 'achievements', 'analytics'],
                'readwrite'
            );

            transaction.objectStore('users').clear();
            transaction.objectStore('sessions').clear();
            transaction.objectStore('progress').clear();
            transaction.objectStore('achievements').clear();
            transaction.objectStore('analytics').clear();

            transaction.oncomplete = () => resolve(true);
            transaction.onerror = () => reject(transaction.error);
        });
    }
}

export default new DataManager();