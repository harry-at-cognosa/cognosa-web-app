import { useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { createTableStore } from "../../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function PaginationLimit({ useStore }: Props) {
  const { nextRequest, data, setLimit, setOffset } = useStore();
  const [inputLimit, setInputLimit] = useState(nextRequest.limit); // local input state
  const debounceRef = useRef<number | null>(null);

  if (!data) return null;
  const { total, table_options } = data;
  const { offset } = nextRequest;

  const handleLimitSelectChange = (value: number) => {
    setInputLimit(value);
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    let newLimit = value;
    if (newLimit < 1) newLimit = 1;
    setLimit(newLimit);
    // Adjust offset if needed
    const newMaxOffset = Math.max(0, total - newLimit);
    if (offset > newMaxOffset) {
      setOffset(newMaxOffset);
    }
  };

  // Handle limit change
  const handleLimitInputChange = (value: number) => {
    // Update local input state immediately for UX
    setInputLimit(value);

    // Clear any existing debounce timer
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Set new debounce timer
    debounceRef.current = setTimeout(() => {
      let newLimit = value;
      if (newLimit < 1) newLimit = 1;

      setLimit(newLimit);

      // Adjust offset if needed
      const newMaxOffset = Math.max(0, total - newLimit);
      if (offset > newMaxOffset) {
        setOffset(newMaxOffset);
      }
    }, 2000); // 2 seconds
  };

  const idLimitInput = "limit_input__" + data.name;

  // A number can be typed (applied after 2 seconds) or picked from the list.
  return (
    <div className="inline-flex items-center gap-2 text-[13px] font-medium text-muted-foreground">
      <label htmlFor={idLimitInput}>Limit</label>
      <div className="inline-flex h-[34px] items-center rounded-full border border-line bg-surface pr-[3px] pl-1 hover:border-tint-edge focus-within:border-ring">
        <input
          id={idLimitInput}
          type="number"
          value={inputLimit}
          className="h-full w-[7ch] rounded-full bg-transparent pl-2.5 font-semibold text-ink tabular-nums outline-none"
          onChange={(e) => {
            const rawValue = e.target.value;
            const value = parseInt(rawValue, 10);
            if (!isNaN(value)) {
              handleLimitInputChange(value);
            }
          }}
          aria-label="Rows per page"
        />
        {table_options.select_limit.length ? (
          <DropdownMenu modal={false}>
            <DropdownMenuTrigger asChild>
              <button
                type="button"
                className="grid size-[26px] flex-none place-items-center rounded-full text-muted-foreground hover:bg-tint hover:text-tint-fg aria-expanded:bg-tint aria-expanded:text-tint-fg"
                aria-label="Choose rows per page"
              >
                <ChevronDown className="size-4" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="min-w-[10ch]">
              {table_options.select_limit.map((size) => (
                <DropdownMenuItem
                  key={size}
                  onSelect={() => handleLimitSelectChange(size)}
                >
                  {size}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        ) : null}
      </div>
    </div>
  );
}
