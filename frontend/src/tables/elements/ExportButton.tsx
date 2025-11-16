import { Button } from "react-bootstrap";
import {
  useExcelExport,
  type ExcelExportColumnDefinition,
} from "../hooks/useExcelExport";
import type { createTableStore } from "../TableStoreFactory";
import { FileEarmark } from "react-bootstrap-icons";
import { useState } from "react";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";
import { useJsonExport } from "../hooks/useJSONExport";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
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

export default function ExportButton({ useStore }: Props) {
  const [isHovered1, setIsHovered1] = useState(false);
  const [isHovered2, setIsHovered2] = useState(false);
  const { color } = useWebAppOptionsStore();
  const { exportToExcel } = useExcelExport();
  const { exportToJson } = useJsonExport();
  const tableStore = useStore();
  const exportList = tableStore.data?.table_options.export || [];
  if (!exportList.length) return null;

  const handleExportExcel = () => {
    const data = tableStore.data;
    if (!data) return;
    const columns: ExcelExportColumnDefinition[] = [];
    for (const col of data.table_options.read__visible_columns) {
      columns.push({
        key: col,
        header: data.columns[col].display || col,
      });
    }
    exportToExcel(data.rows, {
      fileName: getFilename(tableStore.title, "xlsx"),
      sheetName: tableStore.title,
      columns,
    });
  };
  const handleExportJSON = () => {
    const data = tableStore.data;
    if (!data) return;
    exportToJson(data.rows, {
      fileName: getFilename(tableStore.title, "json"),
      indent: 2,
      sortKeys: true,
    });
  };
  return (
    <>
      <span className="pt-1">Export:&nbsp;</span>
      <Button
        type="button"
        variant="warning"
        className="fw-bold py-0 me-1"
        style={{
          fontSize: "smaller",
          backgroundColor: isHovered1 ? color.c400 : color.c300,
        }}
        onMouseEnter={() => setIsHovered1(true)}
        onMouseLeave={() => setIsHovered1(false)}
        onClick={handleExportExcel}
      >
        <FileEarmark size={"16px"} /> Excel
      </Button>
      <Button
        type="button"
        variant="warning"
        className="fw-bold py-0"
        style={{
          fontSize: "smaller",
          backgroundColor: isHovered2 ? color.c400 : color.c300,
        }}
        onMouseEnter={() => setIsHovered2(true)}
        onMouseLeave={() => setIsHovered2(false)}
        onClick={handleExportJSON}
      >
        <FileEarmark size={"16px"} /> JSON
      </Button>
    </>
  );
}
