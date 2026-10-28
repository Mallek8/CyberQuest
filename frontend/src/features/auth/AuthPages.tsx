import { zodResolver } from "@hookform/resolvers/zod";
import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";

import { PublicHeader } from "../../components/layout/PublicHeader";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { useAuth } from "../../hooks/useAuth";
import { errorMessage } from "../../utils/errors";
import { loginSchema, registerSchema, type LoginValues, type RegisterValues } from "./schemas";

export function LoginPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string | null>(null);
  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: LoginValues) {
    try {
      setFormError(null);
      await auth.login(values);
      navigate("/app");
    } catch (error) {
      setFormError(errorMessage(error, "Could not sign in."));
    }
  }

  return (
    <AuthLayout
      title="Sign in"
      lede="Pick up the case you left open."
      footer={
        <>
          New here? <Link to="/register">Create an account</Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)} noValidate>
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          {...form.register("email")}
          error={form.formState.errors.email?.message}
        />
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          {...form.register("password")}
          error={form.formState.errors.password?.message}
        />
        {formError ? <p className="text-sm text-rose-300">{formError}</p> : null}
        <Button type="submit" disabled={form.formState.isSubmitting} className="w-full">
          {form.formState.isSubmitting ? "Signing in" : "Sign in"}
        </Button>
      </form>
    </AuthLayout>
  );
}

export function RegisterPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string | null>(null);
  const form = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", username: "", displayName: "", password: "" },
  });

  async function onSubmit(values: RegisterValues) {
    try {
      setFormError(null);
      await auth.registerAccount(values);
      navigate("/app");
    } catch (error) {
      setFormError(errorMessage(error, "Could not create the account."));
    }
  }

  return (
    <AuthLayout
      title="Create your analyst profile"
      lede="The first mission is open as soon as the account exists."
      footer={
        <>
          Already registered? <Link to="/login">Sign in</Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)} noValidate>
        <Input
          label="Display name"
          autoComplete="name"
          {...form.register("displayName")}
          error={form.formState.errors.displayName?.message}
        />
        <Input
          label="Username"
          autoComplete="username"
          {...form.register("username")}
          error={form.formState.errors.username?.message}
        />
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          {...form.register("email")}
          error={form.formState.errors.email?.message}
        />
        <Input
          label="Password"
          type="password"
          autoComplete="new-password"
          {...form.register("password")}
          error={form.formState.errors.password?.message}
        />
        {formError ? <p className="text-sm text-rose-300">{formError}</p> : null}
        <Button type="submit" disabled={form.formState.isSubmitting} className="w-full">
          {form.formState.isSubmitting ? "Creating account" : "Create account"}
        </Button>
      </form>
    </AuthLayout>
  );
}

function AuthLayout({
  title,
  lede,
  footer,
  children,
}: {
  title: string;
  lede: string;
  footer: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen">
      <PublicHeader />
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rise hidden rounded-3xl border border-cyan-300/15 bg-panel/80 p-8 shadow-glow lg:block">
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-cyan-200/80">Case desk</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-4 max-w-md text-slate-300">{lede}</p>
          <pre className="mt-8 overflow-hidden rounded-2xl border border-white/10 bg-ink p-4 font-mono text-xs leading-6 text-slate-300">
            {`analyst@cyberquest
mission  phishing-investigation
status   ready
score    waiting on your read`}
          </pre>
        </section>
        <section className="rise rounded-3xl border border-white/10 bg-panel/90 p-6 shadow-glow sm:p-8">
          <h1 className="text-2xl font-semibold lg:hidden">{title}</h1>
          <p className="mb-6 mt-2 text-slate-400 lg:hidden">{lede}</p>
          {children}
          <p className="mt-6 text-sm text-slate-400 [&_a]:text-cyan-200">{footer}</p>
        </section>
      </div>
    </div>
  );
}
