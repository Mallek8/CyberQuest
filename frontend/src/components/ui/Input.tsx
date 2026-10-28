import { forwardRef, type InputHTMLAttributes } from "react";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};

export const Input = forwardRef<HTMLInputElement, Props>(function Input(
  { label, error, id, className = "", ...props },
  ref,
) {
  const inputId = id ?? props.name ?? label.toLowerCase().replace(/\s+/g, "-");
  return (
    <label className="block text-sm" htmlFor={inputId}>
      <span className="mb-1.5 block text-slate-300">{label}</span>
      <input
        id={inputId}
        ref={ref}
        aria-invalid={Boolean(error)}
        className={`w-full rounded-xl border border-white/10 bg-ink px-3 py-2.5 text-slate-100 outline-none ring-cyan-300/40 placeholder:text-slate-500 focus:border-cyan-300/50 focus:ring-2 ${className}`}
        {...props}
      />
      {error ? <span className="mt-1 block text-rose-300">{error}</span> : null}
    </label>
  );
});
