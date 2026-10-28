import { Link } from "react-router-dom";

import { buttonClass } from "../ui/Button";
import { Logo } from "./Logo";

export function PublicHeader() {
  return (
    <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5">
      <Logo />
      <nav className="flex items-center gap-3 text-sm">
        <Link to="/login" className="text-slate-300 hover:text-white">
          Sign in
        </Link>
        <Link to="/register" className={buttonClass("primary")}>
          Start your mission
        </Link>
      </nav>
    </header>
  );
}
