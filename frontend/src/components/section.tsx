import { AlertCircleIcon, LoaderCircleIcon } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function Section({
  step,
  title,
  description,
  children,
}: {
  step: string;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section className="flex flex-col gap-5">
      <div className="flex flex-col gap-1">
        <span className="text-[0.7rem] font-medium tracking-[0.18em] text-muted-foreground uppercase">
          {step}
        </span>
        <h2 className="text-lg font-medium tracking-tight">{title}</h2>
        <p className="max-w-2xl text-sm text-muted-foreground">{description}</p>
      </div>
      {children}
    </section>
  );
}

export function Busy({ label }: { label: string }) {
  return (
    <p className="flex items-center gap-2 text-sm text-muted-foreground">
      <LoaderCircleIcon className="size-4 animate-spin" />
      {label}
    </p>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <Alert variant="destructive">
      <AlertCircleIcon />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}

export function SuccessNote({ message }: { message: string }) {
  return (
    <Alert>
      <AlertTitle>Done</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}
