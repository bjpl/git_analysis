/**
 * UI Components Test Suite
 * Tests for individual UI component functionality
 */

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';
import chalk from 'chalk';
import Table from 'cli-table3';
import inquirer from 'inquirer';

// Mock console methods to capture output
let consoleLogs = [];
let mockLog = jest.fn((msg) => consoleLogs.push(msg));
let mockError = jest.fn((msg) => consoleLogs.push(`ERROR: ${msg}`));

describe('UI Components Tests', () => {
    beforeEach(() => {
        consoleLogs = [];
        console.log = mockLog;
        console.error = mockError;
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Console Output Components', () => {
        test('should format headers with chalk colors', () => {
            const header = chalk.cyan.bold('Test Header');
            expect(header).toContain('Test Header');
            expect(typeof header).toBe('string');
        });

        test('should create success messages with green color', () => {
            const success = chalk.green('✓ Success message');
            expect(success).toContain('✓ Success message');
        });

        test('should create error messages with red color', () => {
            const error = chalk.red('✗ Error message');
            expect(error).toContain('✗ Error message');
        });

        test('should create warning messages with yellow color', () => {
            const warning = chalk.yellow('⚠ Warning message');
            expect(warning).toContain('⚠ Warning message');
        });

        test('should create info messages with blue color', () => {
            const info = chalk.blue('ℹ Info message');
            expect(info).toContain('ℹ Info message');
        });
    });

    describe('Table Components', () => {
        test('should create basic table structure', () => {
            const table = new Table({
                head: ['Column 1', 'Column 2', 'Column 3']
            });
            
            expect(table.options.head).toEqual(['Column 1', 'Column 2', 'Column 3']);
        });

        test('should add rows to table', () => {
            const table = new Table();
            table.push(['Row 1 Col 1', 'Row 1 Col 2']);
            table.push(['Row 2 Col 1', 'Row 2 Col 2']);
            
            expect(table.length).toBe(2);
        });

        test('should render table with custom styling', () => {
            const table = new Table({
                head: ['Name', 'Status', 'Progress'],
                style: {
                    head: ['cyan'],
                    border: ['grey']
                }
            });
            
            table.push(['Algorithm 1', 'Complete', '100%']);
            const output = table.toString();
            
            expect(output).toContain('Algorithm 1');
            expect(output).toContain('Complete');
            expect(output).toContain('100%');
        });

        test('should handle empty table gracefully', () => {
            const table = new Table({
                head: ['Empty', 'Table']
            });
            
            const output = table.toString();
            expect(output).toContain('Empty');
            expect(output).toContain('Table');
        });
    });

    describe('Progress Indicators', () => {
        test('should create progress bar component', () => {
            const progress = (current, total) => {
                const percentage = Math.round((current / total) * 100);
                const filled = Math.round((current / total) * 20);
                const bar = '█'.repeat(filled) + '░'.repeat(20 - filled);
                return `[${bar}] ${percentage}%`;
            };

            expect(progress(5, 10)).toContain('50%');
            expect(progress(10, 10)).toContain('100%');
            expect(progress(0, 10)).toContain('0%');
        });

        test('should create spinner component states', () => {
            const spinnerFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
            
            expect(spinnerFrames).toHaveLength(10);
            expect(spinnerFrames[0]).toBe('⠋');
            expect(spinnerFrames[9]).toBe('⠏');
        });
    });

    describe('Menu Components', () => {
        test('should format menu items correctly', () => {
            const menuItems = [
                { key: '1', label: 'Arrays', description: 'Learn about arrays' },
                { key: '2', label: 'Linked Lists', description: 'Learn about linked lists' }
            ];

            const formatMenuItem = (item) => `${item.key}. ${chalk.white.bold(item.label)} - ${chalk.gray(item.description)}`;
            
            const formatted1 = formatMenuItem(menuItems[0]);
            const formatted2 = formatMenuItem(menuItems[1]);
            
            expect(formatted1).toContain('1. Arrays');
            expect(formatted1).toContain('Learn about arrays');
            expect(formatted2).toContain('2. Linked Lists');
            expect(formatted2).toContain('Learn about linked lists');
        });

        test('should handle menu navigation state', () => {
            const menuState = {
                currentIndex: 0,
                items: ['Item 1', 'Item 2', 'Item 3'],
                selectedIndex: null
            };

            // Simulate navigation
            menuState.currentIndex = 1;
            expect(menuState.currentIndex).toBe(1);
            
            // Simulate selection
            menuState.selectedIndex = menuState.currentIndex;
            expect(menuState.selectedIndex).toBe(1);
        });
    });

    describe('Form Components', () => {
        test('should validate input components', () => {
            const validateInput = (input, type = 'text') => {
                switch (type) {
                    case 'number':
                        return !isNaN(Number(input)) && input.trim() !== '';
                    case 'email':
                        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input);
                    case 'text':
                    default:
                        return input.trim().length > 0;
                }
            };

            expect(validateInput('test')).toBe(true);
            expect(validateInput('')).toBe(false);
            expect(validateInput('123', 'number')).toBe(true);
            expect(validateInput('abc', 'number')).toBe(false);
            expect(validateInput('test@example.com', 'email')).toBe(true);
            expect(validateInput('invalid-email', 'email')).toBe(false);
        });

        test('should handle form state management', () => {
            const formState = {
                fields: {
                    name: '',
                    difficulty: 'beginner',
                    topics: []
                },
                errors: {},
                isValid: false
            };

            // Simulate field updates
            formState.fields.name = 'Test User';
            formState.fields.topics = ['arrays', 'sorting'];
            
            expect(formState.fields.name).toBe('Test User');
            expect(formState.fields.topics).toContain('arrays');
            expect(formState.fields.difficulty).toBe('beginner');
        });
    });
});

// Export for use in other test files
export { consoleLogs, mockLog, mockError };
