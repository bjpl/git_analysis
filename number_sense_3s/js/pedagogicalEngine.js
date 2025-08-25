// Pedagogical Engine for Adaptive Learning
export class PedagogicalEngine {
    constructor(dataManager, configManager) {
        this.dataManager = dataManager;
        this.configManager = configManager;
        this.currentUser = null;
        this.learningProfile = null;
        this.mistakePatterns = new Map();
        this.conceptGraph = this.initializeConceptGraph();
        this.difficultyAdjuster = new DifficultyAdjuster();
        this.hintGenerator = new HintGenerator();
        this.feedbackEngine = new FeedbackEngine();
    }

    initializeConceptGraph() {
        return {
            'basic-counting': {
                prerequisites: [],
                skills: ['number-recognition', 'sequence'],
                difficulty: 1
            },
            'divisibility': {
                prerequisites: ['basic-counting'],
                skills: ['mental-math', 'pattern-recognition'],
                difficulty: 2
            },
            'multiplication': {
                prerequisites: ['basic-counting'],
                skills: ['calculation', 'memorization'],
                difficulty: 2
            },
            'patterns': {
                prerequisites: ['basic-counting', 'multiplication'],
                skills: ['logical-thinking', 'sequence-analysis'],
                difficulty: 3
            },
            'factorization': {
                prerequisites: ['multiplication', 'divisibility'],
                skills: ['decomposition', 'prime-recognition'],
                difficulty: 4
            },
            'fractions': {
                prerequisites: ['multiplication', 'divisibility'],
                skills: ['reduction', 'equivalence'],
                difficulty: 4
            },
            'advanced-patterns': {
                prerequisites: ['patterns', 'factorization'],
                skills: ['complex-reasoning', 'multi-step-thinking'],
                difficulty: 5
            }
        };
    }

    async initializeUser(userId) {
        this.currentUser = userId;
        this.learningProfile = await this.buildLearningProfile(userId);
        return this.learningProfile;
    }

    async buildLearningProfile(userId) {
        const progress = await this.dataManager.getProgress(userId);
        const analytics = await this.dataManager.getAnalytics(userId, 'learning');
        
        const profile = {
            userId: userId,
            skillLevels: {},
            conceptMastery: {},
            learningStyle: this.detectLearningStyle(analytics),
            strengths: [],
            weaknesses: [],
            recommendedConcepts: [],
            adaptiveParameters: {
                responseTimeAverage: 0,
                accuracyTrend: 0,
                engagementLevel: 0,
                frustrationIndex: 0,
                masteryVelocity: 0
            }
        };

        // Analyze progress data
        for (const concept in this.conceptGraph) {
            profile.conceptMastery[concept] = this.calculateConceptMastery(progress, concept);
            
            for (const skill of this.conceptGraph[concept].skills) {
                if (!profile.skillLevels[skill]) {
                    profile.skillLevels[skill] = 0;
                }
                profile.skillLevels[skill] += profile.conceptMastery[concept] * 0.2;
            }
        }

        // Identify strengths and weaknesses
        profile.strengths = this.identifyStrengths(profile.conceptMastery);
        profile.weaknesses = this.identifyWeaknesses(profile.conceptMastery);
        
        // Generate recommendations
        profile.recommendedConcepts = this.generateRecommendations(profile);

        // Calculate adaptive parameters
        profile.adaptiveParameters = this.calculateAdaptiveParameters(progress, analytics);

        return profile;
    }

    detectLearningStyle(analytics) {
        const patterns = {
            visual: 0,
            sequential: 0,
            global: 0,
            active: 0,
            reflective: 0
        };

        analytics.forEach(entry => {
            if (entry.data.usedVisualAids) patterns.visual++;
            if (entry.data.followedSequence) patterns.sequential++;
            if (entry.data.jumpedAround) patterns.global++;
            if (entry.data.immediateAttempt) patterns.active++;
            if (entry.data.thoughtTime > 5000) patterns.reflective++;
        });

        // Determine dominant style
        const dominant = Object.keys(patterns).reduce((a, b) => 
            patterns[a] > patterns[b] ? a : b
        );

        return {
            dominant: dominant,
            scores: patterns,
            preferences: this.getLearningPreferences(dominant)
        };
    }

