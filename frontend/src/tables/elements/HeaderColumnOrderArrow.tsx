import type { TableRequest, TableResponse } from "../TableStoreFactory";
import styles from "./HeaderColumnsRow.module.css";

interface Props {
  data: TableResponse;
  col: string;
  nextRequest: TableRequest;
}

export default function HeaderColumnOrderArrow({
  data,
  col,
  nextRequest,
}: Props) {
  if (!data.table_options.order_by__allow.includes(col)) return null;
  const isVisible = nextRequest.order_by === col;
  const arrowSymbol = isVisible
    ? nextRequest.order_dir === "desc"
      ? "▼"
      : "▲"
    : "▲";

  return (
    <span
      className={
        isVisible ? styles.sortIndicator : styles.sortIndicatorInvisible
      }
    >
      {arrowSymbol}
    </span>
  );
}
