import { LoaderCircle } from "lucide-react";
import type { createTableStore } from "../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

// Shown while a create or update request is pending. It is rendered inside the
// Add / Edit dialog and covers it, so nothing can be changed or closed meanwhile.
export default function BusyModal({ useStore }: Props) {
  const { busy } = useStore();
  if (busy !== "create_pending" && busy !== "update_pending") return null;
  return (
    <div
      role="status"
      className="absolute inset-0 z-20 grid place-items-center rounded-[inherit] bg-(--scrim)"
    >
      <div className="glass-pop rounded-3xl px-7 py-6 text-center">
        <LoaderCircle className="mx-auto mb-3 size-8 animate-spin text-accent-text" />
        <div className="font-bold">Processing, please wait...</div>
      </div>
    </div>
  );
}
