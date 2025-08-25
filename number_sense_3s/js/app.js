// Main Application Controller
import ConfigManager from './config.js';
import DataManager from './dataManager.js';
import PedagogicalEngine from './pedagogicalEngine.js';
import GameEngine from './gameEngine.js';
import UIManager from './uiManager.js';
import SoundManager from './soundManager.js';
import AccessibilityManager from './accessibility.js';

class NumberSense3sApp {
    constructor() {
        this.config = ConfigManager;
        this.dataManager = DataManager;
        this.pedagogicalEngine = new PedagogicalEngine(DataManager, ConfigManager);
        this.gameEngine = null;
        this.uiManager = null;
        this.soundManager = null;
        this.accessibilityManager = null;
        this.currentUser = null;
        this.currentSession = null;
        this.isInitialized = false;
    }

    async initialize() {
        try {
            console.log('Initializing Number Sense 3s...');
            
            // Initialize managers
            this.uiManager = new UIManager(this);
            this.soundManager = new SoundManager(this.config);
            this.accessibilityManager = new AccessibilityManager();
            
            // Load user or create guest
            await this.loadUser();
            
            // Initialize game engine
            this.gameEngine = new GameEngine(this);
            
            // Setup UI
            await this.uiManager.initialize();
            
            // Setup accessibility
            this.accessibilityManager.initialize();
            
            // Start session
            await this.startSession();
            
            this.isInitialized = true;
            console.log('Application initialized successfully');
            
            // Show welcome screen
            this.uiManager.showWelcomeScreen();
            
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.handleError(error);
        }
    }

    async loadUser() {
        // Check for existing user in storage
        const storedUserId = localStorage.getItem('number_sense_3s_current_user');
        
        if (storedUserId) {
            this.currentUser = await this.dataManager.getUser(storedUserId);
            if (this.currentUser) {
                await this.pedagogicalEngine.initializeUser(storedUserId);
                console.log('Loaded existing user:', this.currentUser.username);
                return;
            }
        }
        
        // Create guest user
        await this.createGuestUser();
    }

    async createGuestUser() {
        const guestData = {
            username: `Guest_${Math.random().toString(36).substr(2, 9)}`,
            email: '',
            preferences: this.config.userPreferences
        };
        
        this.currentUser = await this.dataManager.createUser(guestData);
        localStorage.setItem('number_sense_3s_current_user', this.currentUser.id);
        await this.pedagogicalEngine.initializeUser(this.currentUser.id);
        console.log('Created guest user:', this.currentUser.username);
    }

    async createUser(userData) {
        // Validate user data
        if (!userData.username || userData.username.trim().length < 3) {
            throw new Error('Username must be at least 3 characters');
        }
        
        // Create user
        this.currentUser = await this.dataManager.createUser(userData);
        localStorage.setItem('number_sense_3s_current_user', this.currentUser.id);
        
        // Initialize pedagogical profile
        await this.pedagogicalEngine.initializeUser(this.currentUser.id);
        
        // Update UI
        this.uiManager.updateUserInfo(this.currentUser);
        
        return this.currentUser;
    }

    async switchUser(userId) {
        // Save current session
        if (this.currentSession) {
            await this.endSession();
        }
        
        // Load new user
        this.currentUser = await this.dataManager.getUser(userId);
        if (!this.currentUser) {
            throw new Error('User not found');
        }
        
        localStorage.setItem('number_sense_3s_current_user', userId);
        await this.pedagogicalEngine.initializeUser(userId);
        
        // Start new session
        await this.startSession();
        
        // Update UI
        this.uiManager.updateUserInfo(this.currentUser);
        
        return this.currentUser;
    }

    async startSession() {
        if (!this.currentUser) {
            throw new Error('No user loaded');
        }
        
        this.currentSession = await this.dataManager.createSession(this.currentUser.id);
        console.log('Started new session:', this.currentSession.id);
        
        // Log session start
        await this.dataManager.logAnalytics(this.currentUser.id, 'session', {
            action: 'start',
            timestamp: new Date().toISOString()
        });
        
        // Setup auto-save
        this.setupAutoSave();
        
        return this.currentSession;
    }

