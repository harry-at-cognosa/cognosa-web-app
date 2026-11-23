import type { ReactNode } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  PopoverClose,
  PopoverContent,
  PopoverTitle,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";

/**
 * Body of the two setting editors (Retrieval Parameters, Retrieval Filters):
 * a glass popover anchored to its pill, with a title, a close button and a
 * sticky Apply footer. Closing without Apply discards (the caller decides).
 */
export function EditorPopoverContent({
  title,
  className,
  onApply,
  children,
}: {
  title: string;
  className?: string;
  onApply: () => void;
  children: ReactNode;
}) {
  return (
    <PopoverContent
      side="top"
      align="start"
      sideOffset={10}
      collisionPadding={12}
      className={cn(
        "scroll-soft max-h-(--radix-popover-content-available-height) max-w-[calc(100vw-24px)] gap-0 overflow-y-auto",
        className,
      )}
    >
      <div className="mb-3 flex items-center gap-3">
        <PopoverTitle className="flex-1 font-heading text-base font-semibold tracking-[-0.01em]">
          {title}
        </PopoverTitle>
        <PopoverClose asChild>
          <Button
            type="button"
            variant="outline"
            size="icon-sm"
            aria-label={`Close ${title} without applying`}
          >
            <X />
          </Button>
        </PopoverClose>
      </div>
      {children}
      <div className="sticky -bottom-4 z-10 -mx-4 mt-3.5 -mb-4 flex justify-end rounded-b-[22px] border-t border-line-soft bg-(--solid) px-4 py-3">
        <Button type="button" onClick={onApply}>
          Apply
        </Button>
      </div>
    </PopoverContent>
  );
}
