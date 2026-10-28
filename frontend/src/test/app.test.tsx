import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { MissionCard } from "../features/missions/MissionCard";
import { loginSchema, registerSchema } from "../features/auth/schemas";
import type { MissionSummary } from "../types/api";
import { ApiError } from "../services/apiClient";
import { errorMessage } from "../utils/errors";
import { statusLabel } from "../utils/format";
import { toggleId } from "../utils/selection";

const mission: MissionSummary = {
  slug: "phishing-investigation",
  title: "Phishing Investigation",
  description: "Review a forwarded email.",
  category: "phishing",
  difficulty: "beginner",
  xp_reward: 120,
  pass_score: 70,
  order_index: 1,
  status: "locked",
  best_score: null,
  attempts_count: 0,
};

describe("forms", () => {
  it("rejects a login email without a domain", () => {
    const result = loginSchema.safeParse({ email: "ada", password: "secret" });
    expect(result.success).toBe(false);
  });

  it("rejects a password without a number", () => {
    const result = registerSchema.safeParse({
      email: "ada@example.com",
      username: "ada",
      displayName: "Ada",
      password: "longpassword",
    });
    expect(result.success).toBe(false);
  });
});

describe("mission card", () => {
  it("shows a locked mission without a link", () => {
    render(
      <MemoryRouter>
        <MissionCard mission={mission} />
      </MemoryRouter>,
    );
    expect(screen.getByRole("heading", { name: "Phishing Investigation" })).toBeTruthy();
    expect(screen.getByText("Locked")).toBeTruthy();
    expect(screen.queryByRole("link")).toBeNull();
  });
});

describe("helpers", () => {
  it("toggles a selected id", () => {
    expect(toggleId(["a"], "b")).toEqual(["a", "b"]);
    expect(toggleId(["a", "b"], "a")).toEqual(["b"]);
  });

  it("labels mission status", () => {
    expect(statusLabel("completed")).toBe("Cleared");
  });

  it("reads the API error message", () => {
    expect(errorMessage(new ApiError(403, "forbidden", "Complete the previous mission."), "no")).toBe(
      "Complete the previous mission.",
    );
  });
});
