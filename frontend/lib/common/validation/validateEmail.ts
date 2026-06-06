export function validateEmail(email: string) {
  let errors: string[] = [];

  if (email.length < 5) {
    return ["Insufficient email provided"];
  }

  if (!email.includes("@")) {
    return ["Malformed email contains no @ symbol"];
  }

  return errors;
}
