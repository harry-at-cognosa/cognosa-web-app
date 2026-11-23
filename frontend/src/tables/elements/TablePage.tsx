import type { ReactNode } from "react";
import { PageHead } from "@/components/Shell";

// Page frame of a CRUD page: the page heading, then the table card.
export default function TablePage({ children }: { children: ReactNode }) {
  return (
    <div className="min-w-0 px-5 pt-3 pb-12">
      <PageHead className="mb-3" />
      {children}
    </div>
  );
}
