import type { createTableStore, TableRow } from "../TableStoreFactory";
import ColumnDisplayName from "./ColumnDisplayName";
import ViewCellElement from "./ViewCellElement";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
  row: TableRow;
  cols: string[];
}

// One labelled box per column: the name, then the value as the table shows it.
// Used by the View and the Confirm delete dialogs.
export default function RowValues({ useStore, row, cols }: Props) {
  const { data } = useStore();
  if (!data) return null;
  return (
    <div className="grid gap-3">
      {cols.map((col) => (
        <table
          key={col + "__col_table"}
          className="w-full table-fixed border-separate border-spacing-0 overflow-hidden rounded-2xl border border-line text-sm"
        >
          <tbody>
            <tr key={col + "__col_name"}>
              <th className="bg-sunk px-3 py-1.5 text-left text-[13px] font-semibold text-ink-2">
                <ColumnDisplayName
                  nameType="dialog"
                  data={data}
                  col={col}
                ></ColumnDisplayName>
              </th>
            </tr>
            <tr key={col + "__col_value"}>
              <ViewCellElement
                useStore={useStore}
                row={row}
                col={col}
              ></ViewCellElement>
            </tr>
          </tbody>
        </table>
      ))}
    </div>
  );
}
