import { write, utils } from "xlsx";

const EXCEL_MAX_CELL_LENGTH = 32700;
const ELLIPSIS = "...";

export interface ExcelExportColumnDefinition {
  key: string; // The property name in your data object
  header?: string; // The display name in the Excel file
}

export interface ExcelExportOptions {
  fileName: string;
  sheetName: string;
  columns: ExcelExportColumnDefinition[]; // Define columns in order with custom headers
  autoWidthPadding?: number; // Additional padding for column width
}

export const useExcelExport = () => {
  const processCellValue = (value: any): any => {
    if (typeof value === "string") {
      if (value.length > EXCEL_MAX_CELL_LENGTH) {
        const availableLength = EXCEL_MAX_CELL_LENGTH - ELLIPSIS.length;
        return value.substring(0, availableLength) + ELLIPSIS;
      }
    }
    return value;
  };
  const exportToExcel = <T extends Record<string, any>>(
    rowList: T[],
    options: ExcelExportOptions
  ) => {
    const { fileName, sheetName, columns, autoWidthPadding = 2 } = options;
    const data = rowList;

    let worksheetData: any[];
    let headerNames: string[];

    // Use specified columns in order
    worksheetData = data.map((row) => {
      const newRow: Record<string, any> = {};
      columns.forEach((col) => {
        const displayKey = col.header || col.key;
        newRow[displayKey] = processCellValue(row[col.key]);
      });
      return newRow;
    });
    headerNames = columns.map((col) => col.header || col.key);

    // Create worksheet
    const worksheet = utils.json_to_sheet(worksheetData);

    // Calculate optimal column widths
    if (worksheet["!ref"] && headerNames.length > 0) {
      const range = utils.decode_range(worksheet["!ref"]);
      const columnWidths = [];

      for (let C = range.s.c; C <= range.e.c; C++) {
        const colName = headerNames[C];

        // Calculate header width
        const headerWidth = colName ? String(colName).length : 0;

        // Calculate max content width for this column (capped for display)
        let maxWidth = headerWidth;
        for (let R = 1; R <= range.e.r; R++) {
          const cellAddress = utils.encode_cell({ c: C, r: R });
          const cell = worksheet[cellAddress];
          if (cell && cell.v !== undefined) {
            // For width calculation, we don't need the full length if it's truncated
            const displayValue = String(cell.v);
            const cellWidth =
              displayValue.length > 50 ? 50 : displayValue.length; // Cap at 50 for display purposes
            if (cellWidth > maxWidth) {
              maxWidth = cellWidth;
            }
          }
        }

        const finalWidth = Math.min(
          Math.max(maxWidth + autoWidthPadding, 8),
          50
        );
        columnWidths.push({ wch: finalWidth });
      }

      worksheet["!cols"] = columnWidths;
    }

    // Create workbook
    const workbook = utils.book_new();
    utils.book_append_sheet(workbook, worksheet, sheetName);

    // Generate Excel file as ArrayBuffer
    const excelBuffer = write(workbook, { bookType: "xlsx", type: "array" });

    // Create Blob
    const blob = new Blob([excelBuffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    // Universal download approach
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;

    // For Safari
    if (
      typeof navigator !== "undefined" &&
      /iPad|iPhone|iPod|Safari/.test(navigator.userAgent)
    ) {
      link.target = "_blank";
    }

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return { exportToExcel };
};
