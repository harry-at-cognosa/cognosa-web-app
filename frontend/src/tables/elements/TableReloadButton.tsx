import { RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import type { createTableStore } from "../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function TableReloadButton({ useStore }: Props) {
  const tableStore = useStore();
  return (
    <button
      type="button"
      className="icon-btn size-[30px]!"
      onClick={() => tableStore.setNeedReload(true)}
      aria-label="Reload"
      title="Reload"
    >
      <RefreshCw
        className={cn("size-3.5", tableStore.busy === "read" && "animate-spin")}
      />
    </button>
  );
}
