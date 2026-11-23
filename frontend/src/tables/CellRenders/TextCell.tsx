import type { TableCellValue } from "../TableStoreFactory";

interface Props {
  value: TableCellValue;
  rows?: number | undefined;
}

// Long text in a cell: a read-only box that scrolls and can be dragged larger.
// "need-fix-height" marks it for fixTextareaHeights (equal heights in a row).
export default function TextCell({ value, rows }: Props) {
  return (
    <textarea
      className="need-fix-height scroll-soft block w-full min-w-44 rounded-xl border border-line-soft bg-surface px-2.5 py-1.5 text-[13px] leading-snug text-ink outline-none focus-visible:border-ring"
      rows={rows || 5}
      readOnly
      value={(value || "").toString()}
    ></textarea>
  );
}