    getLearningPreferences(style) {
        const preferences = {
            visual: {
                showDiagrams: true,
                useColors: true,
                animatedFeedback: true,
                dotRepresentation: true
            },
            sequential: {
                structuredLessons: true,
                stepByStep: true,
                clearProgression: true,
                linearPath: true
            },
            global: {
                overviewFirst: true,
                connections: true,
                bigPicture: true,
                flexibility: true
            },
            active: {
                immediateApplication: true,
                trialAndError: true,
                quickFeedback: true,
                handsonPractice: true
            },
            reflective: {
                thinkingTime: true,
                detailedExplanations: true,
                conceptualUnderstanding: true,
                selfPaced: true
            }
        };

        return preferences[style] || preferences.sequential;
    }

    calculateConceptMastery(progress, concept) {
        const relevantProgress = progress.filter(p => 
            p.concepts && p.concepts.includes(concept)
        );

        if (relevantProgress.length === 0) return 0;

        let mastery = 0;
        let weightSum = 0;

        relevantProgress.forEach((entry, index) => {
            const recency = Math.exp(-index * 0.1); // More recent = higher weight
            const accuracy = entry.questionsCorrect / entry.questionsAttempted || 0;
            const speed = Math.min(1, 5000 / entry.averageResponseTime); // Faster = better
            
            const score = accuracy * 0.7 + speed * 0.3;
            mastery += score * recency;
            weightSum += recency;
        });

        return weightSum > 0 ? mastery / weightSum : 0;
    }

    identifyStrengths(conceptMastery) {
        return Object.entries(conceptMastery)
            .filter(([_, mastery]) => mastery >= 0.8)
            .map(([concept, _]) => concept);
    }

    identifyWeaknesses(conceptMastery) {
        return Object.entries(conceptMastery)
            .filter(([_, mastery]) => mastery < 0.5)
            .map(([concept, _]) => concept);
    }

    generateRecommendations(profile) {
        const recommendations = [];
        
        // Find concepts where prerequisites are met but mastery is low
        for (const [concept, data] of Object.entries(this.conceptGraph)) {
            const prerequisitesMet = data.prerequisites.every(prereq => 
                profile.conceptMastery[prereq] >= 0.7
            );
            
            const currentMastery = profile.conceptMastery[concept] || 0;
            
            if (prerequisitesMet && currentMastery < 0.8) {
                recommendations.push({
                    concept: concept,
                    priority: this.calculatePriority(concept, profile),
                    reason: this.getRecommendationReason(concept, profile)
                });
            }
        }

        // Sort by priority
        recommendations.sort((a, b) => b.priority - a.priority);
        
        return recommendations.slice(0, 3); // Top 3 recommendations
    }

    calculatePriority(concept, profile) {
        let priority = 0;
        
        // Base priority on difficulty gap
        const difficulty = this.conceptGraph[concept].difficulty;
        const userLevel = this.calculateUserLevel(profile);
        priority += Math.max(0, 5 - Math.abs(difficulty - userLevel));
        
        // Boost if it unlocks other concepts
        const unlocksCount = Object.values(this.conceptGraph)
            .filter(c => c.prerequisites.includes(concept)).length;
        priority += unlocksCount * 2;
        
        // Consider learning velocity
        priority += profile.adaptiveParameters.masteryVelocity;
        
        return priority;
    }

    calculateUserLevel(profile) {
        const masteryValues = Object.values(profile.conceptMastery);
        if (masteryValues.length === 0) return 1;
        
        const averageMastery = masteryValues.reduce((a, b) => a + b, 0) / masteryValues.length;
        return Math.floor(averageMastery * 5) + 1; // Level 1-5
    }

    getRecommendationReason(concept, profile) {
        const reasons = [];
        
        if (profile.weaknesses.includes(concept)) {
            reasons.push('Strengthen this weak area');
        }
        
        const unlocksCount = Object.values(this.conceptGraph)
            .filter(c => c.prerequisites.includes(concept)).length;
        if (unlocksCount > 0) {
            reasons.push(`Unlocks ${unlocksCount} new concepts`);
        }
        
        if (profile.conceptMastery[concept] > 0.5 && profile.conceptMastery[concept] < 0.8) {
            reasons.push('Almost mastered - finish strong!');
        }
        
        return reasons.join('. ') || 'Recommended for your learning path';
    }

