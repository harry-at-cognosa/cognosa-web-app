import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";
import type { createTableStore } from "../../TableStoreFactory";
import PaginationLimit from "./PaginationLimit";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

const pageBtn =
  "grid size-7 place-items-center rounded-full text-ink-2 hover:not-disabled:bg-(--seg-on) disabled:cursor-not-allowed disabled:opacity-45";

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
    <>
      {/* Pagination Controls, with the shown rows info in the middle */}
      <div
        className="ml-2 inline-flex items-center gap-0.5 rounded-full bg-sunk p-[3px]"
        role="group"
        aria-label="Paging"
      >
        <button
          type="button"
          className={pageBtn}
          onClick={handleFastBackward}
          disabled={isFirstPage}
          aria-label="First page"
        >
          <ChevronsLeft className="size-4" />
        </button>
        <button
          type="button"
          className={pageBtn}
          onClick={handleBackward}
          disabled={isFirstPage}
          aria-label="Previous page"
        >
          <ChevronLeft className="size-4" />
        </button>
        <span className="px-2 text-[13px] font-semibold whitespace-nowrap text-ink tabular-nums">
          {offset + 1}-{offset + data.rows.length}/{total}
        </span>
        <button
          type="button"
          className={pageBtn}
          onClick={handleForward}
          disabled={isLastPage}
          aria-label="Next page"
        >
          <ChevronRight className="size-4" />
        </button>
        <button
          type="button"
          className={pageBtn}
          onClick={handleFastForward}
          disabled={isLastPage}
          aria-label="Last page"
        >
          <ChevronsRight className="size-4" />
        </button>
      </div>
      {/* Limit selector */}
      <PaginationLimit useStore={useStore} />
    </>
  );
}
