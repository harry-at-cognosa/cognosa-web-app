import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";
import MarkdownRenderer from "../../../components/MarkdownRenderer";

function ResponseArea() {
  const { output_text } = useDocTasksCurrentStore();
  return (
    <div
      className="response-area p-3 overflow-auto bg-white"
      style={{
        wordWrap: "break-word",
        wordBreak: "break-word",
        overflowWrap: "break-word",
        whiteSpace: "pre-wrap", // Optional: preserves formatting but wraps
      }}
    >
      {output_text ? (
        <MarkdownRenderer content={output_text} />
      ) : (
        <p className="text-muted">
          <em>Response will appear here...</em>
        </p>
      )}
    </div>
  );
}

export default ResponseArea;
