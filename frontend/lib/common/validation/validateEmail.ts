export function validateEmail(email: string) {
  let errors: string[] = [];

  if (!email.includes("@")) {
    return ["Malformed email contains no @ symbol"];
  }

  return errors;
}
