import { LoaderCircle } from "lucide-react";

export default function CenteredSpinner() {
  return (
    <div className="flex min-h-dvh items-center justify-center">
      <LoaderCircle
        className="size-8 animate-spin text-accent-text"
        role="status"
        aria-label="Loading"
      />
    </div>
  );
}
