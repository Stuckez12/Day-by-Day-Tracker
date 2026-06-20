export interface ValidationErrorProp {
  api_response: boolean;
  error_count: number;
  errors: Record<string, string[]>;
}
