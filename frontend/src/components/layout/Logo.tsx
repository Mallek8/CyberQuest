import { Shield } from "lucide-react";
import { Link } from "react-router-dom";

export function Logo({ to = "/" }: { to?: string }) {
  return (
    <Link to={to} className="inline-flex items-center gap-2 font-semibold tracking-tight">
      <Shield className="h-5 w-5 text-cyan-300" aria-hidden="true" />
      CyberQuest
    </Link>
  );
}
