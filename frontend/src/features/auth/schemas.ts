import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email."),
  password: z.string().min(1, "Password is required."),
});

export const registerSchema = z.object({
  email: z.string().email("Enter a valid email."),
  username: z
    .string()
    .regex(/^[a-zA-Z0-9_]{3,20}$/, "Use 3 to 20 letters, numbers, or underscores."),
  displayName: z.string().trim().min(2, "Use at least 2 characters.").max(40),
  password: z
    .string()
    .min(8, "Use at least 8 characters.")
    .max(72, "Use at most 72 characters.")
    .regex(/[A-Za-z]/, "Include a letter.")
    .regex(/[0-9]/, "Include a number."),
});

export type LoginValues = z.infer<typeof loginSchema>;
export type RegisterValues = z.infer<typeof registerSchema>;
