import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "ghost";

export function buttonClass(variant: Variant = "primary"): string {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50";
  if (variant === "ghost") {
    return `${base} border border-white/15 bg-white/5 text-slate-100 hover:border-cyan-300/40`;
  }
  return `${base} bg-cyan-300 text-ink hover:bg-cyan-200`;
}

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
};

export function Button({ variant = "primary", className = "", ...props }: Props) {
  return <button className={`${buttonClass(variant)} ${className}`} {...props} />;
}
