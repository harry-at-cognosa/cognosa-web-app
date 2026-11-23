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

const TH =
  "py-px pr-2 text-right align-middle font-semibold whitespace-nowrap text-ink-2";
const TD = "py-px text-left align-middle";

interface Props {
  row: TableRow;
}

export default function GaDocTasksQueryInfo({ row }: Props) {
  const gvdbs_rf_rows = getRetrFiltersShortTableFromJSONStr(
    row["gvdbs_cfg"] as string,
  );
  return (
    <table className="text-[13px] leading-snug">
      <tbody>
        <tr>
          <th className={TH}>Placed at:</th>
          <td className={TD}>{getPlacedAtStr(row)}</td>
        </tr>
        {row["short_name"] ? (
          <tr>
            <th className={TH}>Short Name:</th>
            <td className={TD}>{row["short_name"]}</td>
          </tr>
        ) : null}
        <tr>
          <th className={TH}>Collection:</th>
          <td className={TD}>{row["gvdbs_name"]}</td>
        </tr>
        {row["gvdbs_cfg"] ? (
          <tr>
            <th className={TH}>Retrieval Params:</th>
            <td className={TD}>
              {getRetrParamsShortNameFromShortStr(row["gvdbs_cfg"].toString())}
            </td>
          </tr>
        ) : null}
        {gvdbs_rf_rows ? (
          <tr>
            <th className={TH}>Retrieval Filters:</th>
            <td className={TD}>
              <table className="w-full border-collapse">
                <tbody>
                  {gvdbs_rf_rows.map((row, i) => (
                    <tr key={i}>
                      <td className="w-px border border-line px-1.5 py-px whitespace-nowrap">
                        {row.short_title}
                      </td>
                      <td className="border border-line px-1.5 py-px">
                        {row.global_not ? (
                          <span className="mr-2 font-semibold text-err">
                            NOT:
                          </span>
                        ) : null}
                        {row.value}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </td>
          </tr>
        ) : null}
        <tr>
          <th className={TH}>LLM:</th>
          <td className={TD}>{row["gllms_name"]}</td>
        </tr>
        <tr>
          <th className={TH}>VectorDB/LLM time:</th>
          <td className={TD}>
            {secondsOrNA(row["vdb_query_seconds"]) +
              " / " +
              secondsOrNA(row["llm_query_seconds"])}
          </td>
        </tr>
        <tr>
          <th className={TH}>Tokens Sent/Recv:</th>
          <td className={TD}>
            {row["llm_tokens_sent"] || "N/A"}
            {" / "}
            {row["llm_tokens_received"] || "N/A"}
          </td>
        </tr>
        <tr>
          <th className={TH}>Status:</th>
          <td
            className={
              row["status_str"] === "error" ? TD + " text-err" : TD
            }
          >
            {row["status_str"]}
          </td>
        </tr>
        <tr>
          <th className={TH}></th>
          <td className={TD}></td>
        </tr>
        <tr>
          <th className={TH}></th>
          <td className={TD}></td>
        </tr>
      </tbody>
    </table>
  );
}
