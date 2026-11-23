import { LoaderCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import { useQueryDocumentsStore } from "../stores/useQueryDocumentStore";

interface Props {
  handleSubmit: () => void;
}

export default function AskButton({ handleSubmit }: Props) {
  const current = useDocTasksCurrentStore();
  const queryStore = useQueryDocumentsStore();

  function getButtonText(): string {
    if (current.is_processing) return "";
    if (current.question_number == 1) return "Ask follow-up question";
    if (current.question_number >= 2) return "Added follow-up question";
    return "Ask";
  }
  const disabled =
    queryStore.isPolling ||
    current.needReload ||
    current.needReloadFromHistory ||
    current.is_processing === true ||
    current.question_number >= 2;
  const showSpinner = Boolean(current.is_processing);
  return (
    <Button
      type="button"
      size="lg"
      className="flex-none max-md:w-full"
      onClick={handleSubmit}
      disabled={disabled}
    >
      {showSpinner ? (
        <>
          <LoaderCircle className="animate-spin" />
          <span className="sr-only">{current.status_text || "Processing"}</span>
        </>
      ) : null}
      {getButtonText()}
    </Button>
  );
}
