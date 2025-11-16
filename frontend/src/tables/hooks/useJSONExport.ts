export interface JsonExportOptions {
  fileName: string;
  indent: number; // JSON indentation (default: 2)
  sortKeys: boolean; // Whether to sort object keys alphabetically
}

export const useJsonExport = () => {
  const exportToJson = <T extends Record<string, any> | any[]>(
    data: T,
    options: JsonExportOptions
  ) => {
    const { fileName, indent, sortKeys } = options;

    // Function to sort object keys recursively
    const sortObjectKeys = (obj: any): any => {
      if (obj === null || typeof obj !== "object" || Array.isArray(obj)) {
        return obj;
      }

      const sortedObj: any = {};
      const keys = sortKeys ? Object.keys(obj).sort() : Object.keys(obj);

      keys.forEach((key) => {
        const value = obj[key];
        if (
          value !== null &&
          typeof value === "object" &&
          !Array.isArray(value)
        ) {
          sortedObj[key] = sortObjectKeys(value);
        } else if (Array.isArray(value)) {
          sortedObj[key] = value.map((item) =>
            item !== null && typeof item === "object" && !Array.isArray(item)
              ? sortObjectKeys(item)
              : item
          );
        } else {
          sortedObj[key] = value;
        }
      });

      return sortedObj;
    };

    // Process data to sort keys if requested
    const processedData = sortKeys ? sortObjectKeys(data) : data;

    // Convert to prettified JSON string
    const jsonString = JSON.stringify(processedData, null, indent);

    // Create Blob
    const blob = new Blob([jsonString], {
      type: "application/json",
    });

    // Create download
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;

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

  return { exportToJson };
};
