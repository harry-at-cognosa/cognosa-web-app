import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";

/** VectorDB/LLM time and tokens sent/received of the query on show. */
export default function QueryTokensCounter() {
  const current = useDocTasksCurrentStore();

  const tokensCounterVisible =
    (current.vdb_query_seconds ||
      current.llm_query_seconds ||
      current.llm_tokens_sent ||
      current.llm_tokens_received) !== null;
  function secondsOrNA(seconds: number | null) {
    if (seconds === null) return "N/A";
    return `${seconds} sec`;
  }
  if (!tokensCounterVisible) return null;
  const items: [string, string | number][] = [
    ["VectorDB", secondsOrNA(current.vdb_query_seconds)],
    ["LLM", secondsOrNA(current.llm_query_seconds)],
    ["Tokens sent", current.llm_tokens_sent || "N/A"],
    ["received", current.llm_tokens_received || "N/A"],
  ];
  return (
    <dl className="ml-auto flex flex-wrap justify-end gap-x-4 gap-y-0.5 text-[13px] text-muted-foreground tabular-nums">
      {items.map(([k, v]) => (
        <div key={k} className="flex gap-1.5 whitespace-nowrap">
          <dt>{k}</dt>
          <dd className="font-semibold text-ink">{v}</dd>
        </div>
      ))}
    </dl>
  );
}
