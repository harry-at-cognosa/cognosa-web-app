// History list + work area, shared by Queries and Chat. The width comes from
// the product's panel-width hook (same storage key and limits as v1.0.1); the
// collapsed state is a view-level preference kept in localStorage. This file
// only turns pointer movement into setPct calls.
import { useCallback, useRef, useState, useSyncExternalStore, type ReactNode } from "react";
import { ChevronsLeft, List, Plus } from "lucide-react";
import { Sheet, SheetContent, SheetDescription, SheetTitle } from "@/components/ui/sheet";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { DEFAULT_PCT, MAX_PCT, MIN_PCT, useLeftPanelPct } from "@/pages/QueryDocuments/hooks/useLeftPanelPct";

const COLLAPSED_KEY = "query_page_left_panel_collapsed";
const PHONE_QUERY = "(max-width: 767px)";

function subscribePhone(cb: () => void) {
  const m = window.matchMedia(PHONE_QUERY);
  m.addEventListener("change", cb);
  return () => m.removeEventListener("change", cb);
}

/** True below Tailwind's md breakpoint. Presentation only: no behaviour depends on it. */
// eslint-disable-next-line react-refresh/only-export-components
export function useIsPhone() {
  return useSyncExternalStore(subscribePhone, () => window.matchMedia(PHONE_QUERY).matches);
}

function useCollapsed(): [boolean, () => void] {
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem(COLLAPSED_KEY) === "1";
    } catch {
      return false;
    }
  });
  const toggle = useCallback(() => {
    setCollapsed((cur) => {
      const next = !cur;
      try {
        localStorage.setItem(COLLAPSED_KEY, next ? "1" : "0");
      } catch {
        /* ignore storage errors */
      }
      return next;
    });
  }, []);
  return [collapsed, toggle];
}

interface SplitLayoutProps {
  listLabel: string; // "Query history" / "Conversations"
  newLabel: string; // "New Query" / "New Chat"
  onNew: () => void;
  /** greys out every New button (Chat: while an answer is being written) */
  newDisabled?: boolean;
  /** the list; receives a function to call after a choice (closes the phone sheet) */
  list: (afterPick: () => void) => ReactNode;
  /**
   * the work area; it receives tools for the page heading row: on a phone the
   * button that opens the list, on a desktop with the list collapsed the button
   * that shows it again and the New button (the collapsed list leaves no strip)
   */
  children: (headTools: ReactNode) => ReactNode;
}

const noop = () => {};

