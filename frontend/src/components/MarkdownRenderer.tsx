import React from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import "highlight.js/styles/github-dark.css";
import "./MarkdownRenderer.css";
import { cn } from "@/lib/utils";

interface MarkdownRendererProps {
  content: string;
  /** added to the `md` typography block (e.g. "chat" for the denser chat size) */
  className?: string;
}

/** Answers are Markdown. Typography is the .md block in index.css. */
const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
  className,
}) => {
  return (
    <div className={cn("md", className)}>
      <ReactMarkdown
        // GitHub-flavoured Markdown: tables, strikethrough, task lists, bare links
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw, rehypeHighlight]}
        components={{
          // The wrapper lets a wide table scroll sideways inside the answer.
          table: ({ children }) => (
            <div className="md-table-wrap">
              <table>{children}</table>
            </div>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
