// Accessibility Manager for Number Sense 3s
export class AccessibilityManager {
    constructor() {
        this.settings = {
            highContrast: false,
            largeText: false,
            reduceMotion: false,
            screenReaderMode: false,
            keyboardNavigation: true,
            focusIndicators: true,
            colorBlindMode: 'none' // none, protanopia, deuteranopia, tritanopia
        };
        
        this.announcer = null;
        this.focusTrap = null;
        this.keyboardShortcuts = new Map();
        this.initializeAnnouncer();
    }

    initialize() {
        // Check system preferences
        this.detectSystemPreferences();
        
        // Setup keyboard navigation
        this.setupKeyboardNavigation();
        
        // Setup ARIA live regions
        this.setupAriaRegions();
        
        // Apply saved settings
        this.loadSettings();
        
        // Setup focus management
        this.setupFocusManagement();
        
        console.log('Accessibility features initialized');
    }

    detectSystemPreferences() {
        // Check for prefers-reduced-motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.settings.reduceMotion = true;
            this.applyReducedMotion();
        }

        // Check for prefers-contrast
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            this.settings.highContrast = true;
            this.applyHighContrast();
        }

        // Check for prefers-color-scheme
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode');
        }

        // Listen for changes
        window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
            this.settings.reduceMotion = e.matches;
            this.applyReducedMotion();
        });

        window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
            this.settings.highContrast = e.matches;
            this.applyHighContrast();
        });
    }

    setupKeyboardNavigation() {
        // Define keyboard shortcuts
        this.keyboardShortcuts.set('Escape', () => this.closeModals());
        this.keyboardShortcuts.set('h', () => this.showHelp());
        this.keyboardShortcuts.set('?', () => this.showKeyboardShortcuts());
        this.keyboardShortcuts.set('1', () => this.switchMode('identify'));
        this.keyboardShortcuts.set('2', () => this.switchMode('multiply'));
        this.keyboardShortcuts.set('3', () => this.switchMode('patterns'));
        this.keyboardShortcuts.set('4', () => this.switchMode('skip-count'));
        this.keyboardShortcuts.set('5', () => this.switchMode('factor-tree'));
        this.keyboardShortcuts.set('6', () => this.switchMode('chain'));
        this.keyboardShortcuts.set('7', () => this.switchMode('fractions'));
        this.keyboardShortcuts.set('s', () => this.openSettings());
        this.keyboardShortcuts.set('p', () => this.openProfile());
        this.keyboardShortcuts.set('Tab', (e) => this.handleTabNavigation(e));
        this.keyboardShortcuts.set('Enter', (e) => this.handleEnterKey(e));
        this.keyboardShortcuts.set('Space', (e) => this.handleSpaceKey(e));
        this.keyboardShortcuts.set('ArrowUp', (e) => this.navigateOptions(e, -1));
        this.keyboardShortcuts.set('ArrowDown', (e) => this.navigateOptions(e, 1));
        this.keyboardShortcuts.set('ArrowLeft', (e) => this.navigateTabs(e, -1));
        this.keyboardShortcuts.set('ArrowRight', (e) => this.navigateTabs(e, 1));

        // Add global keyboard listener
        document.addEventListener('keydown', (e) => {
            // Skip if user is typing in an input
            if (this.isTyping(e.target)) {
                return;
            }

            const handler = this.keyboardShortcuts.get(e.key);
            if (handler) {
                handler(e);
            }
        });

        // Add skip links
        this.addSkipLinks();
    }

    setupAriaRegions() {
        // Create screen reader announcer
        this.announcer = document.createElement('div');
        this.announcer.setAttribute('role', 'status');
        this.announcer.setAttribute('aria-live', 'polite');
        this.announcer.setAttribute('aria-atomic', 'true');
        this.announcer.className = 'sr-only';
        document.body.appendChild(this.announcer);

        // Create alert announcer for important messages
        this.alertAnnouncer = document.createElement('div');
        this.alertAnnouncer.setAttribute('role', 'alert');
        this.alertAnnouncer.setAttribute('aria-live', 'assertive');
        this.alertAnnouncer.setAttribute('aria-atomic', 'true');
        this.alertAnnouncer.className = 'sr-only';
        document.body.appendChild(this.alertAnnouncer);

        // Label main regions
        this.labelMainRegions();
    }

    labelMainRegions() {
        // Add ARIA landmarks
        const header = document.querySelector('.app-header');
        if (header) header.setAttribute('role', 'banner');

        const nav = document.querySelector('.nav-tabs');
        if (nav) nav.setAttribute('role', 'navigation');

        const main = document.querySelector('.game-area');
        if (main) main.setAttribute('role', 'main');

        const footer = document.querySelector('.footer');
        if (footer) footer.setAttribute('role', 'contentinfo');

        // Add ARIA labels
        const statsPanel = document.querySelector('.stats-dashboard');
        if (statsPanel) {
            statsPanel.setAttribute('role', 'region');
            statsPanel.setAttribute('aria-label', 'Game Statistics');
        }

        const achievementsPanel = document.querySelector('.achievements-panel');
        if (achievementsPanel) {
            achievementsPanel.setAttribute('role', 'region');
            achievementsPanel.setAttribute('aria-label', 'Achievements');
        }

        const insightsPanel = document.querySelector('.insights-panel');
        if (insightsPanel) {
            insightsPanel.setAttribute('role', 'region');
            insightsPanel.setAttribute('aria-label', 'Learning Insights');
        }
    }

    setupFocusManagement() {
        // Track focus for better navigation
        let lastFocusedElement = null;

        document.addEventListener('focusin', (e) => {
            lastFocusedElement = e.target;
            
            // Add focus indicator class
            if (this.settings.focusIndicators) {
                e.target.classList.add('focused');
            }
        });

        document.addEventListener('focusout', (e) => {
            // Remove focus indicator class
            e.target.classList.remove('focused');
        });

        // Restore focus when modals close
        this.restoreFocus = () => {
            if (lastFocusedElement && lastFocusedElement.focus) {
                lastFocusedElement.focus();
            }
        };
    }

    addSkipLinks() {
        const skipLinksContainer = document.createElement('div');
        skipLinksContainer.className = 'skip-links';
        skipLinksContainer.innerHTML = `
            <a href="#main-content" class="skip-link">Skip to main content</a>
            <a href="#navigation" class="skip-link">Skip to navigation</a>
            <a href="#stats" class="skip-link">Skip to statistics</a>
        `;
        document.body.insertBefore(skipLinksContainer, document.body.firstChild);
    }

    initializeAnnouncer() {
        // Initialize the screen reader announcer
        this.announceQueue = [];
        this.isAnnouncing = false;
    }

    announce(message, priority = 'polite') {
        if (!message) return;

        const announcer = priority === 'assertive' ? this.alertAnnouncer : this.announcer;
        
        if (announcer) {
            // Clear previous announcement
            announcer.textContent = '';
            
            // Use setTimeout to ensure screen reader picks up the change
            setTimeout(() => {
                announcer.textContent = message;
                
                // Clear after announcement
                setTimeout(() => {
                    announcer.textContent = '';
                }, 2000);
            }, 100);
        }

        // Also log to console for debugging
        console.log(`[A11y Announcement]: ${message}`);
    }

    announceQuestion(question) {
        let message = '';
        
        switch (question.type) {
            case 'identify':
                message = `Is ${question.number} a multiple of 3? Press Y for yes, N for no.`;
                break;
            case 'multiply':
                message = `What is 3 times ${question.multiplier}? Enter your answer.`;
                break;
            case 'patterns':
                message = `Complete the pattern: ${question.sequence.join(', ')}. What comes next?`;
                break;
            default:
                message = 'New question ready.';
        }
        
        this.announce(message);
    }

    announceResult(correct, explanation) {
        const message = correct 
            ? `Correct! ${explanation || 'Well done!'}` 
            : `Incorrect. ${explanation || 'Try again!'}`;
        
        this.announce(message, correct ? 'polite' : 'assertive');
    }

    announceAchievement(achievement) {
        this.announce(`Achievement unlocked: ${achievement.name}. ${achievement.description}`, 'assertive');
    }

    applyHighContrast() {
        if (this.settings.highContrast) {
            document.body.classList.add('high-contrast');
            this.announce('High contrast mode enabled');
        } else {
            document.body.classList.remove('high-contrast');
            this.announce('High contrast mode disabled');
        }
    }

    applyLargeText() {
        if (this.settings.largeText) {
            document.body.classList.add('large-text');
            this.announce('Large text enabled');
        } else {
            document.body.classList.remove('large-text');
            this.announce('Large text disabled');
        }
    }

    applyReducedMotion() {
        if (this.settings.reduceMotion) {
            document.body.classList.add('reduce-motion');
            // Disable all animations
            const style = document.createElement('style');
            style.id = 'reduce-motion-styles';
            style.textContent = `
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                    scroll-behavior: auto !important;
                }
            `;
            document.head.appendChild(style);
            this.announce('Animations disabled');
        } else {
            document.body.classList.remove('reduce-motion');
            const style = document.getElementById('reduce-motion-styles');
            if (style) style.remove();
            this.announce('Animations enabled');
        }
    }

    applyColorBlindMode(mode) {
        // Remove existing color blind classes
        document.body.classList.remove('protanopia', 'deuteranopia', 'tritanopia');
        
        if (mode && mode !== 'none') {
            document.body.classList.add(mode);
            
            // Apply color filters
            const filters = {
                protanopia: 'url(#protanopia-filter)',
                deuteranopia: 'url(#deuteranopia-filter)',
                tritanopia: 'url(#tritanopia-filter)'
            };
            
            document.body.style.filter = filters[mode] || '';
            this.announce(`Color blind mode enabled: ${mode}`);
        } else {
            document.body.style.filter = '';
            this.announce('Color blind mode disabled');
        }
        
        this.settings.colorBlindMode = mode;
    }

    createColorBlindFilters() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.display = 'none';
        svg.innerHTML = `
            <defs>
                <!-- Protanopia filter -->
                <filter id="protanopia-filter">
                    <feColorMatrix type="matrix" values="
                        0.567, 0.433, 0,     0, 0
                        0.558, 0.442, 0,     0, 0
                        0,     0.242, 0.758, 0, 0
                        0,     0,     0,     1, 0"/>
                </filter>
                
                <!-- Deuteranopia filter -->
                <filter id="deuteranopia-filter">
                    <feColorMatrix type="matrix" values="
                        0.625, 0.375, 0,   0, 0
                        0.7,   0.3,   0,   0, 0
                        0,     0.3,   0.7, 0, 0
                        0,     0,     0,   1, 0"/>
                </filter>
                
                <!-- Tritanopia filter -->
                <filter id="tritanopia-filter">
                    <feColorMatrix type="matrix" values="
                        0.95, 0.05,  0,     0, 0
                        0,    0.433, 0.567, 0, 0
                        0,    0.475, 0.525, 0, 0
                        0,    0,     0,     1, 0"/>
                </filter>
            </defs>
        `;
        document.body.appendChild(svg);
    }

    handleTabNavigation(e) {
        // Enhanced tab navigation
        const focusableElements = this.getFocusableElements();
        const currentIndex = focusableElements.indexOf(document.activeElement);
        
        if (e.shiftKey) {
            // Backward navigation
            if (currentIndex > 0) {
                focusableElements[currentIndex - 1].focus();
                e.preventDefault();
            }
        } else {
            // Forward navigation
            if (currentIndex < focusableElements.length - 1) {
                focusableElements[currentIndex + 1].focus();
                e.preventDefault();
            }
        }
    }

    handleEnterKey(e) {
        const target = e.target;
        
        // Activate buttons and links
        if (target.matches('button, a, [role="button"]')) {
            target.click();
            e.preventDefault();
        }
        
        // Submit forms
        if (target.matches('input') && target.form) {
            const submitBtn = target.form.querySelector('[type="submit"]');
            if (submitBtn) submitBtn.click();
        }
    }

    handleSpaceKey(e) {
        const target = e.target;
        
        // Activate buttons
        if (target.matches('button, [role="button"]')) {
            target.click();
            e.preventDefault();
        }
        
        // Toggle checkboxes
        if (target.matches('input[type="checkbox"]')) {
            target.checked = !target.checked;
            target.dispatchEvent(new Event('change'));
            e.preventDefault();
        }
    }

    navigateOptions(e, direction) {
        const container = e.target.closest('[role="listbox"], .options-container');
        if (!container) return;
        
        const options = Array.from(container.querySelectorAll('[role="option"], .option'));
        const currentIndex = options.indexOf(document.activeElement);
        const nextIndex = Math.max(0, Math.min(options.length - 1, currentIndex + direction));
        
        if (options[nextIndex]) {
            options[nextIndex].focus();
            e.preventDefault();
        }
    }

    navigateTabs(e, direction) {
        const tablist = e.target.closest('[role="tablist"], .nav-tabs');
        if (!tablist) return;
        
        const tabs = Array.from(tablist.querySelectorAll('[role="tab"], .nav-tab'));
        const currentIndex = tabs.indexOf(document.activeElement);
        let nextIndex = currentIndex + direction;
        
        // Wrap around
        if (nextIndex < 0) nextIndex = tabs.length - 1;
        if (nextIndex >= tabs.length) nextIndex = 0;
        
        if (tabs[nextIndex]) {
            tabs[nextIndex].focus();
            tabs[nextIndex].click();
            e.preventDefault();
        }
    }

    getFocusableElements() {
        const selector = `
            a[href],
            button:not([disabled]),
            input:not([disabled]),
            select:not([disabled]),
            textarea:not([disabled]),
            [tabindex]:not([tabindex="-1"]),
            [contenteditable]
        `;
        
        return Array.from(document.querySelectorAll(selector))
            .filter(el => el.offsetParent !== null); // Filter out hidden elements
    }

    isTyping(element) {
        return element.matches('input, textarea, [contenteditable]');
    }

    trapFocus(container) {
        const focusableElements = Array.from(
            container.querySelectorAll(this.getFocusableSelector())
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        // Store for cleanup
        this.focusTrap = (e) => {
            if (e.key !== 'Tab') return;
            
            if (e.shiftKey && document.activeElement === firstElement) {
                lastElement.focus();
                e.preventDefault();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                firstElement.focus();
                e.preventDefault();
            }
        };
        
        container.addEventListener('keydown', this.focusTrap);
        
        // Focus first element
        firstElement.focus();
    }

    releaseFocusTrap(container) {
        if (this.focusTrap) {
            container.removeEventListener('keydown', this.focusTrap);
            this.focusTrap = null;
        }
        
        // Restore focus
        this.restoreFocus();
    }

    getFocusableSelector() {
        return `
            a[href]:not([disabled]),
            button:not([disabled]),
            textarea:not([disabled]),
            input:not([disabled]),
            select:not([disabled]),
            [tabindex]:not([tabindex="-1"]):not([disabled])
        `;
    }

    // Modal management
    closeModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display !== 'none') {
                modal.style.display = 'none';
                this.releaseFocusTrap(modal);
                this.announce('Modal closed');
            }
        });
    }

    openSettings() {
        const modal = document.getElementById('settings-modal');
        if (modal) {
            modal.style.display = 'block';
            this.trapFocus(modal);
            this.announce('Settings opened');
        }
    }

    openProfile() {
        const modal = document.getElementById('profile-modal');
        if (modal) {
            modal.style.display = 'block';
            this.trapFocus(modal);
            this.announce('Profile opened');
        }
    }

    showHelp() {
        this.announce('Help: Press question mark for keyboard shortcuts, numbers 1-7 to switch game modes, H for hints, S for settings, P for profile, Escape to close dialogs.');
    }

    showKeyboardShortcuts() {
        const shortcuts = [
            '1-7: Switch game modes',
            'Y/N: Answer yes/no questions',
            'Enter: Submit answer',
            'H: Get hint',
            'S: Open settings',
            'P: Open profile',
            'Escape: Close dialogs',
            'Tab: Navigate forward',
            'Shift+Tab: Navigate backward',
            'Arrow keys: Navigate options'
        ];
        
        this.announce('Keyboard shortcuts: ' + shortcuts.join(', '));
    }

    switchMode(mode) {
        const button = document.querySelector(`[data-mode="${mode}"]`);
        if (button) {
            button.click();
            this.announce(`Switched to ${mode} mode`);
        }
    }

    updateSetting(setting, value) {
        this.settings[setting] = value;
        
        switch (setting) {
            case 'highContrast':
                this.applyHighContrast();
                break;
            case 'largeText':
                this.applyLargeText();
                break;
            case 'reduceMotion':
                this.applyReducedMotion();
                break;
            case 'colorBlindMode':
                this.applyColorBlindMode(value);
                break;
        }
        
        this.saveSettings();
    }

    loadSettings() {
        const saved = localStorage.getItem('number_sense_3s_accessibility');
        if (saved) {
            try {
                const settings = JSON.parse(saved);
                Object.assign(this.settings, settings);
                
                // Apply loaded settings
                if (this.settings.highContrast) this.applyHighContrast();
                if (this.settings.largeText) this.applyLargeText();
                if (this.settings.reduceMotion) this.applyReducedMotion();
                if (this.settings.colorBlindMode !== 'none') {
                    this.applyColorBlindMode(this.settings.colorBlindMode);
                }
            } catch (e) {
                console.error('Failed to load accessibility settings:', e);
            }
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('number_sense_3s_accessibility', JSON.stringify(this.settings));
        } catch (e) {
            console.error('Failed to save accessibility settings:', e);
        }
    }

    cleanup() {
        // Remove event listeners
        if (this.focusTrap) {
            document.removeEventListener('keydown', this.focusTrap);
        }
        
        // Remove created elements
        if (this.announcer) this.announcer.remove();
        if (this.alertAnnouncer) this.alertAnnouncer.remove();
        
        // Clear styles
        const reduceMotionStyle = document.getElementById('reduce-motion-styles');
        if (reduceMotionStyle) reduceMotionStyle.remove();
    }
}

export default AccessibilityManager;