export function SplitLayout({ listLabel, newLabel, onNew, newDisabled, list, children }: SplitLayoutProps) {
  const [pct, setPct] = useLeftPanelPct();
  const [collapsed, toggleCollapsed] = useCollapsed();
  const phone = useIsPhone();
  const wrap = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);

  const newButton = (after?: () => void) => (
    <button
      type="button"
      onClick={() => {
        onNew();
        after?.();
      }}
      disabled={newDisabled}
      className="inline-flex h-[38px] min-w-0 flex-1 items-center justify-center gap-2 rounded-full border border-hair bg-surface font-semibold text-accent-text shadow-[0_8px_18px_-12px_var(--glow)] hover:border-tint-edge disabled:pointer-events-none disabled:opacity-50"
    >
      <Plus className="size-4" />
      <span className="truncate">{newLabel}</span>
    </button>
  );

  if (phone) {
    // On a phone the list is always behind its control; it opens as a sheet.
    const closeSheet = () => setSheetOpen(false);
    const listButton = (
      <button
        type="button"
        className="icon-btn"
        aria-label={`Show ${listLabel.toLowerCase()}`}
        aria-expanded={sheetOpen}
        onClick={() => setSheetOpen(true)}
      >
        <List className="size-4" />
      </button>
    );
    return (
      <div className="h-full min-w-0 px-2 pt-2 pb-2">
        {children(listButton)}
        <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
          <SheetContent side="left" className="w-[86vw] gap-0 rounded-r-3xl border-0 p-3 pt-3">
            <SheetTitle className="mb-2 pr-10 pl-1">{listLabel}</SheetTitle>
            <SheetDescription className="sr-only">{listLabel}</SheetDescription>
            <div className="mb-1 flex">{newButton(closeSheet)}</div>
            <div className="scroll-soft -mx-1 min-h-0 flex-1 overflow-y-auto px-1">{list(closeSheet)}</div>
          </SheetContent>
        </Sheet>
      </div>
    );
  }

  const resetPct = () => setPct(DEFAULT_PCT);
  const startDrag = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!wrap.current) return;
    e.preventDefault();
    // the percentage is of the grid's content box, so leave the padding out
    const box = wrap.current.getBoundingClientRect();
    const cs = getComputedStyle(wrap.current);
    const left = box.left + parseFloat(cs.paddingLeft);
    const width = box.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    if (width <= 0) return;
    setDragging(true);
    const move = (ev: PointerEvent) => setPct(((ev.clientX - left) / width) * 100);
    const up = () => {
      setDragging(false);
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      window.removeEventListener("pointercancel", up);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    window.addEventListener("pointercancel", up);
  };

  const hideLabel = `Hide ${listLabel.toLowerCase()}`;
  const showLabel = `Show ${listLabel.toLowerCase()}`;

  if (collapsed) {
    // No strip is left behind: the two controls move into the page heading row.
    const headTools = (
      <>
        <Tooltip>
          <TooltipTrigger asChild>
            <button type="button" className="icon-btn" onClick={toggleCollapsed} aria-expanded={false} aria-label={showLabel}>
              <List className="size-4" />
            </button>
          </TooltipTrigger>
          <TooltipContent side="bottom">{showLabel}</TooltipContent>
        </Tooltip>
        <button
          type="button"
          onClick={onNew}
          disabled={newDisabled}
          className="inline-flex h-9 flex-none items-center gap-1.5 rounded-full border border-hair bg-surface px-3.5 font-semibold text-accent-text shadow-[0_8px_18px_-12px_var(--glow)] hover:border-tint-edge disabled:pointer-events-none disabled:opacity-50"
        >
          <Plus className="size-4" />
          {newLabel}
        </button>
      </>
    );
    return <div className="h-full min-w-0 pt-3 pr-5 pb-2 pl-3">{children(headTools)}</div>;
  }

  return (
    <div
      ref={wrap}
      className={cn("grid h-full min-w-0 pt-3 pr-5 pb-2 pl-1.5", dragging && "cursor-col-resize select-none")}
      style={{ gridTemplateColumns: `${pct}% 12px minmax(0,1fr)` }}
    >
      <aside className="glass-side flex min-h-0 min-w-0 flex-col rounded-3xl px-2.5 pt-3 pb-3.5" aria-label={listLabel}>
        <div className="mb-1.5 flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <button type="button" className="icon-btn" onClick={toggleCollapsed} aria-expanded aria-label={hideLabel}>
                <ChevronsLeft className="size-4" />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom">{hideLabel}</TooltipContent>
          </Tooltip>
          {newButton()}
        </div>
        <div className="scroll-soft -mx-1 min-h-0 flex-1 overflow-y-auto px-1">{list(noop)}</div>
      </aside>
      <div
        role="separator"
        aria-orientation="vertical"
        aria-label={`Resize ${listLabel.toLowerCase()} (double-click to reset)`}
        aria-valuemin={MIN_PCT}
        aria-valuemax={MAX_PCT}
        aria-valuenow={Math.round(pct)}
        tabIndex={0}
        title="Drag to resize. Double-click to reset."
        onPointerDown={startDrag}
        onDoubleClick={resetPct}
        onKeyDown={(e) => {
          if (e.key === "ArrowLeft") setPct(pct - 2);
          if (e.key === "ArrowRight") setPct(pct + 2);
          if (e.key === "Home" || e.key === "Enter") resetPct();
        }}
        className="group relative cursor-col-resize touch-none rounded-full outline-none"
      >
        <span
          className={cn(
            "absolute top-1/2 left-1 h-11 w-1 -translate-y-1/2 rounded bg-(--tint-edge) opacity-60 transition-all group-hover:h-16 group-hover:opacity-100 group-focus-visible:h-16 group-focus-visible:opacity-100 group-focus-visible:outline-2 group-focus-visible:outline-offset-2 group-focus-visible:outline-ring",
            dragging && "h-16 opacity-100",
          )}
        />
      </div>
      <section className="min-h-0 min-w-0">{children(null)}</section>
    </div>
  );
}

/** Heading of a recency group in either list. */
export function GroupLabel({ children }: { children: ReactNode }) {
  return <h3 className="mx-2.5 mt-3.5 mb-1 text-[13px] leading-none font-semibold text-muted-foreground">{children}</h3>;
}
