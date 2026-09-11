import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function isObject(value: unknown) {
  if (typeof value === "object" && !Array.isArray(value) && value !== null)
    return true;
  return false;
}
