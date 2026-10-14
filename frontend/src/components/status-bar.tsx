import { CircleAlertIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Status } from "@/lib/api";

export function StatusBar({ status, error }: { status: Status | null; error: string }) {
  if (error) {
    return (
      <div className="flex items-center gap-2 text-xs text-destructive">
        <CircleAlertIcon className="size-3.5" />
        {error}
      </div>
    );
  }

  if (!status) {
    return <div className="h-5 w-56 animate-pulse rounded-full bg-muted" />;
  }

  return (
    <div className="flex flex-wrap items-center justify-end gap-2">
      <Badge variant={status.apiKeyConfigured ? "secondary" : "outline"}>
        {status.apiKeyConfigured ? "Gemini key configured" : "Gemini key missing"}
      </Badge>
      <Badge variant={status.datasetAvailable ? "secondary" : "outline"}>
        {status.datasetAvailable ? "CSV dataset loaded" : "CSV dataset missing"}
      </Badge>
    </div>
  );
}