    calculateAdaptiveParameters(progress, analytics) {
        const recentProgress = progress.slice(-20); // Last 20 entries
        
        const params = {
            responseTimeAverage: 0,
            accuracyTrend: 0,
            engagementLevel: 0,
            frustrationIndex: 0,
            masteryVelocity: 0
        };

        if (recentProgress.length === 0) return params;

        // Response time average
        params.responseTimeAverage = recentProgress.reduce((sum, p) => 
            sum + p.averageResponseTime, 0) / recentProgress.length;

        // Accuracy trend (positive = improving, negative = declining)
        if (recentProgress.length >= 2) {
            const firstHalf = recentProgress.slice(0, Math.floor(recentProgress.length / 2));
            const secondHalf = recentProgress.slice(Math.floor(recentProgress.length / 2));
            
            const firstAccuracy = this.averageAccuracy(firstHalf);
            const secondAccuracy = this.averageAccuracy(secondHalf);
            
            params.accuracyTrend = secondAccuracy - firstAccuracy;
        }

        // Engagement level (based on session frequency and duration)
        const recentAnalytics = analytics.slice(-50);
        const sessionDurations = recentAnalytics
            .filter(a => a.type === 'session')
            .map(a => a.data.duration);
        
        if (sessionDurations.length > 0) {
            const avgDuration = sessionDurations.reduce((a, b) => a + b, 0) / sessionDurations.length;
            params.engagementLevel = Math.min(1, avgDuration / 600000); // 10 minutes = full engagement
        }

        // Frustration index (based on repeated mistakes and quit patterns)
        const mistakes = recentAnalytics.filter(a => a.type === 'mistake');
        const quits = recentAnalytics.filter(a => a.type === 'quit');
        
        params.frustrationIndex = (mistakes.length * 0.3 + quits.length * 0.7) / 
                                 Math.max(1, recentAnalytics.length);

        // Mastery velocity (how quickly concepts are being mastered)
        const masteryEvents = recentAnalytics.filter(a => 
            a.type === 'mastery' && a.data.level >= 0.8
        );
        params.masteryVelocity = masteryEvents.length / Math.max(1, recentProgress.length);

        return params;
    }

    averageAccuracy(progressArray) {
        if (progressArray.length === 0) return 0;
        
        const total = progressArray.reduce((sum, p) => 
            sum + (p.questionsCorrect / p.questionsAttempted || 0), 0
        );
        
        return total / progressArray.length;
    }

    async recordMistake(questionData, userAnswer, correctAnswer) {
        const mistake = {
            timestamp: new Date().toISOString(),
            question: questionData,
            userAnswer: userAnswer,
            correctAnswer: correctAnswer,
            concept: questionData.concept,
            difficulty: questionData.difficulty
        };

        // Update mistake patterns
        const pattern = this.identifyMistakePattern(mistake);
        if (!this.mistakePatterns.has(pattern)) {
            this.mistakePatterns.set(pattern, []);
        }
        this.mistakePatterns.get(pattern).push(mistake);

        // Log to analytics
        await this.dataManager.logAnalytics(this.currentUser, 'mistake', mistake);

        // Generate targeted feedback
        return this.feedbackEngine.generateMistakeFeedback(mistake, pattern);
    }

    identifyMistakePattern(mistake) {
        // Analyze the type of mistake
        if (mistake.concept === 'divisibility') {
            if (mistake.userAnswer === !mistake.correctAnswer) {
                return 'divisibility-confusion';
            }
        }
        
        if (mistake.concept === 'multiplication') {
            const diff = Math.abs(mistake.userAnswer - mistake.correctAnswer);
            if (diff === 3) return 'off-by-one-multiple';
            if (diff % 3 === 0) return 'multiple-confusion';
        }
        
        if (mistake.concept === 'patterns') {
            if (mistake.userAnswer === mistake.correctAnswer + 3) {
                return 'pattern-overshoot';
            }
            if (mistake.userAnswer === mistake.correctAnswer - 3) {
                return 'pattern-undershoot';
            }
        }
        
        return 'general-mistake';
    }

