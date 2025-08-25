class NumberSenseGame {
    constructor() {
        this.score = 0;
        this.streak = 0;
        this.level = 1;
        this.currentMode = 'identify';
        this.currentNumber = 0;
        this.currentAnswer = null;
        this.skipCountSequence = [];
        this.skipCountIndex = 0;
        this.questionsInLevel = 0;
        this.correctInLevel = 0;
        this.maxQuestionsPerLevel = 10;
        this.responseStartTime = 0;
        this.averageResponseTime = 0;
        this.responseHistory = [];
        this.factorTreeState = { target: 0, activeNode: null, tree: [] };
        this.chainState = { start: 0, steps: [], answers: [] };
        this.totalQuestions = 0;
        this.totalCorrect = 0;
        this.achievements = new Set();
        this.factorTreesCompleted = 0;
        this.perfectStreak = 0;
        this.fractionState = { numerator: 0, denominator: 0, isReducible: false };

        this.initializeElements();
        this.bindEvents();
        this.startGame();
    }

    initializeElements() {
        this.scoreElement = document.getElementById('score');
        this.streakElement = document.getElementById('streak');
        this.levelElement = document.getElementById('level');
        this.currentNumberElement = document.getElementById('current-number');
        this.numberBreakdownElement = document.getElementById('number-breakdown');
        this.feedbackPanel = document.getElementById('feedback-panel');
        this.feedbackIcon = document.getElementById('feedback-icon');
        this.feedbackText = document.getElementById('feedback-text');
        this.feedbackExplanation = document.getElementById('feedback-explanation');
        this.progressFill = document.getElementById('progress-fill');
        this.equationElement = document.getElementById('equation');
        this.multiplyInput = document.getElementById('multiply-input');
        this.patternSequence = document.getElementById('pattern-sequence');
        this.patternInput = document.getElementById('pattern-input');
        this.numberGrid = document.getElementById('number-grid');
        this.tipsContent = document.getElementById('tips-content');
        this.factorTarget = document.getElementById('factor-target');
        this.factorTreeContainer = document.getElementById('factor-tree-container');
        this.factorOptions = document.getElementById('factor-options');
        this.chainStart = document.getElementById('chain-start');
        this.chainInputs = document.querySelectorAll('.chain-input');
        this.chainExplanation = document.getElementById('chain-explanation');
        this.accuracyElement = document.getElementById('accuracy');
        this.fractionNumerator = document.getElementById('fraction-numerator');
        this.fractionDenominator = document.getElementById('fraction-denominator');
        this.fractionVisual = document.getElementById('fraction-visual');
        this.fractionExplanation = document.getElementById('fraction-explanation');
        this.currentActiveInput = null;
        this.numberPads = document.querySelectorAll('.number-pad');
    }

    bindEvents() {
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchMode(e.target.dataset.mode));
        });

        document.querySelectorAll('.answer-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleIdentifyAnswer(e.target.dataset.answer));
        });

        document.getElementById('submit-multiply').addEventListener('click', () => this.handleMultiplyAnswer());
        document.getElementById('multiply-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleMultiplyAnswer();
        });

        document.getElementById('submit-pattern').addEventListener('click', () => this.handlePatternAnswer());
        document.getElementById('pattern-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handlePatternAnswer();
        });

        document.getElementById('reset-grid').addEventListener('click', () => this.resetSkipCount());
        document.getElementById('reset-tree').addEventListener('click', () => this.resetFactorTree());
        document.getElementById('submit-chain').addEventListener('click', () => this.handleChainAnswer());

        document.getElementById('help-btn').addEventListener('click', () => this.toggleTips());
        
        document.addEventListener('keydown', (e) => this.handleKeyboardNavigation(e));
        
        this.setupNumberPads();
        this.setupInputValidation();
        this.setupDragAndDrop();
    }

    switchMode(mode) {
        this.currentMode = mode;
        
        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
        
        document.querySelectorAll('.game-mode').forEach(modeEl => modeEl.classList.add('hidden'));
        document.getElementById(`${mode}-mode`).classList.remove('hidden');
        
        this.hideFeedback();
        this.startMode();
    }

    startMode() {
        switch(this.currentMode) {
            case 'identify':
                this.generateIdentifyQuestion();
                break;
            case 'multiply':
                this.generateMultiplyQuestion();
                break;
            case 'patterns':
                this.generatePatternQuestion();
                break;
            case 'skip-count':
                this.initializeSkipCount();
                break;
            case 'factor-tree':
                this.initializeFactorTree();
                break;
            case 'divisibility-chain':
                this.initializeDivisibilityChain();
                break;
            case 'fractions':
                this.initializeFractions();
                break;
        }
    }

    startGame() {
        this.updateStats();
        this.generateIdentifyQuestion();
    }

    generateIdentifyQuestion() {
        this.responseStartTime = Date.now();
        const range = Math.min(30 + (this.level - 1) * 20, 200);
        this.currentNumber = Math.floor(Math.random() * range) + 1;
        
        this.addVisualRepresentation(this.currentNumber);
        this.currentNumberElement.textContent = this.currentNumber;
        
        const digitSum = this.calculateDigitSum(this.currentNumber);
        this.numberBreakdownElement.textContent = `Sum of digits: ${digitSum}`;
        
        this.currentAnswer = this.currentNumber % 3 === 0;
    }

    calculateDigitSum(num) {
        return num.toString().split('').reduce((sum, digit) => sum + parseInt(digit), 0);
    }

    handleIdentifyAnswer(answer) {
        const responseTime = Date.now() - this.responseStartTime;
        this.recordResponseTime(responseTime);
        
        const userAnswer = answer === 'yes';
        const isCorrect = userAnswer === this.currentAnswer;
        
        this.showFeedback(isCorrect, this.getIdentifyExplanation());
        this.updateScore(isCorrect);
        
        setTimeout(() => {
            this.hideFeedback();
            this.generateIdentifyQuestion();
        }, this.getAdaptiveDelay());
    }

    getIdentifyExplanation() {
        const digitSum = this.calculateDigitSum(this.currentNumber);
        const isMultiple = this.currentNumber % 3 === 0;
        
        if (isMultiple) {
            return `${this.currentNumber} ÷ 3 = ${this.currentNumber / 3}. Sum of digits: ${digitSum} (also divisible by 3).`;
        } else {
            const remainder = this.currentNumber % 3;
            return `${this.currentNumber} ÷ 3 = ${Math.floor(this.currentNumber / 3)} remainder ${remainder}. Sum of digits: ${digitSum}.`;
        }
    }

    generateMultiplyQuestion() {
        const maxMultiplier = Math.min(5 + this.level, 12);
        const multiplier = Math.floor(Math.random() * maxMultiplier) + 1;
        this.currentAnswer = 3 * multiplier;
        this.equationElement.textContent = `3 × ${multiplier} = ?`;
        this.multiplyInput.value = '';
        this.updateDraggableNumbers();
        setTimeout(() => {
            this.multiplyInput.focus();
        }, 100);
    }

    handleMultiplyAnswer() {
        const userAnswer = parseInt(this.multiplyInput.value);
        const isCorrect = userAnswer === this.currentAnswer;
        
        const explanation = `3 × ${this.currentAnswer / 3} = ${this.currentAnswer}`;
        this.showFeedback(isCorrect, explanation);
        this.updateScore(isCorrect);
        
        setTimeout(() => {
            this.hideFeedback();
            this.generateMultiplyQuestion();
        }, 2000);
    }

    generatePatternQuestion() {
        const startNumber = Math.floor(Math.random() * 10) * 3 + 3;
        const sequence = [];
        for (let i = 0; i < 4; i++) {
            sequence.push(startNumber + (i * 3));
        }
        
        this.currentAnswer = sequence[3];
        sequence[3] = '?';
        
        this.patternSequence.innerHTML = sequence.map(num => 
            `<span class="number-box ${num === '?' ? 'unknown' : ''}">${num}</span>`
        ).join('');
        
        this.patternInput.value = '';
        setTimeout(() => {
            this.patternInput.focus();
        }, 100);
    }

    handlePatternAnswer() {
        const userAnswer = parseInt(this.patternInput.value);
        const isCorrect = userAnswer === this.currentAnswer;
        
        const explanation = `The pattern increases by 3 each time. Next number: ${this.currentAnswer}`;
        this.showFeedback(isCorrect, explanation);
        this.updateScore(isCorrect);
        
        setTimeout(() => {
            this.hideFeedback();
            this.generatePatternQuestion();
        }, 2000);
    }

    initializeSkipCount() {
        this.skipCountSequence = [];
        this.skipCountIndex = 0;
        
        const maxNumber = Math.min(30 + (this.level - 1) * 20, 100);
        
        for (let i = 3; i <= maxNumber; i += 3) {
            this.skipCountSequence.push(i);
        }
        
        this.renderNumberGrid(maxNumber);
    }

    renderNumberGrid(maxNumber) {
        this.numberGrid.innerHTML = '';
        
        for (let i = 1; i <= maxNumber; i++) {
            const numberElement = document.createElement('div');
            numberElement.className = 'grid-number';
            numberElement.textContent = i;
            numberElement.addEventListener('click', () => this.handleGridClick(i, numberElement));
            this.numberGrid.appendChild(numberElement);
        }
    }

    handleGridClick(number, element) {
        if (element.classList.contains('correct') || element.classList.contains('incorrect')) {
            return;
        }
        
        const expectedNumber = this.skipCountSequence[this.skipCountIndex];
        
        if (number === expectedNumber) {
            element.classList.add('correct');
            this.skipCountIndex++;
            this.updateScore(true);
            
            if (this.skipCountIndex >= this.skipCountSequence.length) {
                setTimeout(() => {
                    this.showFeedback(true, `Great job! You found all multiples of 3 up to ${number}.`);
                    setTimeout(() => {
                        this.hideFeedback();
                        this.initializeSkipCount();
                    }, 2000);
                }, 500);
            }
        } else {
            element.classList.add('incorrect');
            this.updateScore(false);
            
            setTimeout(() => {
                this.showFeedback(false, `${number} is not the next multiple of 3. Try ${expectedNumber}!`);
                setTimeout(() => {
                    this.hideFeedback();
                    element.classList.remove('incorrect');
                }, 2000);
            }, 500);
        }
    }

    resetSkipCount() {
        this.skipCountIndex = 0;
        document.querySelectorAll('.grid-number').forEach(el => {
            el.classList.remove('correct', 'incorrect', 'selected');
        });
    }

    showFeedback(isCorrect, explanation) {
        this.feedbackPanel.classList.remove('correct', 'incorrect');
        this.feedbackPanel.classList.add(isCorrect ? 'correct' : 'incorrect');
        
        this.feedbackIcon.textContent = isCorrect ? '✓' : '✗';
        this.feedbackText.textContent = isCorrect ? 'Correct!' : 'Try again!';
        this.feedbackExplanation.textContent = explanation;
        
        this.feedbackPanel.classList.add('show');
    }

    hideFeedback() {
        this.feedbackPanel.classList.remove('show');
    }

    updateScore(isCorrect) {
        this.questionsInLevel++;
        this.totalQuestions++;
        
        if (isCorrect) {
            this.score += 10 * this.level;
            this.streak++;
            this.correctInLevel++;
            this.totalCorrect++;
            this.perfectStreak++;
            
            this.checkAchievements(isCorrect);
            
            if (this.streak > 0 && this.streak % 5 === 0) {
                this.score += 50;
            }
        } else {
            this.streak = 0;
            this.perfectStreak = 0;
        }
        
        if (this.questionsInLevel >= this.maxQuestionsPerLevel) {
            if (this.correctInLevel >= this.maxQuestionsPerLevel * 0.7) {
                this.level++;
                this.showFeedback(true, `Level up! Welcome to level ${this.level}!`);
                this.checkAchievements(isCorrect);
            }
            this.questionsInLevel = 0;
            this.correctInLevel = 0;
        }
        
        this.updateStats();
    }

    updateStats() {
        this.scoreElement.textContent = this.score;
        this.streakElement.textContent = this.streak;
        this.levelElement.textContent = this.level;
        
        const accuracy = this.totalQuestions > 0 ? Math.round((this.totalCorrect / this.totalQuestions) * 100) : 0;
        this.accuracyElement.textContent = `${accuracy}%`;
        
        const progress = (this.correctInLevel / this.maxQuestionsPerLevel) * 100;
        this.progressFill.style.width = `${Math.min(progress, 100)}%`;
    }

    toggleTips() {
        this.tipsContent.classList.toggle('hidden');
    }

    isMultipleOfThree(num) {
        return num % 3 === 0;
    }

    generateRandomMultiple() {
        const multiplier = Math.floor(Math.random() * 20) + 1;
        return 3 * multiplier;
    }

    generateRandomNonMultiple() {
        let num;
        do {
            num = Math.floor(Math.random() * 100) + 1;
        } while (this.isMultipleOfThree(num));
        return num;
    }

    addVisualRepresentation(number) {
        const breakdown = this.numberBreakdownElement;
        const digitSum = this.calculateDigitSum(number);
        
        const dotContainer = document.createElement('div');
        dotContainer.className = 'dot-container';
        
        for (let i = 0; i < Math.min(number, 24); i++) {
            const dot = document.createElement('div');
            dot.className = 'dot';
            if (i < Math.floor(number / 3) * 3) {
                dot.classList.add('grouped');
            } else {
                dot.classList.add('remainder');
            }
            dotContainer.appendChild(dot);
        }
        
        breakdown.innerHTML = '';
        breakdown.appendChild(dotContainer);
        const textDiv = document.createElement('div');
        textDiv.textContent = `Sum of digits: ${digitSum}`;
        breakdown.appendChild(textDiv);
    }

    recordResponseTime(time) {
        this.responseHistory.push(time);
        if (this.responseHistory.length > 10) {
            this.responseHistory.shift();
        }
        this.averageResponseTime = this.responseHistory.reduce((a, b) => a + b, 0) / this.responseHistory.length;
    }

    getAdaptiveDelay() {
        if (this.averageResponseTime < 2000) {
            return 1500;
        } else if (this.averageResponseTime < 5000) {
            return 2000;
        } else {
            return 2500;
        }
    }

    initializeFactorTree() {
        const possibleNumbers = [12, 15, 18, 21, 24, 27, 30, 36, 42, 45, 48, 54, 60, 63, 66, 72, 75, 81, 84, 90, 96, 99];
        this.factorTreeState.target = possibleNumbers[Math.floor(Math.random() * possibleNumbers.length)];
        this.factorTreeState.tree = [{ value: this.factorTreeState.target, level: 0, factors: [] }];
        this.factorTreeState.activeNode = null;
        
        this.factorTarget.textContent = this.factorTreeState.target;
        this.renderFactorTree();
        this.updateFactorOptions();
        
        this.factorOptions.addEventListener('click', (e) => {
            if (e.target.classList.contains('factor-btn')) {
                this.handleFactorSelection(parseInt(e.target.dataset.factor));
            }
        });
    }

    renderFactorTree() {
        this.factorTreeContainer.innerHTML = '';
        const levels = this.groupByLevel(this.factorTreeState.tree);
        
        levels.forEach((levelNodes, levelIndex) => {
            const levelDiv = document.createElement('div');
            levelDiv.className = 'tree-level';
            levelDiv.id = `tree-level-${levelIndex}`;
            
            levelNodes.forEach(node => {
                const nodeDiv = document.createElement('div');
                nodeDiv.className = 'factor-node';
                nodeDiv.dataset.value = node.value;
                nodeDiv.textContent = node.value;
                
                if (this.isPrime(node.value)) {
                    nodeDiv.classList.add('prime');
                } else if (node.factors.length === 0) {
                    nodeDiv.classList.add('composite');
                    nodeDiv.addEventListener('click', () => this.selectNode(node));
                } else {
                    nodeDiv.classList.add('factored');
                }
                
                if (this.factorTreeState.activeNode === node) {
                    nodeDiv.classList.add('active');
                }
                
                levelDiv.appendChild(nodeDiv);
            });
            
            this.factorTreeContainer.appendChild(levelDiv);
        });
    }

    groupByLevel(nodes) {
        const levels = [];
        nodes.forEach(node => {
            if (!levels[node.level]) levels[node.level] = [];
            levels[node.level].push(node);
        });
        return levels;
    }

    selectNode(node) {
        this.factorTreeState.activeNode = node;
        this.renderFactorTree();
        this.updateFactorOptions();
    }

    updateFactorOptions() {
        const activeValue = this.factorTreeState.activeNode?.value;
        const factorButtons = this.factorOptions.querySelectorAll('.factor-btn');
        
        factorButtons.forEach(btn => {
            const factor = parseInt(btn.dataset.factor);
            btn.classList.remove('disabled');
            
            if (!activeValue || activeValue % factor !== 0 || factor === activeValue || factor === 1) {
                btn.classList.add('disabled');
            }
        });
    }

    handleFactorSelection(factor) {
        if (!this.factorTreeState.activeNode) return;
        
        const activeNode = this.factorTreeState.activeNode;
        const complement = activeNode.value / factor;
        
        if (activeNode.value % factor === 0 && factor !== 1 && factor !== activeNode.value) {
            activeNode.factors = [factor, complement];
            
            this.factorTreeState.tree.push(
                { value: factor, level: activeNode.level + 1, factors: [] },
                { value: complement, level: activeNode.level + 1, factors: [] }
            );
            
            this.factorTreeState.activeNode = null;
            this.renderFactorTree();
            this.updateFactorOptions();
            
            if (this.isTreeComplete()) {
                this.factorTreesCompleted++;
                this.checkAchievements(true);
                this.showFeedback(true, `Excellent! You found all prime factors of ${this.factorTreeState.target}.`);
                setTimeout(() => {
                    this.hideFeedback();
                    this.initializeFactorTree();
                }, 2000);
            }
        }
    }

    isTreeComplete() {
        return this.factorTreeState.tree.every(node => 
            node.factors.length > 0 || this.isPrime(node.value)
        );
    }

    resetFactorTree() {
        this.initializeFactorTree();
    }

    initializeDivisibilityChain() {
        const startNumbers = [81, 54, 72, 96, 108, 144, 162, 189, 216, 243];
        this.chainState.start = startNumbers[Math.floor(Math.random() * startNumbers.length)];
        this.chainState.steps = [this.chainState.start];
        
        let current = this.chainState.start;
        while (current > 3 && current % 3 === 0) {
            current = current / 3;
            this.chainState.steps.push(current);
        }
        
        this.chainStart.textContent = this.chainState.start;
        this.chainInputs.forEach((input, index) => {
            input.value = '';
            input.placeholder = `Step ${index + 1}`;
        });
        
        this.chainExplanation.textContent = '';
    }

    handleChainAnswer() {
        const userAnswers = Array.from(this.chainInputs).map(input => parseInt(input.value) || 0);
        const correctAnswers = this.chainState.steps.slice(1, 4);
        
        let allCorrect = true;
        let explanation = `Starting with ${this.chainState.start}:\n`;
        
        for (let i = 0; i < Math.min(userAnswers.length, correctAnswers.length); i++) {
            const isStepCorrect = userAnswers[i] === correctAnswers[i];
            allCorrect = allCorrect && isStepCorrect;
            
            explanation += `${this.chainState.steps[i]} ÷ 3 = ${correctAnswers[i]}\n`;
        }
        
        this.showFeedback(allCorrect, explanation);
        this.updateScore(allCorrect);
        
        setTimeout(() => {
            this.hideFeedback();
            this.initializeDivisibilityChain();
        }, 3000);
    }

    isPrime(num) {
        if (num < 2) return false;
        for (let i = 2; i <= Math.sqrt(num); i++) {
            if (num % i === 0) return false;
        }
        return true;
    }

    checkAchievements(isCorrect) {
        const responseTime = Date.now() - this.responseStartTime;

        if (isCorrect && !this.achievements.has('first-correct')) {
            this.unlockAchievement('first-correct');
        }

        if (this.streak >= 5 && !this.achievements.has('streak-5')) {
            this.unlockAchievement('streak-5');
        }

        if (responseTime < 2000 && isCorrect && !this.achievements.has('speed-demon')) {
            this.unlockAchievement('speed-demon');
        }

        if (this.level >= 2 && !this.achievements.has('level-up')) {
            this.unlockAchievement('level-up');
        }

        if (this.perfectStreak >= 10 && !this.achievements.has('perfect-accuracy')) {
            this.unlockAchievement('perfect-accuracy');
        }

        if (this.factorTreesCompleted >= 5 && !this.achievements.has('factor-master')) {
            this.unlockAchievement('factor-master');
        }
    }

    unlockAchievement(achievementId) {
        this.achievements.add(achievementId);
        const achievementElement = document.querySelector(`[data-achievement="${achievementId}"]`);
        if (achievementElement) {
            achievementElement.classList.remove('locked');
            achievementElement.classList.add('unlocked');
            
            setTimeout(() => {
                this.showFeedback(true, `🏆 Achievement Unlocked: ${achievementElement.querySelector('.achievement-name').textContent}!`);
            }, 1000);
        }
    }

    handleKeyboardNavigation(e) {
        if (e.key === 'Escape') {
            this.hideFeedback();
        }
        
        if (this.currentMode === 'identify' || this.currentMode === 'fractions') {
            if (e.key === '1' || e.key === 'y' || e.key === 'Y') {
                if (this.currentMode === 'identify') {
                    this.handleIdentifyAnswer('yes');
                } else {
                    this.handleFractionAnswer('yes');
                }
            } else if (e.key === '2' || e.key === 'n' || e.key === 'N') {
                if (this.currentMode === 'identify') {
                    this.handleIdentifyAnswer('no');
                } else {
                    this.handleFractionAnswer('no');
                }
            }
        }
        
        if (e.key === 'Enter') {
            const activeElement = document.activeElement;
            if (activeElement && activeElement.classList.contains('answer-input')) {
                if (this.currentMode === 'multiply') {
                    this.handleMultiplyAnswer();
                } else if (this.currentMode === 'patterns') {
                    this.handlePatternAnswer();
                } else if (this.currentMode === 'divisibility-chain') {
                    this.handleChainAnswer();
                }
            }
        }
        
        if (e.key >= '1' && e.key <= '7') {
            const modeIndex = parseInt(e.key) - 1;
            const modes = ['identify', 'multiply', 'patterns', 'skip-count', 'factor-tree', 'divisibility-chain', 'fractions'];
            if (modes[modeIndex]) {
                this.switchMode(modes[modeIndex]);
            }
        }
        
        if (e.key === '?' || e.key === 'h' || e.key === 'H') {
            this.toggleTips();
        }
    }

    initializeFractions() {
        const fractionPairs = [
            [6, 9], [9, 12], [12, 15], [15, 18], [18, 21], [21, 24],
            [3, 6], [6, 12], [9, 15], [12, 18], [15, 21], [18, 24],
            [4, 8], [5, 10], [7, 14], [8, 16], [10, 20], [11, 22],
            [6, 8], [9, 16], [12, 20], [15, 25], [18, 28], [21, 32]
        ];
        
        const selectedPair = fractionPairs[Math.floor(Math.random() * fractionPairs.length)];
        this.fractionState.numerator = selectedPair[0];
        this.fractionState.denominator = selectedPair[1];
        
        const gcd = this.getGCD(this.fractionState.numerator, this.fractionState.denominator);
        this.fractionState.isReducible = gcd === 3 || (gcd > 1 && gcd % 3 === 0);
        
        this.fractionNumerator.textContent = this.fractionState.numerator;
        this.fractionDenominator.textContent = this.fractionState.denominator;
        
        this.renderFractionVisual();
        this.fractionExplanation.textContent = '';
    }

    renderFractionVisual() {
        this.fractionVisual.innerHTML = '';
        
        const totalCircles = this.fractionState.denominator;
        const filledCircles = this.fractionState.numerator;
        
        for (let i = 0; i < totalCircles; i++) {
            const circle = document.createElement('div');
            circle.className = 'fraction-circle';
            
            if (i < filledCircles) {
                circle.classList.add('filled');
            }
            
            this.fractionVisual.appendChild(circle);
        }
    }

    handleFractionAnswer(answer) {
        const userAnswer = answer === 'yes';
        const isCorrect = userAnswer === this.fractionState.isReducible;
        
        const explanation = this.getFractionExplanation();
        this.showFeedback(isCorrect, explanation);
        this.updateScore(isCorrect);
        
        setTimeout(() => {
            this.hideFeedback();
            this.initializeFractions();
        }, 3000);
    }

    getFractionExplanation() {
        const gcd = this.getGCD(this.fractionState.numerator, this.fractionState.denominator);
        
        if (this.fractionState.isReducible) {
            const reducedNum = this.fractionState.numerator / gcd;
            const reducedDen = this.fractionState.denominator / gcd;
            return `${this.fractionState.numerator}/${this.fractionState.denominator} can be reduced by dividing both by ${gcd} to get ${reducedNum}/${reducedDen}`;
        } else {
            return `${this.fractionState.numerator}/${this.fractionState.denominator} cannot be reduced using multiples of 3. GCD is ${gcd}.`;
        }
    }

    getGCD(a, b) {
        while (b !== 0) {
            const temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    setupNumberPads() {
        this.numberPads.forEach(pad => {
            pad.addEventListener('click', (e) => {
                if (e.target.classList.contains('num-btn')) {
                    this.handleNumberPadClick(e.target);
                }
            });
        });
    }

    setupInputValidation() {
        const inputs = document.querySelectorAll('.answer-input, .chain-input');
        inputs.forEach(input => {
            input.addEventListener('focus', (e) => {
                this.currentActiveInput = e.target;
                this.showNumberPadForInput(e.target);
                this.autoFocusInput(e.target);
            });

            input.addEventListener('blur', (e) => {
                setTimeout(() => {
                    if (!document.activeElement.classList.contains('num-btn')) {
                        this.hideNumberPads();
                    }
                }, 100);
            });

            input.addEventListener('input', (e) => {
                this.validateInput(e.target);
                this.formatInput(e.target);
            });

            input.addEventListener('keydown', (e) => {
                this.handleInputKeydown(e);
            });
        });
    }

    showNumberPadForInput(input) {
        this.hideNumberPads();
        
        const inputContainer = input.closest('.game-mode');
        const numberPad = inputContainer.querySelector('.number-pad');
        
        if (numberPad) {
            numberPad.style.display = 'grid';
            numberPad.style.opacity = '0';
            numberPad.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                numberPad.style.opacity = '1';
                numberPad.style.transform = 'translateY(0)';
            }, 10);
        }
    }

    hideNumberPads() {
        this.numberPads.forEach(pad => {
            pad.style.display = 'none';
        });
    }

    handleNumberPadClick(button) {
        if (!this.currentActiveInput) return;

        const action = button.dataset.action;
        const num = button.dataset.num;

        if (action === 'clear') {
            this.currentActiveInput.value = '';
            this.addInputAnimation(button, 'clear');
        } else if (action === 'backspace') {
            this.currentActiveInput.value = this.currentActiveInput.value.slice(0, -1);
            this.addInputAnimation(button, 'backspace');
        } else if (num) {
            const currentValue = this.currentActiveInput.value;
            const maxLength = this.getMaxLength(this.currentActiveInput);
            
            if (currentValue.length < maxLength) {
                this.currentActiveInput.value = currentValue + num;
                this.addInputAnimation(button, 'number');
            }
        }

        this.validateInput(this.currentActiveInput);
        this.formatInput(this.currentActiveInput);
    }

    addInputAnimation(button, type) {
        button.style.transform = 'scale(0.95)';
        button.style.background = type === 'clear' ? '#f56565' : 
                                  type === 'backspace' ? '#ed8936' : '#4299e1';
        button.style.color = 'white';

        setTimeout(() => {
            button.style.transform = '';
            button.style.background = '';
            button.style.color = '';
        }, 150);
    }

    getMaxLength(input) {
        if (input.classList.contains('chain-input')) return 2;
        return 3;
    }

    validateInput(input) {
        const value = parseInt(input.value);
        const validationElement = this.getValidationElement(input);
        
        input.classList.remove('valid', 'invalid');
        validationElement.classList.remove('show', 'valid', 'invalid');

        if (input.value === '') {
            return;
        }

        const isValid = this.isValidInput(input, value);
        
        if (isValid) {
            input.classList.add('valid');
            validationElement.classList.add('show', 'valid');
            validationElement.textContent = this.getValidMessage(input, value);
        } else {
            input.classList.add('invalid');
            validationElement.classList.add('show', 'invalid');
            validationElement.textContent = this.getInvalidMessage(input, value);
        }
    }

    getValidationElement(input) {
        const container = input.closest('.input-container');
        return container.querySelector('.input-validation');
    }

    isValidInput(input, value) {
        if (isNaN(value) || value < 0) return false;
        
        const max = parseInt(input.getAttribute('max')) || 999;
        if (value > max) return false;

        if (this.currentMode === 'multiply') {
            return value <= 144;
        } else if (this.currentMode === 'patterns') {
            return value <= 300;
        } else if (this.currentMode === 'divisibility-chain') {
            return value <= 999;
        }
        
        return true;
    }

    getValidMessage(input, value) {
        if (this.currentMode === 'multiply') {
            return value % 3 === 0 ? 'Multiple of 3 ✓' : 'Good input';
        } else if (this.currentMode === 'patterns') {
            return value % 3 === 0 ? 'Multiple of 3 ✓' : 'Valid number';
        }
        return 'Valid';
    }

    getInvalidMessage(input, value) {
        if (isNaN(value)) return 'Enter a number';
        if (value < 0) return 'Positive numbers only';
        
        const max = parseInt(input.getAttribute('max')) || 999;
        if (value > max) return `Max: ${max}`;
        
        return 'Invalid input';
    }

    formatInput(input) {
        let value = input.value.replace(/[^0-9]/g, '');
        
        if (value.length > 0) {
            value = parseInt(value).toString();
        }
        
        input.value = value;
    }

    autoFocusInput(input) {
        input.select();
        
        setTimeout(() => {
            const hint = this.createInputHint(input);
            input.parentNode.appendChild(hint);
            
            setTimeout(() => {
                hint.classList.add('show');
            }, 10);
            
            setTimeout(() => {
                hint.classList.remove('show');
                setTimeout(() => {
                    if (hint.parentNode) {
                        hint.parentNode.removeChild(hint);
                    }
                }, 300);
            }, 2000);
        }, 100);
    }

    createInputHint(input) {
        const hint = document.createElement('div');
        hint.className = 'input-hint';
        
        if (this.currentMode === 'multiply') {
            hint.textContent = 'Enter the product';
        } else if (this.currentMode === 'patterns') {
            hint.textContent = 'What comes next?';
        } else if (this.currentMode === 'divisibility-chain') {
            hint.textContent = 'Divide by 3';
        }
        
        return hint;
    }

    handleInputKeydown(e) {
        const input = e.target;
        
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            e.preventDefault();
            const currentValue = parseInt(input.value) || 0;
            const increment = e.key === 'ArrowUp' ? 1 : -1;
            const newValue = Math.max(0, currentValue + increment);
            
            input.value = newValue;
            this.validateInput(input);
            this.formatInput(input);
        }
        
        if (e.key === 'Tab') {
            const inputs = Array.from(document.querySelectorAll('.answer-input:not([style*="display: none"]), .chain-input:not([style*="display: none"])'));
            const currentIndex = inputs.indexOf(input);
            
            if (currentIndex >= 0) {
                const nextInput = inputs[currentIndex + (e.shiftKey ? -1 : 1)];
                if (nextInput) {
                    e.preventDefault();
                    nextInput.focus();
                }
            }
        }
    }

    setupDragAndDrop() {
        const dragNumbers = document.querySelectorAll('.drag-number');
        const inputContainers = document.querySelectorAll('.input-container');

        dragNumbers.forEach(dragNum => {
            dragNum.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', e.target.dataset.value);
                e.target.classList.add('dragging');
                
                inputContainers.forEach(container => {
                    container.classList.add('drag-target');
                });
            });

            dragNum.addEventListener('dragend', (e) => {
                e.target.classList.remove('dragging');
                
                inputContainers.forEach(container => {
                    container.classList.remove('drag-target');
                });
            });
        });

        inputContainers.forEach(container => {
            container.addEventListener('dragover', (e) => {
                e.preventDefault();
                container.parentElement.classList.add('drag-over');
            });

            container.addEventListener('dragleave', (e) => {
                container.parentElement.classList.remove('drag-over');
            });

            container.addEventListener('drop', (e) => {
                e.preventDefault();
                const value = e.dataTransfer.getData('text/plain');
                const input = container.querySelector('.answer-input, .chain-input');
                
                if (input && value) {
                    input.value = value;
                    this.validateInput(input);
                    this.formatInput(input);
                    
                    const draggedElement = document.querySelector(`.drag-number[data-value="${value}"]`);
                    if (draggedElement) {
                        draggedElement.classList.add('used');
                        setTimeout(() => {
                            draggedElement.classList.remove('used');
                        }, 2000);
                    }
                }
                
                container.parentElement.classList.remove('drag-over');
            });
        });
    }

    formatInput(input) {
        let value = input.value.replace(/[^0-9]/g, '');
        
        if (value.length > 0) {
            value = parseInt(value).toString();
            
            if (value.length > 2) {
                input.classList.add('formatted');
                const formatted = value.replace(/(\d)(?=(\d{2})+(?!\d))/g, '$1,');
                input.setAttribute('data-formatted', formatted);
            } else {
                input.classList.remove('formatted');
                input.removeAttribute('data-formatted');
            }
        }
        
        input.value = value;
    }

    updateDraggableNumbers() {
        const draggableContainer = document.querySelector(`#draggable-${this.currentMode}`);
        if (!draggableContainer) return;

        draggableContainer.innerHTML = '';
        
        let numbers = [];
        if (this.currentMode === 'multiply') {
            const maxRange = Math.min(12 * 3, 36);
            for (let i = 3; i <= maxRange; i += 3) {
                numbers.push(i);
            }
        } else if (this.currentMode === 'patterns') {
            for (let i = 3; i <= 60; i += 3) {
                numbers.push(i);
            }
        }

        numbers.forEach(num => {
            const dragNum = document.createElement('div');
            dragNum.className = 'drag-number';
            dragNum.draggable = true;
            dragNum.dataset.value = num;
            dragNum.textContent = num;
            draggableContainer.appendChild(dragNum);
        });

        this.setupDragAndDrop();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const game = new NumberSenseGame();
    
    window.addEventListener('beforeunload', () => {
        const gameState = {
            score: game.score,
            level: game.level,
            streak: game.streak
        };
        localStorage.setItem('numberSenseGameState', JSON.stringify(gameState));
    });
    
    const savedState = localStorage.getItem('numberSenseGameState');
    if (savedState) {
        const state = JSON.parse(savedState);
        game.score = state.score || 0;
        game.level = state.level || 1;
        game.streak = state.streak || 0;
        game.updateStats();
    }
});

function showNumber(number) {
    const factors = [];
    for (let i = 1; i <= number; i++) {
        if (number % i === 0) {
            factors.push(i);
        }
    }
    return factors;
}

function getMultiplesOfThree(limit) {
    const multiples = [];
    for (let i = 3; i <= limit; i += 3) {
        multiples.push(i);
    }
    return multiples;
}

function checkDivisibilityRule(number) {
    const digits = number.toString().split('').map(Number);
    const sum = digits.reduce((a, b) => a + b, 0);
    return {
        number: number,
        digits: digits,
        sum: sum,
        isDivisibleByThree: sum % 3 === 0,
        explanation: `${digits.join(' + ')} = ${sum}, which ${sum % 3 === 0 ? 'is' : 'is not'} divisible by 3`
    };
}