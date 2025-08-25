// Bundled Number Sense 3s Application
// This is a single-file version that works without module imports

class NumberSense3sApp {
    constructor() {
        this.config = {
            difficulty: 'intermediate',
            soundEnabled: true,
            animationsEnabled: true,
            hintsEnabled: true,
            currentMode: 'identify'
        };
        
        this.gameState = {
            score: 0,
            streak: 0,
            level: 1,
            totalQuestions: 0,
            totalCorrect: 0,
            currentQuestion: null,
            sessionStartTime: Date.now()
        };
        
        this.modes = {
            'identify': { name: 'Identify Multiples', icon: '🎯' },
            'multiply': { name: 'Multiplication', icon: '✖️' },
            'patterns': { name: 'Pattern Recognition', icon: '🔢' },
            'skip-count': { name: 'Skip Counting', icon: '🏃' },
            'factor-tree': { name: 'Factor Trees', icon: '🌳' },
            'chain': { name: 'Divisibility Chain', icon: '⛓️' },
            'fractions': { name: 'Fractions & 3s', icon: '🥧' }
        };
        
        this.currentUser = {
            username: 'Guest',
            score: 0,
            level: 1
        };
    }

    initialize() {
        console.log('Initializing Number Sense 3s...');
        
        // Hide loading screen
        const loadingScreen = document.getElementById('loading-screen');
        const app = document.getElementById('app');
        
        if (loadingScreen) {
            setTimeout(() => {
                loadingScreen.style.display = 'none';
                if (app) app.style.display = 'block';
            }, 1000);
        }
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initialize first game mode
        this.startMode('identify');
        
        // Update UI
        this.updateStats();
        
        console.log('Application initialized successfully');
    }