    async generateAdaptiveQuestion() {
        if (!this.learningProfile) return null;

        // Determine appropriate difficulty
        const targetDifficulty = this.difficultyAdjuster.getTargetDifficulty(
            this.learningProfile.adaptiveParameters
        );

        // Select concept based on recommendations
        const concept = this.selectNextConcept();

        // Generate question
        const question = await this.generateQuestion(concept, targetDifficulty);

        // Add pedagogical metadata
        question.hints = this.hintGenerator.generateHints(question, this.learningProfile);
        question.scaffolding = this.getScaffolding(concept, this.learningProfile);

        return question;
    }

    selectNextConcept() {
        if (this.learningProfile.recommendedConcepts.length > 0) {
            // Use spaced repetition algorithm
            const weights = this.learningProfile.recommendedConcepts.map((rec, index) => 
                rec.priority * Math.exp(-index * 0.3)
            );
            
            const totalWeight = weights.reduce((a, b) => a + b, 0);
            let random = Math.random() * totalWeight;
            
            for (let i = 0; i < weights.length; i++) {
                random -= weights[i];
                if (random <= 0) {
                    return this.learningProfile.recommendedConcepts[i].concept;
                }
            }
        }
        
        // Fallback to random concept user has some mastery in
        const availableConcepts = Object.entries(this.learningProfile.conceptMastery)
            .filter(([_, mastery]) => mastery > 0.2 && mastery < 0.9)
            .map(([concept, _]) => concept);
        
        return availableConcepts[Math.floor(Math.random() * availableConcepts.length)] || 'basic-counting';
    }

    async generateQuestion(concept, difficulty) {
        // This would integrate with your question generation logic
        // For now, returning a template
        return {
            concept: concept,
            difficulty: difficulty,
            type: this.getQuestionType(concept),
            content: await this.createQuestionContent(concept, difficulty),
            correctAnswer: null, // To be filled by game logic
            metadata: {
                generatedAt: new Date().toISOString(),
                adaptiveLevel: difficulty,
                concept: concept
            }
        };
    }

    getQuestionType(concept) {
        const typeMap = {
            'basic-counting': 'skip-count',
            'divisibility': 'identify',
            'multiplication': 'multiply',
            'patterns': 'patterns',
            'factorization': 'factor-tree',
            'fractions': 'fractions',
            'advanced-patterns': 'patterns'
        };
        
        return typeMap[concept] || 'identify';
    }

    async createQuestionContent(concept, difficulty) {
        // Generate appropriate numbers based on concept and difficulty
        const range = Math.floor(30 * difficulty);
        const complexity = Math.floor(difficulty / 2) + 1;
        
        return {
            range: range,
            complexity: complexity,
            visualAids: this.learningProfile.learningStyle.dominant === 'visual'
        };
    }

    getScaffolding(concept, profile) {
        const scaffolding = {
            level: 'none',
            elements: []
        };

        const mastery = profile.conceptMastery[concept] || 0;
        
        if (mastery < 0.3) {
            scaffolding.level = 'high';
            scaffolding.elements = ['step-by-step', 'visual-aids', 'worked-example'];
        } else if (mastery < 0.6) {
            scaffolding.level = 'medium';
            scaffolding.elements = ['hints-available', 'partial-solution'];
        } else if (mastery < 0.8) {
            scaffolding.level = 'low';
            scaffolding.elements = ['hints-on-request'];
        }

        return scaffolding;
    }
}

