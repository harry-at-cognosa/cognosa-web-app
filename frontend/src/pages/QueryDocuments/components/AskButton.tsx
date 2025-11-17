import { Button, Spinner } from "react-bootstrap";
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
    current.is_processing === true ||
    current.question_number >= 2;
  const showSpinner = Boolean(current.is_processing);
  return (
    <Button
      onClick={handleSubmit}
      disabled={disabled}
      variant="outline-secondary"
      className="w-100 fw-bold"
      style={{ color: "black" }}
    >
      {showSpinner ? <Spinner size={"sm"} /> : null}
      {getButtonText()}
    </Button>
  );
}
