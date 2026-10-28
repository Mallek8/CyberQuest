import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { buttonClass, Button } from "../../components/ui/Button";
import { Spinner } from "../../components/ui/Spinner";
import { ApiError, api } from "../../services/apiClient";
import type { Achievement, HintHistory, HintResult, MissionDetail, SubmitResult } from "../../types/api";
import { errorMessage } from "../../utils/errors";
import { categoryLabel } from "../../utils/format";
import { toggleId } from "../../utils/selection";
import { BadgeNotice, HintPanel } from "../ai-assistant/HintPanel";
import { AnomalyView } from "./AnomalyView";
import { LogView } from "./LogView";
import { readEmail, readEvents, readLogs } from "./payload";
import { PhishingView } from "./PhishingView";
import { ResultPanel } from "./ResultPanel";

export function GameplayPage() {
  const { slug = "" } = useParams();
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<string[]>([]);
  const [result, setResult] = useState<SubmitResult | null>(null);
  const [notice, setNotice] = useState<Achievement[]>([]);

  useEffect(() => {
    setSelected([]);
    setResult(null);
    setNotice([]);
  }, [slug]);

  const missionQuery = useQuery({
    queryKey: ["mission", slug],
    queryFn: () => api<MissionDetail>(`/missions/${slug}`),
    enabled: Boolean(slug),
    retry: false,
  });

  const hintsQuery = useQuery({
    queryKey: ["hints", slug],
    queryFn: () => api<HintHistory>(`/missions/${slug}/hints`),
    enabled: Boolean(missionQuery.data),
  });

  const start = useMutation({
    mutationFn: () => api(`/missions/${slug}/start`, { method: "POST" }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["mission", slug] });
      void queryClient.invalidateQueries({ queryKey: ["missions"] });
    },
  });

  const status = missionQuery.data?.status;
  const startMission = start.mutate;
  useEffect(() => {
    if (status === "available") {
      startMission();
    }
  }, [status, slug, startMission]);

  const submit = useMutation({
    mutationFn: () =>
      api<SubmitResult>(`/missions/${slug}/submit`, {
        method: "POST",
        body: JSON.stringify({ selected_ids: selected }),
      }),
    onSuccess: (data) => {
      setResult(data);
      setNotice(data.newly_unlocked_achievements);
      void queryClient.invalidateQueries({ queryKey: ["mission", slug] });
      void queryClient.invalidateQueries({ queryKey: ["missions"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      void queryClient.invalidateQueries({ queryKey: ["achievements"] });
      void queryClient.invalidateQueries({ queryKey: ["attempts"] });
      void queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const hint = useMutation({
    mutationFn: () => api<HintResult>(`/missions/${slug}/hints`, { method: "POST" }),
    onSuccess: (data) => {
      setNotice(data.newly_unlocked_achievements);
      void queryClient.invalidateQueries({ queryKey: ["hints", slug] });
      void queryClient.invalidateQueries({ queryKey: ["achievements"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  if (missionQuery.isLoading) {
    return <Spinner label="Opening mission" />;
  }

  if (missionQuery.error instanceof ApiError && missionQuery.error.code === "forbidden") {
    return (
      <div>
        <h1 className="text-3xl font-semibold">Mission locked</h1>
        <p className="mt-3 max-w-xl text-slate-300">{missionQuery.error.message}</p>
        <Link to="/app/missions" className={`${buttonClass()} mt-6`}>
          Back to missions
        </Link>
      </div>
    );
  }

  if (!missionQuery.data) {
    return <p className="text-rose-300">This mission could not be opened.</p>;
  }

  const mission = missionQuery.data;
  const email = mission.category === "phishing" ? readEmail(mission.challenge.payload) : null;
  const logs = mission.category === "logs" ? readLogs(mission.challenge.payload) : null;
  const events = mission.category === "anomaly" ? readEvents(mission.challenge.payload) : null;

  function toggle(id: string) {
    setSelected((current) => toggleId(current, id));
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-wide text-cyan-200">{categoryLabel(mission.category)}</p>
        <h1 className="mt-1 text-3xl font-semibold">{mission.title}</h1>
        <p className="mt-3 max-w-3xl text-slate-300">{mission.briefing}</p>
        <p className="mt-3 text-sm text-slate-400">
          Pass mark {mission.pass_score}. Reward up to {mission.xp_reward} XP.
          {mission.best_score !== null ? ` Best score ${mission.best_score}.` : ""}
        </p>
      </header>
      <BadgeNotice badges={notice} />
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-5">
          <p className="text-sm text-slate-200">{mission.challenge.prompt}</p>
          {email ? (
            <PhishingView
              email={email.email}
              indicators={email.indicators}
              selected={selected}
              onToggle={toggle}
            />
          ) : null}
          {logs ? <LogView logs={logs} selected={selected} onToggle={toggle} /> : null}
          {events ? <AnomalyView events={events} selected={selected} onToggle={toggle} /> : null}
          <div className="flex flex-wrap items-center gap-3">
            <Button type="button" onClick={() => submit.mutate()} disabled={submit.isPending}>
              {submit.isPending ? "Scoring" : `Submit ${selected.length} selected`}
            </Button>
            {submit.isError ? (
              <p className="text-sm text-rose-300">{errorMessage(submit.error, "Submit failed.")}</p>
            ) : null}
          </div>
          {result ? (
            <ResultPanel
              score={result.score}
              maxScore={result.max_score}
              passed={result.passed}
              xpAwarded={result.xp_awarded}
              summary={result.summary}
              feedback={result.feedback}
            />
          ) : null}
        </div>
        <div className="space-y-3">
          <HintPanel
            history={hintsQuery.data}
            pending={hint.isPending}
            onRequest={() => hint.mutate()}
          />
          {hint.isError ? (
            <p className="text-sm text-rose-300">{errorMessage(hint.error, "No hint was returned.")}</p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
