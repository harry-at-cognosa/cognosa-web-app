import { useState } from "react";
import { FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";

interface JsonItem {
  page_content: string;
  metadata: Record<string, any>;
  [key: string]: any; // Allow other properties
}

export default function ContextJSON() {
  const [show, setShow] = useState(false);
  const { context_json, doc_task_id, short_name } = useDocTasksCurrentStore();
  if (!context_json) return null;

  // Parse the JSON string
  let parsedData: JsonItem[] = [];
  try {
    parsedData = JSON.parse(context_json);
  } catch {}

  const headerText = "Found documents (" + parsedData.length + ")";
  function getItemHeader(item: JsonItem) {
    if (item?.metadata?.source)
      return (
        (item.metadata.source.length > 100 ? "..." : "") +
        item.metadata.source.slice(-100)
      );
    return item.page_content?.substring(0, 50) + "..." || "";
  }

  return (
    <>
      <Button
        type="button"
        variant="secondary"
        size="sm"
        onClick={() => setShow(true)}
      >
        <FileText className="size-3.5" />
        {headerText + "..."}
      </Button>
      <Sheet open={show} onOpenChange={setShow}>
        <SheetContent
          side="right"
          className="gap-0 border-0 data-[side=right]:w-[min(1100px,100vw)] data-[side=right]:border-l-0 data-[side=right]:sm:max-w-[min(1100px,92vw)] md:rounded-l-[28px]"
        >
          <SheetHeader className="p-5 pb-3">
            <SheetTitle>{headerText + ":"}</SheetTitle>
            <SheetDescription>
              Query {doc_task_id}: {short_name}
            </SheetDescription>
          </SheetHeader>
          {parsedData.length === 0 ? (
            <div className="py-6 text-center">
              <p>No data to display</p>
            </div>
          ) : (
            <ol className="scroll-soft min-h-0 flex-1 overflow-y-auto px-5 pb-5">
              {parsedData.map((item, index) => (
                <li key={index} className="border-t border-line-soft py-3.5">
                  <div className="mb-2 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-0.5">
                    <h3 className="font-semibold text-ink">
                      Item{" "}
                      <span className="text-accent-text tabular-nums">
                        {index + 1}
                      </span>
                    </h3>
                    <small className="min-w-0 text-[13px] wrap-anywhere text-muted-foreground">
                      {getItemHeader(item)}
                    </small>
                  </div>
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                    {/* Page Content - Textarea */}
                    <div className="flex min-w-0 flex-col">
                      <label className="lbl" htmlFor={`found-doc-${index}`}>
                        Page Content
                      </label>
                      <textarea
                        id={`found-doc-${index}`}
                        rows={12}
                        value={item.page_content || ""}
                        readOnly
                        className="scroll-soft min-h-[300px] w-full flex-1 resize-y rounded-xl border border-line bg-surface px-3 py-2 font-mono text-xs text-ink outline-none focus-visible:border-ring"
                      />
                    </div>

                    {/* Metadata and Other Fields - JSON */}
                    <div className="flex min-w-0 flex-col">
                      <span className="lbl">Metadata & Other Fields</span>
                      <pre className="scroll-soft m-0 min-h-[300px] flex-1 overflow-auto rounded-xl bg-sunk p-3 font-mono text-xs wrap-anywhere whitespace-pre-wrap text-ink">
                        {JSON.stringify(
                          {
                            metadata: item.metadata,
                            ...Object.fromEntries(
                              Object.entries(item).filter(
                                ([key]) => key !== "page_content",
                              ),
                            ),
                          },
                          null,
                          2,
                        )}
                      </pre>
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </SheetContent>
      </Sheet>
    </>
  );
}
