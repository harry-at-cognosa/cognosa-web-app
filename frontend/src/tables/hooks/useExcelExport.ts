import { write, utils } from "xlsx";

export interface ExcelExportColumnDefinition {
  key: string; // The property name in your data object
  header?: string; // The display name in the Excel file
}

export interface ExcelExportOptions {
  fileName?: string;
  sheetName?: string;
  columns?: ExcelExportColumnDefinition[]; // Define columns in order with custom headers
  autoWidthPadding?: number; // Additional padding for column width
}

export const useExcelExport = () => {
  const exportToExcel = <T extends Record<string, any>>(
    data: T[],
    options: ExcelExportOptions = {}
  ) => {
    const {
      fileName = "data.xlsx",
      sheetName = "Sheet1",
      columns = [],
      autoWidthPadding = 2,
    } = options;

    let worksheetData: any[];
    let headers: string[];

    if (columns.length > 0) {
      // Use specified columns in order
      worksheetData = data.map((row) => {
        const newRow: Record<string, any> = {};
        columns.forEach((col) => {
          const displayKey = col.header || col.key;
          newRow[displayKey] = row[col.key];
        });
        return newRow;
      });
      headers = columns.map((col) => col.header || col.key);
    } else {
      // Use all keys from first row (default order)
      worksheetData = data.map((row) => ({ ...row }));
      headers = data.length > 0 ? Object.keys(data[0]) : [];
    }

    // Create worksheet
    const worksheet = utils.json_to_sheet(worksheetData);

    // Calculate and set column widths
    if (worksheet["!ref"]) {
      const range = utils.decode_range(worksheet["!ref"]);
      const columnWidths = [];

      for (let C = range.s.c; C <= range.e.c; C++) {
        const cellAddress = utils.encode_cell({ c: C, r: 0 }); // Header row
        const cell = worksheet[cellAddress];

        let headerText = cell ? cell.v : "";
        if (columns.length > 0) {
          // Get header from columns definition
          const colIndex = C;
          if (colIndex < columns.length) {
            headerText = columns[colIndex].header || columns[colIndex].key;
          }
        } else if (headers[C]) {
          headerText = headers[C];
        }

        // Calculate width based on header length + padding
        const width = Math.min(
          Math.max(String(headerText).length + autoWidthPadding, 8),
          50
        );
        columnWidths.push({ wch: width });
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
