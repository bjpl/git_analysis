import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Setup MSW server for node environment (unit/integration tests)
export const server = setupServer(...handlers);

// Enhanced server controls for testing
export const resetHandlers = () => server.resetHandlers(...handlers);
export const restoreHandlers = () => server.restoreHandlers();
export const close = () => server.close();