    async endSession() {
        if (!this.currentSession) return;
        
        const endTime = new Date().toISOString();
        const duration = new Date(endTime) - new Date(this.currentSession.startTime);
        
        // Update session
        await this.dataManager.updateSession(this.currentSession.id, {
            endTime: endTime,
            duration: duration,
            performance: this.gameEngine.getSessionPerformance()
        });
        
        // Log session end
        await this.dataManager.logAnalytics(this.currentUser.id, 'session', {
            action: 'end',
            duration: duration,
            timestamp: endTime
        });
        
        // Clear auto-save
        this.clearAutoSave();
        
        console.log('Ended session:', this.currentSession.id);
        this.currentSession = null;
    }

    setupAutoSave() {
        this.autoSaveInterval = setInterval(() => {
            this.saveProgress();
        }, this.config.config.storage.saveInterval);
    }

    clearAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
    }

    async saveProgress() {
        if (!this.currentUser || !this.currentSession) return;
        
        try {
            // Get current game state
            const gameState = this.gameEngine.getState();
            
            // Save progress
            await this.dataManager.saveProgress(
                this.currentUser.id,
                gameState.currentMode,
                gameState.progress
            );
            
            // Update session
            await this.dataManager.updateSession(this.currentSession.id, {
                questionsAttempted: gameState.totalQuestions,
                questionsCorrect: gameState.totalCorrect,
                score: gameState.score,
                modes: gameState.modesPlayed
            });
            
            // Update user stats
            await this.dataManager.updateUser(this.currentUser.id, {
                stats: {
                    ...this.currentUser.stats,
                    totalScore: gameState.score,
                    totalQuestions: gameState.totalQuestions,
                    totalCorrect: gameState.totalCorrect,
                    level: gameState.level
                }
            });
            
            console.log('Progress saved');
        } catch (error) {
            console.error('Failed to save progress:', error);
        }
    }

    async changeMode(mode) {
        if (!this.gameEngine) return;
        
        // Save current mode progress
        await this.saveProgress();
        
        // Log mode change
        await this.dataManager.logAnalytics(this.currentUser.id, 'mode_change', {
            from: this.gameEngine.currentMode,
            to: mode,
            timestamp: new Date().toISOString()
        });
        
        // Change mode
        this.gameEngine.switchMode(mode);
        
        // Update UI
        this.uiManager.updateMode(mode);
    }

    async handleAnswer(answer) {
        if (!this.gameEngine) return;
        
        // Process answer
        const result = await this.gameEngine.processAnswer(answer);
        
        // Log answer
        await this.dataManager.logAnalytics(this.currentUser.id, 'answer', {
            mode: this.gameEngine.currentMode,
            question: result.question,
            answer: answer,
            correct: result.correct,
            responseTime: result.responseTime,
            timestamp: new Date().toISOString()
        });
        
        // Handle mistakes for learning
        if (!result.correct) {
            const feedback = await this.pedagogicalEngine.recordMistake(
                result.question,
                answer,
                result.correctAnswer
            );
            result.feedback = feedback;
        }
        
        // Check achievements
        const newAchievements = await this.checkAchievements(result);
        if (newAchievements.length > 0) {
            result.achievements = newAchievements;
        }
        
        // Update UI with result
        this.uiManager.showResult(result);
        
        // Play sound
        if (this.config.config.userPreferences.soundEnabled) {
            this.soundManager.play(result.correct ? 'success' : 'error');
        }
        
        return result;
    }

    async checkAchievements(result) {
        const newAchievements = [];
        const userAchievements = await this.dataManager.getAchievements(this.currentUser.id);
        const unlockedIds = new Set(userAchievements.map(a => a.achievementId));
        
        for (const [id, achievement] of Object.entries(this.config.config.achievements)) {
            if (unlockedIds.has(id)) continue;
            
            const isUnlocked = await this.checkAchievementCriteria(achievement.criteria, result);
            
            if (isUnlocked) {
                await this.dataManager.unlockAchievement(this.currentUser.id, id, achievement);
                newAchievements.push({ id, ...achievement });
            }
        }
        
        return newAchievements;
    }

    async checkAchievementCriteria(criteria, result) {
        const gameState = this.gameEngine.getState();
        
        switch (criteria.type) {
            case 'single':
                return criteria.condition === 'first_correct' && result.correct;
                
            case 'streak':
                return gameState.streak >= criteria.count;
                
            case 'speed':
                return result.responseTime < criteria.time;
                
            case 'level':
                return gameState.level >= criteria.target;
                
            case 'accuracy':
                return gameState.accuracy >= criteria.threshold;
                
            case 'cumulative':
                return gameState.totalCorrect >= criteria.count;
                
            default:
                return false;
        }
    }

    async getHint() {
        if (!this.gameEngine || !this.gameEngine.currentQuestion) {
            return null;
        }
        
        const question = this.gameEngine.currentQuestion;
        const hints = this.pedagogicalEngine.hintGenerator.generateHints(
            question,
            this.pedagogicalEngine.learningProfile
        );
        
        // Log hint usage
        await this.dataManager.logAnalytics(this.currentUser.id, 'hint', {
            mode: this.gameEngine.currentMode,
            question: question,
            timestamp: new Date().toISOString()
        });
        
        // Show hint in UI
        this.uiManager.showHint(hints[this.gameEngine.hintsShown] || hints[0]);
        this.gameEngine.hintsShown++;
        
        return hints;
    }

    async exportData() {
        try {
            const data = await this.dataManager.exportUserData(this.currentUser.id);
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `number_sense_3s_${this.currentUser.username}_${new Date().toISOString()}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
            
            this.uiManager.showNotification('Data exported successfully', 'success');
        } catch (error) {
            console.error('Failed to export data:', error);
            this.uiManager.showNotification('Failed to export data', 'error');
        }
    }

    async importData(file) {
        try {
            const text = await file.text();
            const data = JSON.parse(text);
            
            await this.dataManager.importUserData(data);
            
            // Reload user
            if (data.user) {
                await this.switchUser(data.user.id);
            }
            
            this.uiManager.showNotification('Data imported successfully', 'success');
        } catch (error) {
            console.error('Failed to import data:', error);
            this.uiManager.showNotification('Failed to import data', 'error');
        }
    }

    async resetProgress() {
        if (!confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
            return;
        }
        
        try {
            await this.dataManager.clearAllData();
            await this.createGuestUser();
            await this.startSession();
            
            this.gameEngine.reset();
            this.uiManager.reset();
            
            this.uiManager.showNotification('Progress reset successfully', 'success');
        } catch (error) {
            console.error('Failed to reset progress:', error);
            this.uiManager.showNotification('Failed to reset progress', 'error');
        }
    }

    updateSettings(settings) {
        // Update config
        Object.assign(this.config.config.userPreferences, settings);
        this.config.saveUserPreferences();
        
        // Apply settings
        if (settings.soundEnabled !== undefined) {
            this.soundManager.setEnabled(settings.soundEnabled);
        }
        
        if (settings.animationsEnabled !== undefined) {
            this.uiManager.setAnimations(settings.animationsEnabled);
        }
        
        if (settings.theme !== undefined) {
            this.uiManager.setTheme(settings.theme);
        }
        
        if (settings.difficulty !== undefined) {
            this.config.setDifficulty(settings.difficulty);
            this.gameEngine.updateDifficulty();
        }
        
        // Update UI
        this.uiManager.updateSettings(settings);
    }

    handleError(error) {
        console.error('Application error:', error);
        
        // Log error
        if (this.currentUser) {
            this.dataManager.logAnalytics(this.currentUser.id, 'error', {
                message: error.message,
                stack: error.stack,
                timestamp: new Date().toISOString()
            });
        }
        
        // Show error to user
        this.uiManager.showError(error.message);
    }

    async cleanup() {
        try {
            // Save final progress
            await this.saveProgress();
            
            // End session
            await this.endSession();
            
            // Cleanup managers
            if (this.soundManager) this.soundManager.cleanup();
            if (this.uiManager) this.uiManager.cleanup();
            if (this.accessibilityManager) this.accessibilityManager.cleanup();
            
            console.log('Application cleaned up');
        } catch (error) {
            console.error('Cleanup error:', error);
        }
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.app = new NumberSense3sApp();
        window.app.initialize();
    });
} else {
    window.app = new NumberSense3sApp();
    window.app.initialize();
}

// Handle page unload
window.addEventListener('beforeunload', async (event) => {
    if (window.app && window.app.isInitialized) {
        await window.app.cleanup();
    }
});

// Handle visibility change for auto-pause
document.addEventListener('visibilitychange', () => {
    if (window.app && window.app.gameEngine) {
        if (document.hidden) {
            window.app.gameEngine.pause();
        } else {
            window.app.gameEngine.resume();
        }
    }
});

export default NumberSense3sApp;