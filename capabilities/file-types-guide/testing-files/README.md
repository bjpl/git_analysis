# Testing Files Guide

## Overview
Testing files ensure code quality, prevent regressions, and document expected behavior. This guide covers essential file types for comprehensive testing strategies.

## File Types Reference

| **Test Type** | **Core Files** | **Supporting Files** | **Purpose** |
|--------------|----------------|---------------------|------------|
| **Test Suites** | `.test.js`, `.spec.ts` | `.test.py`, `_test.go` | Unit and integration testing |
| **Test Configs** | `jest.config.js`, `karma.conf.js` | `pytest.ini`, `.mocharc.json` | Test framework configuration |
| **Mock Data** | `.json`, `.js` | `.yml`, `.csv` | Test fixtures and stubs |

## Use Cases & Examples

### Unit Test Suites
**Best For:** Function testing, component testing, isolated logic
```javascript
// userService.test.js - Jest unit test
const UserService = require('./userService');
const UserRepository = require('./userRepository');

jest.mock('./userRepository');

describe('UserService', () => {
  let userService;
  let mockRepository;

  beforeEach(() => {
    mockRepository = new UserRepository();
    userService = new UserService(mockRepository);
  });

  describe('createUser', () => {
    it('should create a user with valid data', async () => {
      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'SecurePass123!'
      };

      const expectedUser = {
        id: '123',
        ...userData,
        password: undefined,
        createdAt: new Date()
      };

      mockRepository.create.mockResolvedValue(expectedUser);

      const result = await userService.createUser(userData);

      expect(mockRepository.create).toHaveBeenCalledWith(
        expect.objectContaining({
          email: userData.email,
          username: userData.username
        })
      );
      expect(result).toEqual(expectedUser);
    });

    it('should throw error for duplicate email', async () => {
      mockRepository.create.mockRejectedValue(
        new Error('Duplicate email')
      );

      await expect(
        userService.createUser({ email: 'existing@example.com' })
      ).rejects.toThrow('Duplicate email');
    });
  });

  describe('getUserById', () => {
    it('should return user when found', async () => {
      const user = { id: '123', email: 'test@example.com' };
      mockRepository.findById.mockResolvedValue(user);

      const result = await userService.getUserById('123');

      expect(result).toEqual(user);
    });

    it('should return null when user not found', async () => {
      mockRepository.findById.mockResolvedValue(null);

      const result = await userService.getUserById('999');

      expect(result).toBeNull();
    });
  });
});
```

**Component Testing (React):**
```typescript
// Button.test.tsx - React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button Component', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant styles', () => {
    render(<Button variant="primary">Primary</Button>);
    const button = screen.getByText('Primary');
    expect(button).toHaveClass('btn-primary');
  });

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByText('Disabled')).toBeDisabled();
  });
});
```
**Example Projects:** Library testing, API testing, component libraries

### Integration Tests
**Best For:** API endpoints, database operations, service interactions
```python
# test_api.py - pytest integration test
import pytest
from fastapi.testclient import TestClient
from app import app
from database import get_test_db

client = TestClient(app)

@pytest.fixture
def test_db():
    """Create test database"""
    db = get_test_db()
    yield db
    db.cleanup()

class TestUserAPI:
    def test_create_user(self, test_db):
        response = client.post(
            "/api/users",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "password" not in data

    def test_get_user(self, test_db):
        # Create user first
        create_response = client.post(
            "/api/users",
            json={"email": "test@example.com", "username": "test"}
        )
        user_id = create_response.json()["id"]

        # Get user
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    def test_update_user(self, test_db):
        # Setup
        user_id = create_test_user()

        # Update
        response = client.put(
            f"/api/users/{user_id}",
            json={"username": "updated"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "updated"

    def test_delete_user(self, test_db):
        user_id = create_test_user()
        
        response = client.delete(f"/api/users/{user_id}")
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 404
```
**Example Projects:** REST API testing, GraphQL testing, microservice testing

### End-to-End Tests
**Best For:** User workflows, critical paths, browser automation
```javascript
// e2e/login.spec.js - Playwright E2E test
const { test, expect } = require('@playwright/test');

test.describe('User Authentication Flow', () => {
  test('successful login redirects to dashboard', async ({ page }) => {
    await page.goto('/login');
    
    // Fill login form
    await page.fill('[data-testid="email"]', 'user@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Wait for redirect
    await page.waitForURL('/dashboard');
    
    // Verify dashboard elements
    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('invalid credentials show error message', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('[data-testid="email"]', 'wrong@example.com');
    await page.fill('[data-testid="password"]', 'wrongpass');
    await page.click('[data-testid="login-button"]');
    
    await expect(page.locator('.error-message')).toContainText(
      'Invalid email or password'
    );
  });

  test('password reset flow', async ({ page }) => {
    await page.goto('/login');
    await page.click('text=Forgot password?');
    
    await page.fill('[data-testid="reset-email"]', 'user@example.com');
    await page.click('[data-testid="reset-button"]');
    
    await expect(page.locator('.success-message')).toContainText(
      'Password reset email sent'
    );
  });
});
```
**Example Projects:** User journey testing, checkout flows, form submissions

### Test Configuration
**Best For:** Test environment setup, coverage settings, test runners
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  transform: {
    '^.+\\.jsx?$': 'babel-jest',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/**/*.test.js',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/test/setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};
```

### Mock Data
**Best For:** Test fixtures, API mocks, sample data
```json
// __mocks__/users.json
{
  "users": [
    {
      "id": "1",
      "email": "admin@example.com",
      "username": "admin",
      "role": "admin",
      "profile": {
        "firstName": "Admin",
        "lastName": "User",
        "avatar": "https://example.com/avatar1.jpg"
      }
    },
    {
      "id": "2",
      "email": "user@example.com",
      "username": "testuser",
      "role": "user",
      "profile": {
        "firstName": "Test",
        "lastName": "User",
        "avatar": "https://example.com/avatar2.jpg"
      }
    }
  ]
}
```

## Best Practices

1. **Test Pyramid:** More unit tests, fewer E2E tests
2. **Isolation:** Tests should not depend on each other
3. **Clarity:** Use descriptive test names
4. **Speed:** Keep tests fast, mock external dependencies
5. **Coverage:** Aim for high coverage but focus on critical paths
6. **Maintenance:** Keep tests updated with code changes

## File Organization Pattern
```
tests/
├── unit/
│   ├── services/
│   └── utils/
├── integration/
│   ├── api/
│   └── database/
├── e2e/
│   ├── auth/
│   └── checkout/
├── fixtures/
│   ├── users.json
│   └── products.json
└── helpers/
    └── testUtils.js
```

## Testing Strategies

### Test-Driven Development (TDD)
```javascript
// 1. Write failing test
test('should calculate discount', () => {
  expect(calculateDiscount(100, 0.1)).toBe(90);
});

// 2. Write minimal code to pass
function calculateDiscount(price, discount) {
  return price * (1 - discount);
}

// 3. Refactor if needed
```

### Snapshot Testing
```javascript
test('renders correctly', () => {
  const tree = renderer
    .create(<Component prop="value" />)
    .toJSON();
  expect(tree).toMatchSnapshot();
});
```

## Performance Considerations
- Parallel test execution
- Test database optimization
- Mock heavy operations
- Use test containers for isolation
- Profile slow tests

## Testing Tools
- **Unit Testing:** Jest, Mocha, pytest, Go testing
- **E2E Testing:** Playwright, Cypress, Selenium
- **API Testing:** Postman, Insomnia, REST Client
- **Performance:** k6, JMeter, Locust
- **Coverage:** Istanbul, Coverage.py, GoCover