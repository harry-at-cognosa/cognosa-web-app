import { Check, X } from "lucide-react";
import type { TableOptions, TableCellValue } from "../TableStoreFactory";

interface Props {
  table_options: TableOptions;
  col: string;
  value: TableCellValue;
}

export default function BooleanCheck({ table_options, col, value }: Props) {
  if (!table_options) return null;
  if (!value && table_options.read__hide_on_false.includes(col)) return null;
  if (value)
    return (
      <Check
        className="inline-block size-[18px] stroke-[2.6] text-ok"
        role="img"
        aria-label="yes"
      />
    );
  else
    return (
      <X
        className="inline-block size-[18px] stroke-[2.6] text-err"
        role="img"
        aria-label="no"
      />
    );
}
