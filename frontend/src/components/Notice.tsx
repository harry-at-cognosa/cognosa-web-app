import { CircleAlert, X } from "lucide-react";
import { Alert, AlertAction, AlertDescription } from "@/components/ui/alert";

/** The store's `notice` (v1.0.1 uses alert() for these), as a dismissible shadcn Alert. */
export function Notice({ text, onDismiss }: { text: string | null; onDismiss: () => void }) {
  if (!text) return null;
  return (
    <Alert role="alert" className="rounded-2xl border-transparent bg-err-bg px-3.5 py-2.5 text-err has-data-[slot=alert-action]:pr-12">
      <CircleAlert />
      <AlertDescription className="text-sm font-medium text-err">{text}</AlertDescription>
      <AlertAction className="top-1.5 right-1.5">
        <button type="button" className="x-btn text-err" aria-label="Dismiss message" onClick={onDismiss}>
          <X className="size-4" />
        </button>
      </AlertAction>
    </Alert>
  );
}
