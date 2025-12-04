import getColor from "../../api/getColor";
import BooleanCheck from "../CellRenders/BooleanCheck";
import { BusyCell } from "../CellRenders/BusyCell";
import TextCell from "../CellRenders/TextCell";
import type { createTableStore, TableRow } from "../TableStoreFactory";

interface TdProps extends React.TdHTMLAttributes<HTMLTableCellElement> {
  isBusy: boolean | undefined;
}

function Td({ isBusy, className, children, ...props }: TdProps) {
  const combinedClassName = "position-relative " + (className || "");
  return (
    <td {...props} className={combinedClassName}>
      {children}
      <BusyCell isBusy={isBusy || false} />
    </td>
  );
}

interface Props {
  useStore: ReturnType<typeof createTableStore>;
  row: TableRow;
  col: string;
  isBusy?: boolean;
}

export default function ViewCellElement({ useStore, row, col, isBusy }: Props) {
  const { data } = useStore();
  if (!data) return null;
  const pk_value_str = (row[data.table_options.pk] || -1).toString();
  const key = "td__" + pk_value_str + "__" + col;
  const value = row[col];
  const value_str = value?.toString() || "";
  const cellType = data.columns[col].type;
  const add_values = data.table_options.add_values;

  if (cellType === "boolean")
    return (
      <Td key={key} isBusy={isBusy}>
        <BooleanCheck
          table_options={data.table_options}
          col={col}
          value={value}
        ></BooleanCheck>
      </Td>
    );
  if (cellType === "text") {
    if (!value) return <Td key={key} isBusy={isBusy}></Td>;
    const value_str = value.toString();
    if (value_str.length < 10 && !value_str.includes("\n")) {
      return (
        <Td key={key} isBusy={isBusy}>
          {value}
        </Td>
      );
    }
    return (
      <Td key={key} isBusy={isBusy}>
        <TextCell value={value}></TextCell>
      </Td>
    );
  }
  if (cellType === "group_id_name") {
    const group_id_name: Record<number, string> = add_values["group_id_name"];
    return (
      <Td key={key} isBusy={isBusy}>
        {group_id_name[Number(value)]}
      </Td>
    );
  }
  if (cellType === "user_id_name") {
    const user_id_name: Record<number, string> = add_values["user_id_name"];
    return (
      <Td key={key} isBusy={isBusy}>
        {user_id_name[Number(value)]}
      </Td>
    );
  }
  if (["gllms_status", "gvdbs_status"].includes(cellType)) {
    const cellText =
      row["gllms_status_text"] || row["gvdbs_status_text"] || "<Pending>";
    return (
      <Td key={key} className={"table-" + value} isBusy={isBusy}>
        {cellText}
      </Td>
    );
  }
  if (cellType === "api_settings_value") {
    if (pk_value_str === "webapp_main_color")
      return (
        <Td
          key={key}
          className="fw-bold"
          style={{
            backgroundColor: getColor(value_str, 300),
          }}
          isBusy={isBusy}
        >
          {value}
        </Td>
      );
    return (
      <Td key={key} isBusy={isBusy}>
        <TextCell value={value} rows={2}></TextCell>
      </Td>
    );
  }
  if (cellType === "datetime") {
    if (!value)
      return (
        <Td key={key} isBusy={isBusy}>
          -
        </Td>
      );
    const date = new Date(value as string);
    // Format date (e.g., "October 28, 2025")
    const dateString = date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });

    // Format time (e.g., "10:22:30 PM")
    const timeString = date.toLocaleTimeString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
    return (
      <Td key={key} isBusy={isBusy}>
        <div className="text-nowrap">{dateString}</div>
        <div className="text-nowrap">{timeString}</div>
      </Td>
    );
  }
  return (
    <Td key={key} isBusy={isBusy}>
      {value_str}
    </Td>
  );
}
