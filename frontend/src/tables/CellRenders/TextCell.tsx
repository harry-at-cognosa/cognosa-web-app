import type { TableCellValue } from "../TableStoreFactory";

interface Props {
  value: TableCellValue;
  rows?: number | undefined;
}

export default function TextCell({ value, rows }: Props) {
  return (
    <textarea
      className="form-control need-fix-height"
      rows={rows || 5}
      readOnly
      value={(value || "").toString()}
    ></textarea>
  );
}