// Difficulty Adjuster
class DifficultyAdjuster {
    getTargetDifficulty(adaptiveParams) {
        let baseDifficulty = 3; // Medium difficulty
        
        // Adjust based on accuracy trend
        if (adaptiveParams.accuracyTrend > 0.1) {
            baseDifficulty += 0.5;
        } else if (adaptiveParams.accuracyTrend < -0.1) {
            baseDifficulty -= 0.5;
        }
        
        // Adjust based on frustration
        if (adaptiveParams.frustrationIndex > 0.3) {
            baseDifficulty -= 1;
        }
        
        // Adjust based on engagement
        if (adaptiveParams.engagementLevel > 0.7) {
            baseDifficulty += 0.3;
        }
        
        // Adjust based on mastery velocity
        baseDifficulty += adaptiveParams.masteryVelocity * 2;
        
        // Clamp between 1 and 5
        return Math.max(1, Math.min(5, baseDifficulty));
    }
}

// Hint Generator
class HintGenerator {
    generateHints(question, profile) {
        const hints = [];
        const maxHints = profile.learningStyle.dominant === 'reflective' ? 4 : 3;
        
        // Generate concept-specific hints
        switch (question.concept) {
            case 'divisibility':
                hints.push('Remember: Add all the digits together');
                hints.push('If the sum is divisible by 3, so is the number');
                hints.push(`For ${question.content.number}: ${this.showDigitSum(question.content.number)}`);
                break;
                
            case 'multiplication':
                hints.push('Think of skip counting by 3s');
                hints.push('Break it down: 3 × 10 = 30');
                hints.push('Use what you know about smaller multiples');
                break;
                
            case 'patterns':
                hints.push('Look at the difference between numbers');
                hints.push('Is it always the same difference?');
                hints.push('Try adding 3 to the last number');
                break;
                
            default:
                hints.push('Take your time and think carefully');
                hints.push('Look for patterns in the numbers');
                hints.push('Use what you\'ve learned before');
        }
        
        return hints.slice(0, maxHints);
    }
    
    showDigitSum(number) {
        const digits = number.toString().split('');
        const sum = digits.reduce((a, b) => parseInt(a) + parseInt(b), 0);
        return `${digits.join(' + ')} = ${sum}`;
    }
}

// Feedback Engine
class FeedbackEngine {
    generateMistakeFeedback(mistake, pattern) {
        const feedback = {
            message: '',
            explanation: '',
            suggestion: '',
            relatedConcept: ''
        };
        
        switch (pattern) {
            case 'divisibility-confusion':
                feedback.message = 'Not quite! Let\'s review divisibility by 3.';
                feedback.explanation = `${mistake.question.number} ${mistake.correctAnswer ? 'is' : 'is not'} divisible by 3.`;
                feedback.suggestion = 'Try adding up the digits and checking if that sum is divisible by 3.';
                feedback.relatedConcept = 'divisibility';
                break;
                
            case 'off-by-one-multiple':
                feedback.message = 'So close! You\'re off by one multiple of 3.';
                feedback.explanation = `The correct answer is ${mistake.correctAnswer}.`;
                feedback.suggestion = 'Double-check your multiplication or try skip counting.';
                feedback.relatedConcept = 'multiplication';
                break;
                
            case 'pattern-overshoot':
                feedback.message = 'You went a bit too far in the pattern!';
                feedback.explanation = `The pattern increases by 3, but you added 6.`;
                feedback.suggestion = 'Look at the consistent difference between consecutive numbers.';
                feedback.relatedConcept = 'patterns';
                break;
                
            default:
                feedback.message = 'Not quite right, but keep trying!';
                feedback.explanation = `The correct answer is ${mistake.correctAnswer}.`;
                feedback.suggestion = 'Review the concept and try a similar problem.';
                feedback.relatedConcept = mistake.concept;
        }
        
        return feedback;
    }
    
    generateSuccessFeedback(question, responseTime, streak) {
        const messages = [];
        
        if (responseTime < 2000) {
            messages.push('Lightning fast! ⚡');
        } else if (responseTime < 5000) {
            messages.push('Quick thinking! 🎯');
        }
        
        if (streak >= 5) {
            messages.push(`${streak} in a row! You're on fire! 🔥`);
        } else if (streak >= 3) {
            messages.push('Great streak going! Keep it up!');
        }
        
        if (question.difficulty >= 4) {
            messages.push('You mastered a challenging problem!');
        }
        
        return messages.join(' ') || 'Correct! Well done!';
    }
}

export default PedagogicalEngine;