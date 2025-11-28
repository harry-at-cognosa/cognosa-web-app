import { Button } from "react-bootstrap";
import { SkipStartFill, PlayFill, SkipEndFill } from "react-bootstrap-icons";
import type { createTableStore } from "../../TableStoreFactory";
import PaginationLimit from "./PaginationLimit";
import clsx from "clsx";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function PaginationControls({ useStore }: Props) {
  const { nextRequest, data, setOffset } = useStore();

  if (!data) return null;
  const { total } = data;
  const { offset, limit } = nextRequest;
  const isFirstPage = offset === 0;
  const isLastPage = offset + limit >= total;

  // Handle fast backward (first page)
  const handleFastBackward = () => {
    setOffset(0);
  };

  // Handle backward (previous page)
  const handleBackward = () => {
    setOffset(Math.max(0, offset - limit));
  };

  // Handle forward (next page)
  const handleForward = () => {
    setOffset(Math.min(total - limit, offset + limit));
  };

  // Handle fast forward (last page)
  const handleFastForward = () => {
    setOffset(Math.max(0, total - limit));
  };

  return (
    <div className="d-flex align-items-center justify-content-between mx-3">
      {/* Pagination Controls */}
      <div className="d-flex gap-2">
        <Button
          variant="outline-secondary"
          className={clsx("p-0", isFirstPage ? "bg-tc-100" : "bg-tc-300")}
          size="sm"
          onClick={handleFastBackward}
          disabled={isFirstPage}
          aria-label="First page"
        >
          <SkipStartFill size={"28px"} />
        </Button>
        <Button
          variant="outline-secondary"
          size="sm"
          className={clsx("p-0", isFirstPage ? "bg-tc-100" : "bg-tc-300")}
          onClick={handleBackward}
          disabled={isFirstPage}
          aria-label="Previous page"
        >
          <PlayFill size={"28px"} style={{ transform: "rotate(180deg)" }} />
        </Button>
        <Button
          variant="outline-secondary"
          size="sm"
          className={clsx("p-0", isLastPage ? "bg-tc-100" : "bg-tc-300")}
          onClick={handleForward}
          disabled={isLastPage}
          aria-label="Next page"
        >
          <PlayFill size={"28px"} />
        </Button>
        <Button
          variant="outline-secondary"
          size="sm"
          className={clsx("p-0", isLastPage ? "bg-tc-100" : "bg-tc-300")}
          onClick={handleFastForward}
          disabled={isLastPage}
          aria-label="Last page"
        >
          <SkipEndFill size={"28px"} />
        </Button>
      </div>

      {/* Shown rows info */}
      <div className="text-muted small mx-1">
        {offset + 1}-{offset + data.rows.length}/{total}
      </div>
      {/* Limit selector */}
      <PaginationLimit useStore={useStore} />
    </div>
  );
}
