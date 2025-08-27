export interface ValidationError {
  field: string
  message: string
}

export class ValidationException extends Error {
  errors: ValidationError[]

  constructor(errors: ValidationError[]) {
    super('Validation failed')
    this.errors = errors
  }
}

export function validateRequired(value: unknown, fieldName: string): ValidationError | null {
  if (value === null || value === undefined || value === '') {
    return { field: fieldName, message: `${fieldName} is required` }
  }
  return null
}

export function validateEmail(email: string): ValidationError | null {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    return { field: 'email', message: 'Invalid email format' }
  }
  return null
}

export function validateUrl(url: string, fieldName: string): ValidationError | null {
  try {
    new URL(url)
    return null
  } catch {
    return { field: fieldName, message: `${fieldName} must be a valid URL` }
  }
}

export function validateLength(
  value: string, 
  min: number, 
  max: number, 
  fieldName: string
): ValidationError | null {
  if (value.length < min) {
    return { field: fieldName, message: `${fieldName} must be at least ${min} characters` }
  }
  if (value.length > max) {
    return { field: fieldName, message: `${fieldName} must not exceed ${max} characters` }
  }
  return null
}

export function validateEnum<T>(
  value: string, 
  allowedValues: T[], 
  fieldName: string
): ValidationError | null {
  if (!allowedValues.includes(value as T)) {
    return { 
      field: fieldName, 
      message: `${fieldName} must be one of: ${allowedValues.join(', ')}` 
    }
  }
  return null
}

export function createValidationErrorResponse(errors: ValidationError[]): Response {
  return new Response(
    JSON.stringify({ 
      error: 'Validation failed', 
      details: errors 
    }),
    { 
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    }
  )
}