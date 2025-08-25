// Configuration System for Number Sense 3s
export const Config = {
    // Difficulty Settings
    difficulty: {
        beginner: {
            name: 'Beginner',
            maxNumber: 30,
            timeLimit: null,
            hintsEnabled: true,
            visualAidsEnabled: true,
            questionsPerLevel: 5,
            levelUpThreshold: 0.6,
            modes: ['identify', 'multiply', 'patterns']
        },
        intermediate: {
            name: 'Intermediate',
            maxNumber: 100,
            timeLimit: 30000,
            hintsEnabled: true,
            visualAidsEnabled: false,
            questionsPerLevel: 10,
            levelUpThreshold: 0.7,
            modes: ['identify', 'multiply', 'patterns', 'skip-count', 'fractions']
        },
        advanced: {
            name: 'Advanced',
            maxNumber: 300,
            timeLimit: 15000,
            hintsEnabled: false,
            visualAidsEnabled: false,
            questionsPerLevel: 15,
            levelUpThreshold: 0.8,
            modes: ['identify', 'multiply', 'patterns', 'skip-count', 'factor-tree', 'divisibility-chain', 'fractions']
        },
        expert: {
            name: 'Expert',
            maxNumber: 999,
            timeLimit: 10000,
            hintsEnabled: false,
            visualAidsEnabled: false,
            questionsPerLevel: 20,
            levelUpThreshold: 0.9,
            modes: ['all']
        }
    },

    // Scoring System
    scoring: {
        basePoints: 10,
        levelMultiplier: 1.5,
        streakBonus: 5,
        speedBonus: {
            fast: { time: 2000, bonus: 20 },
            medium: { time: 5000, bonus: 10 },
            slow: { time: 10000, bonus: 5 }
        },
        perfectRoundBonus: 50,
        achievementPoints: 100
    },

    // Pedagogical Features
    pedagogy: {
        adaptiveDifficulty: true,
        personalizedHints: true,
        mistakeAnalysis: true,
        progressTracking: true,
        spaceRepetition: true,
        masteryThreshold: 0.85,
        reviewInterval: 7,
        conceptMastery: {
            'divisibility': 0,
            'multiplication': 0,
            'patterns': 0,
            'factorization': 0,
            'fractions': 0
        }
    },

    // Visual Settings
    visuals: {
        animations: true,
        sounds: true,
        hapticFeedback: true,
        colorBlindMode: false,
        highContrast: false,
        fontSize: 'medium',
        theme: 'light'
    },

    // Game Modes Configuration
    modes: {
        identify: {
            name: 'Identify Multiples',
            description: 'Determine if numbers are multiples of 3',
            icon: '🎯',
            concepts: ['divisibility'],
            pedagogicalGoals: ['recognition', 'mental-math'],
            variations: [
                { type: 'classic', name: 'Classic Mode' },
                { type: 'timed', name: 'Speed Challenge' },
                { type: 'endless', name: 'Endless Practice' }
            ]
        },
        multiply: {
            name: 'Multiplication',
            description: 'Practice multiplication by 3',
            icon: '✖️',
            concepts: ['multiplication'],
            pedagogicalGoals: ['calculation', 'memorization'],
            variations: [
                { type: 'forward', name: '3 × n' },
                { type: 'reverse', name: 'n × 3' },
                { type: 'missing', name: 'Find Missing Factor' }
            ]
        },
        patterns: {
            name: 'Pattern Recognition',
            description: 'Complete number patterns involving 3',
            icon: '🔢',
            concepts: ['patterns', 'sequences'],
            pedagogicalGoals: ['pattern-recognition', 'logical-thinking'],
            variations: [
                { type: 'arithmetic', name: 'Arithmetic Sequences' },
                { type: 'geometric', name: 'Geometric Sequences' },
                { type: 'complex', name: 'Complex Patterns' }
            ]
        },
        'skip-count': {
            name: 'Skip Counting',
            description: 'Count by 3s in sequence',
            icon: '🏃',
            concepts: ['counting', 'sequences'],
            pedagogicalGoals: ['sequential-thinking', 'number-sense'],
            variations: [
                { type: 'forward', name: 'Count Up' },
                { type: 'backward', name: 'Count Down' },
                { type: 'grid', name: 'Grid Selection' }
            ]
        },
        'factor-tree': {
            name: 'Factor Trees',
            description: 'Build factor trees for multiples of 3',
            icon: '🌳',
            concepts: ['factorization', 'prime-factors'],
            pedagogicalGoals: ['decomposition', 'structural-thinking'],
            variations: [
                { type: 'guided', name: 'Guided Factoring' },
                { type: 'free', name: 'Free Build' },
                { type: 'reverse', name: 'Rebuild from Factors' }
            ]
        },
        'divisibility-chain': {
            name: 'Divisibility Chain',
            description: 'Follow chains of division by 3',
            icon: '⛓️',
            concepts: ['division', 'sequences'],
            pedagogicalGoals: ['division-fluency', 'chain-reasoning'],
            variations: [
                { type: 'forward', name: 'Division Chain' },
                { type: 'reverse', name: 'Multiplication Chain' },
                { type: 'mixed', name: 'Mixed Operations' }
            ]
        },
        fractions: {
            name: 'Fractions & 3s',
            description: 'Work with fractions involving 3',
            icon: '🥧',
            concepts: ['fractions', 'reduction'],
            pedagogicalGoals: ['fraction-sense', 'simplification'],
            variations: [
                { type: 'reduce', name: 'Simplify Fractions' },
                { type: 'compare', name: 'Compare Fractions' },
                { type: 'operations', name: 'Fraction Operations' }
            ]
        }
    },

    // Achievement System
    achievements: {
        'first-success': {
            name: 'First Success',
            description: 'Get your first answer correct',
            icon: '🎯',
            points: 10,
            criteria: { type: 'single', condition: 'first_correct' }
        },
        'streak-master': {
            name: 'Streak Master',
            description: 'Get 10 answers correct in a row',
            icon: '🔥',
            points: 50,
            criteria: { type: 'streak', count: 10 }
        },
        'speed-demon': {
            name: 'Speed Demon',
            description: 'Answer 5 questions in under 2 seconds each',
            icon: '⚡',
            points: 75,
            criteria: { type: 'speed', time: 2000, count: 5 }
        },
        'level-climber': {
            name: 'Level Climber',
            description: 'Reach level 5',
            icon: '📈',
            points: 100,
            criteria: { type: 'level', target: 5 }
        },
        'perfectionist': {
            name: 'Perfectionist',
            description: 'Complete a round with 100% accuracy',
            icon: '💯',
            points: 150,
            criteria: { type: 'accuracy', threshold: 1.0 }
        },
        'mode-master': {
            name: 'Mode Master',
            description: 'Master all game modes',
            icon: '🏆',
            points: 500,
            criteria: { type: 'mastery', modes: 'all' }
        },
        'daily-dedication': {
            name: 'Daily Dedication',
            description: 'Practice for 7 consecutive days',
            icon: '📅',
            points: 200,
            criteria: { type: 'consistency', days: 7 }
        },
        'problem-solver': {
            name: 'Problem Solver',
            description: 'Solve 100 problems correctly',
            icon: '🧩',
            points: 250,
            criteria: { type: 'cumulative', count: 100 }
        }
    },

    // Hint System
    hints: {
        identify: [
            'Add up all the digits in the number',
            'If the sum is divisible by 3, so is the number',
            'Look for patterns in the digits',
            'Try dividing mentally by 3'
        ],
        multiply: [
            'Remember: 3 × 10 = 30',
            'Break down larger numbers: 3 × 12 = 3 × 10 + 3 × 2',
            'Use doubling: 3 × 4 = 6 × 2',
            'Count by 3s to reach the answer'
        ],
        patterns: [
            'Look at the difference between consecutive numbers',
            'Check if the pattern increases by 3 each time',
            'Consider if there might be a multiplication pattern',
            'Sometimes patterns skip numbers'
        ],
        general: [
            'Take your time to think',
            'Use the visual aids if available',
            'Practice makes perfect',
            'Look for shortcuts and tricks'
        ]
    },

    // Feedback Messages
    feedback: {
        correct: [
            'Excellent!',
            'Perfect!',
            'Great job!',
            'Fantastic!',
            'You got it!',
            'Brilliant!',
            'Outstanding!',
            'Superb!',
            'Well done!',
            'Awesome!'
        ],
        incorrect: [
            'Not quite, try again!',
            'Keep trying!',
            'Almost there!',
            'Give it another shot!',
            'You can do this!',
            'Don\'t give up!',
            'Keep practicing!',
            'That\'s okay, learn from it!'
        ],
        encouragement: [
            'You\'re improving!',
            'Great progress!',
            'Keep up the good work!',
            'You\'re getting better!',
            'Nice effort!',
            'You\'re on the right track!'
        ]
    },

    // User Preferences (can be saved/loaded)
    userPreferences: {
        difficulty: 'intermediate',
        soundEnabled: true,
        animationsEnabled: true,
        autoAdvance: true,
        showTimer: true,
        showHints: true,
        preferredModes: [],
        colorScheme: 'auto'
    },

    // API/Storage Settings
    storage: {
        type: 'localStorage',
        prefix: 'number_sense_3s_',
        autoSave: true,
        saveInterval: 30000,
        dataVersion: '2.0.0'
    },

    // Performance Tracking
    analytics: {
        trackProgress: true,
        trackMistakes: true,
        trackTime: true,
        trackPatterns: true,
        sessionTracking: true,
        errorLogging: true
    }
};

