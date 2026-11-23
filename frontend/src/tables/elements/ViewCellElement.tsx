import { TableCell } from "@/components/ui/table";
import { cn } from "@/lib/utils";
import getColor from "../../api/getColor";
import { getRetrParamsShortNameFromFullStr } from "../../components/GVDBsRetrParams/functions";
import BooleanCheck from "../CellRenders/BooleanCheck";
import { BusyCell } from "../CellRenders/BusyCell";
import GaDocTasksAnswer from "../CellRenders/GaDocTasksAnswer";
import GaDocTasksQueryInfo from "../CellRenders/GaDocTasksQueryInfo";
import GVDBsRetrFiltersCell from "../CellRenders/GVDBsRetrFiltersCell";
import TextCell from "../CellRenders/TextCell";
import type { createTableStore, TableRow } from "../TableStoreFactory";

interface TdProps extends React.TdHTMLAttributes<HTMLTableCellElement> {
  isBusy: boolean | undefined;
}

function Td({ isBusy, className, children, ...props }: TdProps) {
  return (
    <TableCell {...props} className={cn("relative wrap-break-word", className)}>
      {children}
      <BusyCell isBusy={isBusy || false} />
    </TableCell>
  );
}

// gllms_status / gvdbs_status values are Bootstrap context names set by the server
const STATUS_CLASS: Record<string, string> = {
  success: "ok",
  warning: "warn",
  danger: "err",
};

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
      <Td key={key} isBusy={isBusy} className="min-w-44">
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
      <Td key={key} isBusy={isBusy}>
        <span
          className={cn(
            "status plain",
            STATUS_CLASS[value_str] || "off",
          )}
        >
          {cellText}
        </span>
      </Td>
    );
  }
  if (cellType === "api_settings_value") {
    if (pk_value_str === "webapp_main_color")
      return (
        <Td key={key} isBusy={isBusy}>
          {/* a swatch of the chosen ramp, not a theme colour */}
          <span
            className="inline-flex h-7 items-center rounded-full px-3 text-[13px] font-bold"
            style={{
              backgroundColor: getColor(value_str, 300),
              color: getColor(value_str, 900),
            }}
          >
            {value}
          </span>
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
        <div className="whitespace-nowrap">{dateString}</div>
        <div className="whitespace-nowrap">{timeString}</div>
      </Td>
    );
  }
  if (cellType === "ga_manage_doc_tasks__query_info") {
    return (
      <Td key={key} isBusy={isBusy}>
        <GaDocTasksQueryInfo row={row} />
      </Td>
    );
  }
  if (cellType === "ga_manage_doc_tasks__answer") {
    return (
      <Td
        key={key}
        isBusy={isBusy}
        className="align-top"
      >
        <GaDocTasksAnswer row={row} />
      </Td>
    );
  }
  if (cellType === "ga_manage_doc_tasks__text") {
    if (!value) return <Td key={key} isBusy={isBusy}></Td>;
    return (
      <Td key={key} isBusy={isBusy}>
        <TextCell value={value} rows={7}></TextCell>
      </Td>
    );
  }
  if (cellType === "gvdbs_retr_params") {
    return (
      <Td key={key} isBusy={isBusy}>
        <b className="font-semibold whitespace-nowrap tabular-nums">
          {getRetrParamsShortNameFromFullStr(value_str)}
        </b>
      </Td>
    );
  }
  if (cellType === "gvdbs_retr_filters") {
    return (
      <Td key={key} isBusy={isBusy}>
        <GVDBsRetrFiltersCell value={value} />
      </Td>
    );
  }

  return (
    <Td key={key} isBusy={isBusy}>
      {value_str}
    </Td>
  );
}
