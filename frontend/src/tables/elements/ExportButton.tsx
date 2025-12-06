import { Button } from "react-bootstrap";
import {
  useExcelExport,
  type ExcelExportColumnDefinition,
} from "../hooks/useExcelExport";
import type { createTableStore, TableRow } from "../TableStoreFactory";
import { FileEarmark } from "react-bootstrap-icons";
import { useJsonExport } from "../hooks/useJSONExport";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
  row?: TableRow | undefined;
}
function getCurrentDateTimeString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0"); // Month is 0-indexed
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");
  return `${year}_${month}_${day}_${hours}_${minutes}_${seconds}`;
}

function getFilename(title: string, fileExt: string) {
  return (
    title.replace(" ", "_") + "_" + getCurrentDateTimeString() + "." + fileExt
  );
}

export default function ExportButton({ useStore, row }: Props) {
  const { exportToExcel } = useExcelExport();
  const { exportToJson } = useJsonExport();
  const tableStore = useStore();
  const exportList = tableStore.data?.table_options.export || [];
  if (!exportList.length) return null;

  const handleExportExcel = () => {
    const data = tableStore.data;
    if (!data) return;
    const columns: ExcelExportColumnDefinition[] = [];
    if (data.table_options.export_columns) {
      for (const [col_index, col] of Object.entries(
        data.table_options.export_columns
      )) {
        const ecd = data.table_options.export_columns_display;
        const header = (ecd && ecd[Number(col_index)]) || col;
        columns.push({ key: col, header });
      }
    } else {
      for (const col of data.table_options.read__visible_columns) {
        columns.push({
          key: col,
          header: data.columns[col]?.display || col,
        });
      }
    }

    exportToExcel(row ? [row] : data.rows, {
      fileName: getFilename(tableStore.title, "xlsx"),
      sheetName: tableStore.title,
      columns,
    });
  };

  const handleExportJSON = () => {
    const data = tableStore.data;
    if (!data) return;
    exportToJson(row ? [row] : data.rows, {
      fileName: getFilename(tableStore.title, "json"),
      indent: 2,
      sortKeys: true,
      onlyKeys: data.table_options.export_columns,
    });
  };
  return (
    <>
      <span className="pt-1">Export:&nbsp;</span>
      {exportList.includes("xlsx-current") ? (
        <Button
          type="button"
          variant=""
          className="fw-bold py-0 me-1 btn-tc-300-400"
          style={{
            fontSize: "smaller",
          }}
          onClick={handleExportExcel}
        >
          <FileEarmark size={"16px"} /> Excel
        </Button>
      ) : null}
      {exportList.includes("json-current") ? (
        <Button
          type="button"
          variant=""
          className="fw-bold py-0 btn-tc-300-400"
          style={{
            fontSize: "smaller",
          }}
          onClick={handleExportJSON}
        >
          <FileEarmark size={"16px"} /> JSON
        </Button>
      ) : null}
    </>
  );
}
