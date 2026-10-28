import { useQuery } from "@tanstack/react-query";

import { Spinner } from "../../components/ui/Spinner";
import { api } from "../../services/apiClient";
import type { MissionSummary } from "../../types/api";
import { MissionCard } from "./MissionCard";

export function MissionListPage() {
  const missions = useQuery({
    queryKey: ["missions"],
    queryFn: () => api<MissionSummary[]>("/missions"),
  });

  if (missions.isLoading) return <Spinner label="Loading missions" />;
  if (missions.isError || !missions.data) {
    return <p className="text-rose-300">Missions could not be loaded.</p>;
  }

  return (
    <div>
      <h1 className="text-3xl font-semibold">Missions</h1>
      <p className="mt-2 max-w-2xl text-slate-300">
        Cases open in order. Clear one at the pass mark before the next briefing is available.
      </p>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {missions.data.map((mission) => (
          <MissionCard key={mission.slug} mission={mission} />
        ))}
      </div>
    </div>
  );
}
