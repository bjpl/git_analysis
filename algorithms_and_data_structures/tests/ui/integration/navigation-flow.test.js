/**
 * Navigation Flow Integration Tests
 * Tests for complete navigation workflows and user journeys
 */

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';

describe('Navigation Flow Integration Tests', () => {
    let navigationSystem;
    let mockState;
    let eventLog;

    beforeEach(() => {
        eventLog = [];
        mockState = {
            currentScreen: 'main-menu',
            currentIndex: 0,
            history: [],
            breadcrumbs: ['Home'],
            canGoBack: false,
            isLoading: false,
            error: null
        };

        navigationSystem = {
            state: mockState,
            screens: {
                'main-menu': {
                    title: 'Main Menu',
                    items: [
                        { id: 'arrays', label: 'Arrays', screen: 'arrays-menu' },
                        { id: 'linkedlists', label: 'Linked Lists', screen: 'linkedlists-menu' },
                        { id: 'trees', label: 'Trees', screen: 'trees-menu' },
                        { id: 'graphs', label: 'Graphs', screen: 'graphs-menu' },
                        { id: 'algorithms', label: 'Algorithms', screen: 'algorithms-menu' },
                        { id: 'practice', label: 'Practice Problems', screen: 'practice-menu' },
                        { id: 'progress', label: 'Progress', screen: 'progress-view' },
                        { id: 'settings', label: 'Settings', screen: 'settings-menu' }
                    ]
                },
                'arrays-menu': {
                    title: 'Arrays',
                    parent: 'main-menu',
                    items: [
                        { id: 'basics', label: 'Array Basics', screen: 'array-basics' },
                        { id: 'operations', label: 'Array Operations', screen: 'array-operations' },
                        { id: 'practice', label: 'Array Practice', screen: 'array-practice' }
                    ]
                },
                'array-basics': {
                    title: 'Array Basics',
                    parent: 'arrays-menu',
                    type: 'lesson',
                    content: 'Arrays are fundamental data structures...'
                },
                'practice-menu': {
                    title: 'Practice Problems',
                    parent: 'main-menu',
                    items: [
                        { id: 'easy', label: 'Easy Problems', screen: 'practice-easy' },
                        { id: 'medium', label: 'Medium Problems', screen: 'practice-medium' },
                        { id: 'hard', label: 'Hard Problems', screen: 'practice-hard' }
                    ]
                }
            },
            navigate: function(screenId, addToHistory = true) {
                eventLog.push({ action: 'navigate', from: this.state.currentScreen, to: screenId });
                
                if (!this.screens[screenId]) {
                    this.state.error = `Screen '${screenId}' not found`;
                    return false;
                }

                if (addToHistory && this.state.currentScreen !== screenId) {
                    this.state.history.push(this.state.currentScreen);
                }

                this.state.currentScreen = screenId;
                this.state.currentIndex = 0;
                this.state.canGoBack = this.state.history.length > 0;
                this.state.error = null;
                
                this.updateBreadcrumbs();
                return true;
            },
            goBack: function() {
                if (this.state.history.length > 0) {
                    const previousScreen = this.state.history.pop();
                    eventLog.push({ action: 'go-back', from: this.state.currentScreen, to: previousScreen });
                    
                    this.state.currentScreen = previousScreen;
                    this.state.currentIndex = 0;
                    this.state.canGoBack = this.state.history.length > 0;
                    
                    this.updateBreadcrumbs();
                    return true;
                }
                return false;
            },
            selectCurrentItem: function() {
                const screen = this.screens[this.state.currentScreen];
                if (screen.items && screen.items[this.state.currentIndex]) {
                    const item = screen.items[this.state.currentIndex];
                    eventLog.push({ action: 'select-item', item: item.id, screen: item.screen });
                    return this.navigate(item.screen);
                }
                return false;
            },
            updateBreadcrumbs: function() {
                const breadcrumbs = ['Home'];
                let currentScreen = this.screens[this.state.currentScreen];
                const path = [];
                
                while (currentScreen && currentScreen.parent) {
                    path.unshift(currentScreen.title);
                    currentScreen = this.screens[currentScreen.parent];
                }
                
                this.state.breadcrumbs = breadcrumbs.concat(path);
            },
            getCurrentScreen: function() {
                return this.screens[this.state.currentScreen];
            }
        };
    });

    describe('Basic Navigation Flows', () => {
        test('should navigate from main menu to arrays submenu', () => {
            const success = navigationSystem.navigate('arrays-menu');
            
            expect(success).toBe(true);
            expect(navigationSystem.state.currentScreen).toBe('arrays-menu');
            expect(navigationSystem.state.history).toContain('main-menu');
            expect(navigationSystem.state.canGoBack).toBe(true);
        });

        test('should maintain navigation history correctly', () => {
            navigationSystem.navigate('arrays-menu');
            navigationSystem.navigate('array-basics');
            
            expect(navigationSystem.state.history).toEqual(['main-menu', 'arrays-menu']);
            expect(navigationSystem.state.canGoBack).toBe(true);
        });

        test('should go back through navigation history', () => {
            navigationSystem.navigate('arrays-menu');
            navigationSystem.navigate('array-basics');
            
            const backResult1 = navigationSystem.goBack();
            expect(backResult1).toBe(true);
            expect(navigationSystem.state.currentScreen).toBe('arrays-menu');
            
            const backResult2 = navigationSystem.goBack();
            expect(backResult2).toBe(true);
            expect(navigationSystem.state.currentScreen).toBe('main-menu');
            expect(navigationSystem.state.canGoBack).toBe(false);
        });

        test('should handle navigation to non-existent screen', () => {
            const result = navigationSystem.navigate('non-existent');
            
            expect(result).toBe(false);
            expect(navigationSystem.state.error).toContain('Screen \'non-existent\' not found');
            expect(navigationSystem.state.currentScreen).toBe('main-menu'); // Should remain unchanged
        });
    });

    describe('Menu Item Selection Flows', () => {
        test('should select menu items and navigate to target screens', () => {
            navigationSystem.state.currentIndex = 0; // Arrays item
            const result = navigationSystem.selectCurrentItem();
            
            expect(result).toBe(true);
            expect(navigationSystem.state.currentScreen).toBe('arrays-menu');
            expect(eventLog.some(e => e.action === 'select-item' && e.item === 'arrays')).toBe(true);
        });

        test('should handle selection when no items exist', () => {
            navigationSystem.navigate('array-basics'); // Lesson screen with no items
            const result = navigationSystem.selectCurrentItem();
            
            expect(result).toBe(false);
        });

        test('should handle selection beyond available items', () => {
            navigationSystem.state.currentIndex = 999; // Beyond available items
            const result = navigationSystem.selectCurrentItem();
            
            expect(result).toBe(false);
        });
    });

    describe('Complete User Journey Flows', () => {
        test('should complete full learning path navigation', () => {
            // Start at main menu -> Arrays -> Array Basics
            navigationSystem.state.currentIndex = 0;
            navigationSystem.selectCurrentItem(); // Go to arrays-menu
            
            navigationSystem.state.currentIndex = 0;
            navigationSystem.selectCurrentItem(); // Go to array-basics
            
            expect(navigationSystem.state.currentScreen).toBe('array-basics');
            expect(navigationSystem.state.history).toEqual(['main-menu', 'arrays-menu']);
            
            // Navigate back through the path
            navigationSystem.goBack(); // Back to arrays-menu
            navigationSystem.goBack(); // Back to main-menu
            
            expect(navigationSystem.state.currentScreen).toBe('main-menu');
            expect(navigationSystem.state.history).toHaveLength(0);
        });

        test('should handle practice problem workflow', () => {
            // Navigate to practice problems
            navigationSystem.state.currentIndex = 5; // Practice Problems
            navigationSystem.selectCurrentItem();
            
            expect(navigationSystem.state.currentScreen).toBe('practice-menu');
            
            // Select difficulty level
            navigationSystem.state.currentIndex = 1; // Medium Problems
            navigationSystem.selectCurrentItem();
            
            expect(navigationSystem.state.currentScreen).toBe('practice-medium');
            
            // Verify full path is tracked
            expect(navigationSystem.state.history).toEqual(['main-menu', 'practice-menu']);
        });

        test('should maintain consistent state during complex navigation', () => {
            const navigationSteps = [
                { action: 'select', index: 0 }, // Arrays
                { action: 'select', index: 1 }, // Array Operations
                { action: 'back' },             // Back to Arrays menu
                { action: 'select', index: 2 }, // Array Practice
                { action: 'back' },             // Back to Arrays menu
                { action: 'back' }              // Back to Main menu
            ];

            navigationSteps.forEach((step, i) => {
                if (step.action === 'select') {
                    navigationSystem.state.currentIndex = step.index;
                    navigationSystem.selectCurrentItem();
                } else if (step.action === 'back') {
                    navigationSystem.goBack();
                }
                
                // Verify state consistency at each step
                expect(navigationSystem.state.currentIndex).toBe(0); // Should reset on navigation
                expect(navigationSystem.state.error).toBeNull();
            });
            
            expect(navigationSystem.state.currentScreen).toBe('main-menu');
            expect(navigationSystem.state.canGoBack).toBe(false);
        });
    });

    describe('Breadcrumb Navigation', () => {
        test('should update breadcrumbs correctly during navigation', () => {
            navigationSystem.navigate('arrays-menu');
            expect(navigationSystem.state.breadcrumbs).toEqual(['Home', 'Arrays']);
            
            navigationSystem.navigate('array-basics');
            expect(navigationSystem.state.breadcrumbs).toEqual(['Home', 'Arrays', 'Array Basics']);
        });

        test('should maintain breadcrumbs when going back', () => {
            navigationSystem.navigate('arrays-menu');
            navigationSystem.navigate('array-basics');
            navigationSystem.goBack();
            
            expect(navigationSystem.state.breadcrumbs).toEqual(['Home', 'Arrays']);
        });

        test('should handle deep navigation breadcrumbs', () => {
            navigationSystem.navigate('practice-menu');
            navigationSystem.navigate('practice-medium');
            
            expect(navigationSystem.state.breadcrumbs).toEqual(['Home', 'Practice Problems']);
        });
    });

    describe('Error Handling in Navigation', () => {
        test('should handle navigation errors gracefully', () => {
            const initialScreen = navigationSystem.state.currentScreen;
            
            navigationSystem.navigate('invalid-screen');
            
            expect(navigationSystem.state.currentScreen).toBe(initialScreen);
            expect(navigationSystem.state.error).toBeTruthy();
        });

        test('should recover from navigation errors', () => {
            navigationSystem.navigate('invalid-screen');
            expect(navigationSystem.state.error).toBeTruthy();
            
            navigationSystem.navigate('arrays-menu');
            expect(navigationSystem.state.error).toBeNull();
            expect(navigationSystem.state.currentScreen).toBe('arrays-menu');
        });

        test('should handle back navigation when no history exists', () => {
            const result = navigationSystem.goBack();
            
            expect(result).toBe(false);
            expect(navigationSystem.state.currentScreen).toBe('main-menu');
        });
    });

    describe('Navigation Event Logging', () => {
        test('should log all navigation events', () => {
            navigationSystem.navigate('arrays-menu');
            navigationSystem.state.currentIndex = 0;
            navigationSystem.selectCurrentItem();
            navigationSystem.goBack();
            
            expect(eventLog).toHaveLength(3);
            expect(eventLog[0]).toEqual({ action: 'navigate', from: 'main-menu', to: 'arrays-menu' });
            expect(eventLog[1]).toEqual({ action: 'select-item', item: 'basics', screen: 'array-basics' });
            expect(eventLog[2]).toEqual({ action: 'go-back', from: 'array-basics', to: 'arrays-menu' });
        });

        test('should track user journey patterns', () => {
            // Simulate a typical learning session
            navigationSystem.state.currentIndex = 0;
            navigationSystem.selectCurrentItem(); // Arrays
            navigationSystem.state.currentIndex = 0;
            navigationSystem.selectCurrentItem(); // Array Basics
            navigationSystem.goBack();
            navigationSystem.state.currentIndex = 1;
            navigationSystem.selectCurrentItem(); // Array Operations
            
            const navigationEvents = eventLog.filter(e => e.action === 'navigate' || e.action === 'select-item');
            expect(navigationEvents).toHaveLength(4);
            
            // Verify the learning path
            const path = navigationEvents.map(e => e.screen || e.to);
            expect(path).toEqual(['arrays-menu', 'array-basics', 'array-operations']);
        });
    });

    describe('Screen State Management', () => {
        test('should properly initialize screen state', () => {
            const screen = navigationSystem.getCurrentScreen();
            
            expect(screen).toBeDefined();
            expect(screen.title).toBe('Main Menu');
            expect(screen.items).toHaveLength(8);
        });

        test('should handle different screen types', () => {
            navigationSystem.navigate('array-basics');
            const lessonScreen = navigationSystem.getCurrentScreen();
            
            expect(lessonScreen.type).toBe('lesson');
            expect(lessonScreen.content).toBeDefined();
            expect(lessonScreen.items).toBeUndefined();
        });

        test('should maintain screen relationships', () => {
            navigationSystem.navigate('arrays-menu');
            const screen = navigationSystem.getCurrentScreen();
            
            expect(screen.parent).toBe('main-menu');
            expect(screen.title).toBe('Arrays');
        });
    });
});