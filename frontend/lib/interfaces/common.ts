export interface ValidationErrorProp {
  api_response: boolean;
  error_count: number;
  errors: Record<string, string[]>;
}

export type Result<R, E = ValidationErrorProp> =
  | { ok: true; data: R }
  | { ok: false; error: E };