    setupEventListeners() {
        // Navigation tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.switchMode(mode);
            });
        });
        
        // Settings button
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.openSettings());
        }
        
        // User menu button
        const userMenuBtn = document.getElementById('user-menu-btn');
        if (userMenuBtn) {
            userMenuBtn.addEventListener('click', () => this.openProfile());
        }
        
        // Help button
        const helpBtn = document.getElementById('help-btn');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => this.showHelp());
        }
        
        // Hint button
        const hintBtn = document.getElementById('hint-btn');
        if (hintBtn) {
            hintBtn.addEventListener('click', () => this.showHint());
        }
        
        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) modal.style.display = 'none';
            });
        });
        
        // Settings form
        this.setupSettingsForm();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    setupSettingsForm() {
        // Difficulty radio buttons
        document.querySelectorAll('input[name="difficulty"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.config.difficulty = e.target.value;
                this.saveSettings();
            });
        });
        
        // Toggle switches
        const soundToggle = document.getElementById('sound-enabled');
        if (soundToggle) {
            soundToggle.addEventListener('change', (e) => {
                this.config.soundEnabled = e.target.checked;
                this.saveSettings();
            });
        }
        
        const animationsToggle = document.getElementById('animations-enabled');
        if (animationsToggle) {
            animationsToggle.addEventListener('change', (e) => {
                this.config.animationsEnabled = e.target.checked;
                document.body.classList.toggle('no-animations', !e.target.checked);
                this.saveSettings();
            });
        }
        
        // Data management buttons
        const exportBtn = document.getElementById('export-data');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }
        
        const resetBtn = document.getElementById('reset-progress');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetProgress());
        }
    }

    switchMode(mode) {
        // Update active tab
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === mode);
        });
        
        this.config.currentMode = mode;
        this.startMode(mode);
    }

    startMode(mode) {
        const gameContent = document.getElementById('game-content');
        if (!gameContent) return;
        
        // Clear previous content
        gameContent.innerHTML = '';
        
        // Create mode-specific content
        switch(mode) {
            case 'identify':
                this.createIdentifyMode(gameContent);
                break;
            case 'multiply':
                this.createMultiplyMode(gameContent);
                break;
            case 'patterns':
                this.createPatternsMode(gameContent);
                break;
            case 'skip-count':
                this.createSkipCountMode(gameContent);
                break;
            case 'factor-tree':
                this.createFactorTreeMode(gameContent);
                break;
            case 'chain':
                this.createChainMode(gameContent);
                break;
            case 'fractions':
                this.createFractionsMode(gameContent);
                break;
        }
        
        this.showNotification(`Switched to ${this.modes[mode].name} mode`, 'info');
    }

    createIdentifyMode(container) {
        const number = this.generateNumber();
        this.currentQuestion = {
            type: 'identify',
            number: number,
            answer: number % 3 === 0
        };
        
        container.innerHTML = `
            <div class="question-display">
                <h2>Is this number a multiple of 3?</h2>
                <div class="number-showcase">${number}</div>
                <div class="digit-sum">Sum of digits: ${this.getDigitSum(number)}</div>
            </div>
            <div class="button-group">
                <button class="btn btn-success" onclick="app.checkAnswer(true)">
                    ✓ Yes (Y)
                </button>
                <button class="btn btn-danger" onclick="app.checkAnswer(false)">
                    ✗ No (N)
                </button>
            </div>
        `;
    }

    createMultiplyMode(container) {
        const multiplier = Math.floor(Math.random() * 12) + 1;
        this.currentQuestion = {
            type: 'multiply',
            multiplier: multiplier,
            answer: 3 * multiplier
        };
        
        container.innerHTML = `
            <div class="question-display">
                <h2>What is the answer?</h2>
                <div class="number-showcase">3 × ${multiplier} = ?</div>
            </div>
            <div class="input-group">
                <input type="number" id="answer-input" class="input-field" 
                       placeholder="Enter your answer" autofocus>
            </div>
            <div class="button-group">
                <button class="btn btn-primary" onclick="app.checkMultiplyAnswer()">
                    Submit (Enter)
                </button>
            </div>
        `;
        
        // Add enter key listener
        const input = document.getElementById('answer-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.checkMultiplyAnswer();
            });
        }
    }

    createPatternsMode(container) {
        const start = Math.floor(Math.random() * 10) * 3 + 3;
        const pattern = [start, start + 3, start + 6, start + 9];
        this.currentQuestion = {
            type: 'pattern',
            pattern: pattern,
            answer: start + 9
        };
        
        container.innerHTML = `
            <div class="question-display">
                <h2>Complete the pattern</h2>
                <div class="pattern-sequence">
                    <span class="pattern-number">${pattern[0]}</span>
                    <span class="pattern-number">${pattern[1]}</span>
                    <span class="pattern-number">${pattern[2]}</span>
                    <span class="pattern-number unknown">?</span>
                </div>
            </div>
            <div class="input-group">
                <input type="number" id="pattern-input" class="input-field" 
                       placeholder="Next number" autofocus>
            </div>
            <div class="button-group">
                <button class="btn btn-primary" onclick="app.checkPatternAnswer()">
                    Submit
                </button>
            </div>
        `;
    }

    createSkipCountMode(container) {
        const maxNum = 30 + (this.gameState.level - 1) * 15;
        const gridSize = Math.min(maxNum, 100);
        
        container.innerHTML = `
            <div class="question-display">
                <h2>Click the multiples of 3 in order!</h2>
                <div class="number-grid" id="skip-grid"></div>
            </div>
            <div class="button-group">
                <button class="btn btn-secondary" onclick="app.resetSkipCount()">
                    Reset Grid
                </button>
            </div>
        `;
        
        const grid = document.getElementById('skip-grid');
        if (grid) {
            for (let i = 1; i <= gridSize; i++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                cell.textContent = i;
                cell.dataset.number = i;
                cell.addEventListener('click', () => this.handleGridClick(i));
                grid.appendChild(cell);
            }
        }
        
        this.skipCountSequence = [];
        for (let i = 3; i <= gridSize; i += 3) {
            this.skipCountSequence.push(i);
        }
        this.skipCountIndex = 0;
    }

    createFactorTreeMode(container) {
        const numbers = [12, 18, 24, 27, 36, 45, 54, 63, 72, 81];
        const target = numbers[Math.floor(Math.random() * numbers.length)];
        
        container.innerHTML = `
            <div class="question-display">
                <h2>Build the factor tree for ${target}</h2>
                <div class="factor-tree-container">
                    <div class="factor-node root">${target}</div>
                </div>
                <div class="factor-buttons">
                    ${this.getFactors(target).map(f => 
                        `<button class="btn btn-secondary" onclick="app.applyFactor(${f})">${f}</button>`
                    ).join('')}
                </div>
            </div>
        `;
        
        this.currentQuestion = {
            type: 'factor-tree',
            target: target,
            factors: this.getFactors(target)
        };
    }

    createChainMode(container) {
        const starts = [27, 54, 81, 108, 135, 162];
        const start = starts[Math.floor(Math.random() * starts.length)];
        
        container.innerHTML = `
            <div class="question-display">
                <h2>Follow the division chain</h2>
                <div class="chain-display">
                    <span class="chain-number">${start}</span>
                    <span class="chain-arrow">÷3→</span>
                    <input type="number" class="chain-input" id="chain1" placeholder="?">
                    <span class="chain-arrow">÷3→</span>
                    <input type="number" class="chain-input" id="chain2" placeholder="?">
                    <span class="chain-arrow">÷3→</span>
                    <input type="number" class="chain-input" id="chain3" placeholder="?">
                </div>
            </div>
            <div class="button-group">
                <button class="btn btn-primary" onclick="app.checkChainAnswer()">
                    Check Chain
                </button>
            </div>
        `;
        
        this.currentQuestion = {
            type: 'chain',
            start: start,
            answers: [start/3, start/9, start/27]
        };
    }

    createFractionsMode(container) {
        const fractions = [
            [3, 9], [6, 9], [9, 12], [12, 15], [15, 18],
            [3, 6], [6, 12], [9, 15], [12, 18], [15, 21]
        ];
        const [num, den] = fractions[Math.floor(Math.random() * fractions.length)];
        
        const gcd = this.getGCD(num, den);
        const canReduce = gcd > 1 && gcd % 3 === 0;
        
        container.innerHTML = `
            <div class="question-display">
                <h2>Can this fraction be reduced using 3?</h2>
                <div class="fraction-display">
                    <div class="numerator">${num}</div>
                    <div class="fraction-bar"></div>
                    <div class="denominator">${den}</div>
                </div>
            </div>
            <div class="button-group">
                <button class="btn btn-success" onclick="app.checkFractionAnswer(true)">
                    ✓ Yes, it can be reduced
                </button>
                <button class="btn btn-danger" onclick="app.checkFractionAnswer(false)">
                    ✗ No, it cannot be reduced
                </button>
            </div>
        `;
        
        this.currentQuestion = {
            type: 'fraction',
            numerator: num,
            denominator: den,
            answer: canReduce
        };
    }

    // Answer checking methods
    checkAnswer(userAnswer) {
        const correct = userAnswer === this.currentQuestion.answer;
        this.processResult(correct);
        
        if (correct) {
            this.showNotification('Correct! Well done!', 'success');
        } else {
            const explanation = this.currentQuestion.number % 3 === 0 
                ? `${this.currentQuestion.number} is divisible by 3`
                : `${this.currentQuestion.number} is not divisible by 3`;
            this.showNotification(`Not quite. ${explanation}`, 'error');
        }
        
        setTimeout(() => this.createIdentifyMode(document.getElementById('game-content')), 2000);
    }

    checkMultiplyAnswer() {
        const input = document.getElementById('answer-input');
        if (!input) return;
        
        const userAnswer = parseInt(input.value);
        const correct = userAnswer === this.currentQuestion.answer;
        this.processResult(correct);
        
        if (correct) {
            this.showNotification('Correct!', 'success');
        } else {
            this.showNotification(`The answer is ${this.currentQuestion.answer}`, 'error');
        }
        
        setTimeout(() => this.createMultiplyMode(document.getElementById('game-content')), 2000);
    }

    checkPatternAnswer() {
        const input = document.getElementById('pattern-input');
        if (!input) return;
        
        const userAnswer = parseInt(input.value);
        const correct = userAnswer === this.currentQuestion.answer;
        this.processResult(correct);
        
        if (correct) {
            this.showNotification('Perfect pattern recognition!', 'success');
        } else {
            this.showNotification(`The next number is ${this.currentQuestion.answer}`, 'error');
        }
        
        setTimeout(() => this.createPatternsMode(document.getElementById('game-content')), 2000);
    }

    handleGridClick(number) {
        const expectedNumber = this.skipCountSequence[this.skipCountIndex];
        const cell = document.querySelector(`[data-number="${number}"]`);
        
        if (number === expectedNumber) {
            cell.classList.add('correct');
            this.skipCountIndex++;
            this.processResult(true);
            
            if (this.skipCountIndex >= this.skipCountSequence.length) {
                this.showNotification('Excellent! You found all multiples of 3!', 'success');
                setTimeout(() => this.createSkipCountMode(document.getElementById('game-content')), 2000);
            }
        } else {
            cell.classList.add('incorrect');
            this.processResult(false);
            this.showNotification(`That's not the next multiple of 3. Looking for ${expectedNumber}`, 'error');
            
            setTimeout(() => {
                cell.classList.remove('incorrect');
            }, 1000);
        }
    }

    checkChainAnswer() {
        const chain1 = parseInt(document.getElementById('chain1').value);
        const chain2 = parseInt(document.getElementById('chain2').value);
        const chain3 = parseInt(document.getElementById('chain3').value);
        
        const allCorrect = 
            chain1 === this.currentQuestion.answers[0] &&
            chain2 === this.currentQuestion.answers[1] &&
            chain3 === this.currentQuestion.answers[2];
        
        this.processResult(allCorrect);
        
        if (allCorrect) {
            this.showNotification('Perfect chain!', 'success');
        } else {
            this.showNotification(`The chain should be: ${this.currentQuestion.answers.join(' → ')}`, 'error');
        }
        
        setTimeout(() => this.createChainMode(document.getElementById('game-content')), 2000);
    }

    checkFractionAnswer(userAnswer) {
        const correct = userAnswer === this.currentQuestion.answer;
        this.processResult(correct);
        
        const gcd = this.getGCD(this.currentQuestion.numerator, this.currentQuestion.denominator);
        
        if (correct) {
            if (this.currentQuestion.answer) {
                this.showNotification(`Correct! Both can be divided by ${gcd}`, 'success');
            } else {
                this.showNotification('Correct! This fraction cannot be reduced by 3', 'success');
            }
        } else {
            this.showNotification('Not quite. Try again!', 'error');
        }
        
        setTimeout(() => this.createFractionsMode(document.getElementById('game-content')), 2000);
    }

    // Helper methods
    generateNumber() {
        const max = 30 + (this.gameState.level - 1) * 20;
        return Math.floor(Math.random() * max) + 1;
    }

    getDigitSum(number) {
        return number.toString().split('').reduce((sum, digit) => sum + parseInt(digit), 0);
    }

    getFactors(number) {
        const factors = [];
        for (let i = 2; i <= Math.sqrt(number); i++) {
            if (number % i === 0) {
                factors.push(i);
                if (i !== number / i) {
                    factors.push(number / i);
                }
            }
        }
        return factors.sort((a, b) => a - b);
    }

    getGCD(a, b) {
        while (b !== 0) {
            const temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    processResult(correct) {
        this.gameState.totalQuestions++;
        
        if (correct) {
            this.gameState.score += 10 * this.gameState.level;
            this.gameState.streak++;
            this.gameState.totalCorrect++;
            
            // Check for level up
            if (this.gameState.totalCorrect % 10 === 0) {
                this.gameState.level++;
                this.showNotification(`Level up! Welcome to level ${this.gameState.level}!`, 'success');
            }
        } else {
            this.gameState.streak = 0;
        }
        
        this.updateStats();
    }

    updateStats() {
        document.getElementById('score').textContent = this.gameState.score;
        document.getElementById('streak').textContent = this.gameState.streak;
        document.getElementById('level').textContent = this.gameState.level;
        
        const accuracy = this.gameState.totalQuestions > 0 
            ? Math.round((this.gameState.totalCorrect / this.gameState.totalQuestions) * 100)
            : 0;
        document.getElementById('accuracy').textContent = `${accuracy}%`;
        
        const mastery = Math.min(100, Math.round((this.gameState.totalCorrect / 50) * 100));
        document.getElementById('mastery').textContent = `${mastery}%`;
        
        // Update progress bar
        const progress = (this.gameState.totalCorrect % 10) * 10;
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
        document.getElementById('progress-percent').textContent = `${progress}%`;
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    showHint() {
        const hints = {
            'identify': 'Add up all the digits. If the sum is divisible by 3, so is the number!',
            'multiply': 'Try skip counting by 3s to reach the answer',
            'patterns': 'Look at the difference between consecutive numbers',
            'skip-count': 'Start with 3, then add 3 each time',
            'factor-tree': 'Find two numbers that multiply to give the target',
            'chain': 'Divide each number by 3 to get the next',
            'fractions': 'Check if both numbers share 3 as a common factor'
        };
        
        const hint = hints[this.config.currentMode] || 'Take your time and think carefully!';
        this.showNotification(`💡 Hint: ${hint}`, 'info');
    }

    showHelp() {
        this.showNotification('Press 1-7 to switch modes, Y/N for yes/no, Enter to submit', 'info');
    }

    handleKeyboard(e) {
        // Number keys for mode switching
        if (e.key >= '1' && e.key <= '7') {
            const modes = ['identify', 'multiply', 'patterns', 'skip-count', 'factor-tree', 'chain', 'fractions'];
            const mode = modes[parseInt(e.key) - 1];
            if (mode) this.switchMode(mode);
        }
        
        // Y/N for yes/no questions
        if (this.config.currentMode === 'identify' || this.config.currentMode === 'fractions') {
            if (e.key === 'y' || e.key === 'Y') {
                this.checkAnswer(true);
            } else if (e.key === 'n' || e.key === 'N') {
                this.checkAnswer(false);
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.style.display = 'none';
            });
        }
        
        // H for hint
        if (e.key === 'h' || e.key === 'H') {
            this.showHint();
        }
    }

    openSettings() {
        const modal = document.getElementById('settings-modal');
        if (modal) modal.style.display = 'block';
    }

    openProfile() {
        const modal = document.getElementById('profile-modal');
        if (modal) modal.style.display = 'block';
        
        // Update profile stats
        document.getElementById('total-score').textContent = this.gameState.score;
        document.getElementById('total-questions').textContent = this.gameState.totalQuestions;
        
        const accuracy = this.gameState.totalQuestions > 0 
            ? Math.round((this.gameState.totalCorrect / this.gameState.totalQuestions) * 100)
            : 0;
        document.getElementById('overall-accuracy').textContent = `${accuracy}%`;
        
        const timePlayed = Math.floor((Date.now() - this.gameState.sessionStartTime) / 60000);
        document.getElementById('time-played').textContent = `${Math.floor(timePlayed / 60)}h ${timePlayed % 60}m`;
    }

    saveSettings() {
        localStorage.setItem('number_sense_3s_config', JSON.stringify(this.config));
        this.showNotification('Settings saved', 'success');
    }

    loadSettings() {
        const saved = localStorage.getItem('number_sense_3s_config');
        if (saved) {
            try {
                this.config = JSON.parse(saved);
            } catch (e) {
                console.error('Failed to load settings:', e);
            }
        }
    }

    exportData() {
        const data = {
            config: this.config,
            gameState: this.gameState,
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `number_sense_3s_${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('Data exported successfully', 'success');
    }

    resetProgress() {
        if (confirm('Are you sure you want to reset all progress?')) {
            this.gameState = {
                score: 0,
                streak: 0,
                level: 1,
                totalQuestions: 0,
                totalCorrect: 0,
                currentQuestion: null,
                sessionStartTime: Date.now()
            };
            
            this.updateStats();
            this.showNotification('Progress reset', 'info');
            
            // Restart current mode
            this.startMode(this.config.currentMode);
        }
    }

    resetSkipCount() {
        this.skipCountIndex = 0;
        document.querySelectorAll('.grid-cell').forEach(cell => {
            cell.classList.remove('correct', 'incorrect');
        });
    }

    applyFactor(factor) {
        this.showNotification(`Factor ${factor} selected`, 'info');
    }
}

// Add styles for notifications
const style = document.createElement('style');
style.textContent = `
    .loading-screen {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }
    
    .loading-content {
        text-align: center;
        color: white;
    }
    
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 20px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .notification-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
    }
    
    .notification {
        background: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateX(400px);
        transition: transform 0.3s ease;
        min-width: 250px;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left: 4px solid #10B981;
        background: #F0FDF4;
        color: #065F46;
    }
    
    .notification-error {
        border-left: 4px solid #EF4444;
        background: #FEF2F2;
        color: #991B1B;
    }
    
    .notification-info {
        border-left: 4px solid #3B82F6;
        background: #EFF6FF;
        color: #1E40AF;
    }
    
    .pattern-sequence {
        display: flex;
        gap: 20px;
        justify-content: center;
        margin: 30px 0;
    }
    
    .pattern-number {
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #F3F4F6;
        border: 2px solid #D1D5DB;
        border-radius: 12px;
        font-size: 24px;
        font-weight: bold;
    }
    
    .pattern-number.unknown {
        background: #FEE2E2;
        border-color: #EF4444;
        color: #EF4444;
    }
    
    .number-grid {
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 8px;
        max-width: 500px;
        margin: 20px auto;
    }
    
    .grid-cell {
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #F9FAFB;
        border: 2px solid #E5E7EB;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .grid-cell:hover {
        background: #F3F4F6;
        transform: scale(1.05);
    }
    
    .grid-cell.correct {
        background: #10B981;
        color: white;
        border-color: #059669;
    }
    
    .grid-cell.incorrect {
        background: #EF4444;
        color: white;
        border-color: #DC2626;
    }
    
    .chain-display {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin: 30px 0;
        flex-wrap: wrap;
    }
    
    .chain-number {
        font-size: 32px;
        font-weight: bold;
        color: #5B21B6;
    }
    
    .chain-arrow {
        font-size: 24px;
        color: #6B7280;
    }
    
    .chain-input {
        width: 80px;
        padding: 10px;
        border: 2px solid #D1D5DB;
        border-radius: 8px;
        font-size: 20px;
        text-align: center;
    }
    
    .fraction-display {
        display: inline-block;
        text-align: center;
        font-size: 48px;
        font-weight: bold;
        margin: 30px 0;
    }
    
    .numerator {
        color: #5B21B6;
    }
    
    .fraction-bar {
        height: 3px;
        background: #4B5563;
        margin: 5px 0;
    }
    
    .denominator {
        color: #0EA5E9;
    }
    
    .digit-sum {
        font-size: 18px;
        color: #6B7280;
        margin-top: 20px;
    }
    
    .factor-tree-container {
        margin: 30px 0;
    }
    
    .factor-node {
        display: inline-block;
        padding: 15px 25px;
        background: #F3F4F6;
        border: 2px solid #D1D5DB;
        border-radius: 8px;
        font-size: 24px;
        font-weight: bold;
        margin: 10px;
    }
    
    .factor-node.root {
        background: #EDE9FE;
        border-color: #7C3AED;
        color: #5B21B6;
    }
    
    .factor-buttons {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 20px;
    }
    
    .no-animations * {
        animation: none !important;
        transition: none !important;
    }
    
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
`;
document.head.appendChild(style);

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