// Configuration Manager
export class ConfigManager {
    constructor() {
        this.config = { ...Config };
        this.loadUserPreferences();
    }

    loadUserPreferences() {
        const stored = localStorage.getItem(`${Config.storage.prefix}preferences`);
        if (stored) {
            try {
                const preferences = JSON.parse(stored);
                this.config.userPreferences = { ...this.config.userPreferences, ...preferences };
            } catch (e) {
                console.error('Failed to load preferences:', e);
            }
        }
    }

    saveUserPreferences() {
        try {
            localStorage.setItem(
                `${Config.storage.prefix}preferences`,
                JSON.stringify(this.config.userPreferences)
            );
        } catch (e) {
            console.error('Failed to save preferences:', e);
        }
    }

    getDifficulty() {
        return this.config.difficulty[this.config.userPreferences.difficulty];
    }

    setDifficulty(level) {
        if (this.config.difficulty[level]) {
            this.config.userPreferences.difficulty = level;
            this.saveUserPreferences();
            return true;
        }
        return false;
    }

    getMode(modeName) {
        return this.config.modes[modeName];
    }

    getAchievement(achievementId) {
        return this.config.achievements[achievementId];
    }

    getHints(mode) {
        return this.config.hints[mode] || this.config.hints.general;
    }

    getRandomFeedback(type) {
        const messages = this.config.feedback[type];
        return messages[Math.floor(Math.random() * messages.length)];
    }

    updateConceptMastery(concept, score) {
        if (this.config.pedagogy.conceptMastery.hasOwnProperty(concept)) {
            const current = this.config.pedagogy.conceptMastery[concept];
            this.config.pedagogy.conceptMastery[concept] = 
                current * 0.7 + score * 0.3; // Weighted average
        }
    }

    shouldShowHint(concept) {
        if (!this.config.userPreferences.showHints) return false;
        const mastery = this.config.pedagogy.conceptMastery[concept] || 0;
        return mastery < this.config.pedagogy.masteryThreshold;
    }

    export() {
        return JSON.stringify(this.config, null, 2);
    }

    import(configString) {
        try {
            const imported = JSON.parse(configString);
            this.config = { ...this.config, ...imported };
            this.saveUserPreferences();
            return true;
        } catch (e) {
            console.error('Failed to import config:', e);
            return false;
        }
    }
}

export default new ConfigManager();