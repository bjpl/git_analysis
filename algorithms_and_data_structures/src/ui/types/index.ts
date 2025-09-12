/**
 * Core UI Types and Interfaces
 */

export interface Theme {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  background: string;
  foreground: string;
  border: string;
  accent: string;
  muted: string;
}

export interface Position {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface Bounds extends Position, Size {}

export interface StyleOptions {
  color?: string;
  backgroundColor?: string;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  inverse?: boolean;
}

export interface ComponentProps {
  theme?: Partial<Theme>;
  visible?: boolean;
  position?: Partial<Position>;
  size?: Partial<Size>;
  style?: StyleOptions;
  className?: string;
  onKeyPress?: (key: string, matches: any) => void;
  onFocus?: () => void;
  onBlur?: () => void;
}

export interface InputProps extends ComponentProps {
  value?: string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  onChange?: (value: string) => void;
  onSubmit?: (value: string) => void;
  onCancel?: () => void;
}

export interface ValidationRule {
  test: (value: string) => boolean;
  message: string;
}

export interface SelectOption<T = any> {
  label: string;
  value: T;
  disabled?: boolean;
  icon?: string;
  description?: string;
}

export interface TableColumn<T = any> {
  key: keyof T;
  label: string;
  width?: number;
  sortable?: boolean;
  filterable?: boolean;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T, index: number) => string;
}

export interface TableData<T = any> {
  columns: TableColumn<T>[];
  rows: T[];
}

export interface AlertType {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  persistent?: boolean;
}

export interface GridCell {
  content: string;
  style?: StyleOptions;
  span?: number;
}

export interface GridRow {
  cells: GridCell[];
  height?: number;
}