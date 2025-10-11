import type { TableCellValue } from "../TableStoreFactory";

interface Props {
  value: TableCellValue;
}

export default function TextCell({ value }: Props) {
  return (
    <textarea
      className="form-control"
      rows={5}
      readOnly
      value={(value || "").toString()}
    ></textarea>
  );
}
