import { Table } from "react-bootstrap";
import { getRetrFiltersShortTableFromJSONStr } from "../../components/GVDBsRetrFilters/functions";
import { getRetrParamsShortNameFromShortStr } from "../../components/GVDBsRetrParams/functions";
import type { TableCellValue, TableRow } from "../TableStoreFactory";

function getPlacedAtStr(row: TableRow): string {
  if (!row["created_at"]) return "N/A";
  const date = new Date(row["created_at"] as string);
  // Format date (e.g., "October 28, 2025")
  const dateString = date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  // Format time (e.g., "10:22:30 PM")
  const timeString = date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
  return dateString + " " + timeString;
}

function secondsOrNA(seconds: TableCellValue) {
  if (seconds === null) return "N/A";
  return `${seconds} sec`;
}

interface Props {
  row: TableRow;
}

export default function GaDocTasksQueryInfo({ row }: Props) {
  const gvdbs_rf_rows = getRetrFiltersShortTableFromJSONStr(
    row["gvdbs_cfg"] as string,
  );
  return (
    <table>
      <tbody>
        <tr>
          <th className="text-end pe-2">Placed at:</th>
          <td className="text-start">{getPlacedAtStr(row)}</td>
        </tr>
        {row["short_name"] ? (
          <tr>
            <th className="text-end pe-2">Short Name:</th>
            <td className="text-start">{row["short_name"]}</td>
          </tr>
        ) : null}
        <tr>
          <th className="text-end pe-2">Collection:</th>
          <td className="text-start">{row["gvdbs_name"]}</td>
        </tr>
        {row["gvdbs_cfg"] ? (
          <tr>
            <th className="text-end pe-2">Retrieval Params:</th>
            <td className="text-start">
              {getRetrParamsShortNameFromShortStr(row["gvdbs_cfg"].toString())}
            </td>
          </tr>
        ) : null}
        {gvdbs_rf_rows ? (
          <tr>
            <th className="text-end pe-2">Retrieval Filters:</th>
            <td className="text-start">
              <Table bordered className="mb-0">
                <tbody>
                  {gvdbs_rf_rows.map((row, i) => (
                    <tr key={i}>
                      <td
                        className={"text-nowrap py-0"}
                        style={{ width: "1%", backgroundColor: "#fff0" }}
                      >
                        {row.short_title}
                      </td>
                      <td className="py-0" style={{ backgroundColor: "#fff0" }}>
                        {row.global_not ? (
                          <span
                            className="me-2 pb-1"
                            style={{ color: "#e00000" }}
                          >
                            NOT:
                          </span>
                        ) : null}
                        {row.value}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </td>
          </tr>
        ) : null}
        <tr>
          <th className="text-end pe-2">LLM:</th>
          <td className="text-start">{row["gllms_name"]}</td>
        </tr>
        <tr>
          <th className="text-end pe-2">VectorDB/LLM time:</th>
          <td className="text-start">
            {secondsOrNA(row["vdb_query_seconds"]) +
              " / " +
              secondsOrNA(row["llm_query_seconds"])}
          </td>
        </tr>
        <tr>
          <th className="text-end pe-2">Tokens Sent/Recv:</th>
          <td className="text-start">
            {row["llm_tokens_sent"] || "N/A"}
            {" / "}
            {row["llm_tokens_received"] || "N/A"}
          </td>
        </tr>
        <tr>
          <th className="text-end pe-2">Status:</th>
          <td
            className="text-start"
            style={{
              color: row["status_str"] === "error" ? "red" : "black",
            }}
          >
            {row["status_str"]}
          </td>
        </tr>
        <tr>
          <th className="text-end pe-2"></th>
          <td className="text-start"></td>
        </tr>
        <tr>
          <th className="text-end pe-2"></th>
          <td className="text-start"></td>
        </tr>
      </tbody>
    </table>
  );
}
