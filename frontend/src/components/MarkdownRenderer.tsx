import React from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";

interface MarkdownRendererProps {
  content: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        rehypePlugins={[rehypeRaw, rehypeHighlight]}
        components={
          {
            //   h1: ({ children }) => (
            //     <h1 className="text-2xl font-bold mt-6 mb-3">{children}</h1>
            //   ),
            //   h2: ({ children }) => (
            //     <h2 className="text-xl font-semibold mt-5 mb-2">{children}</h2>
            //   ),
            //   p: ({ children }) => (
            //     <p className="mb-4 leading-relaxed">{children}</p>
            //   ),
            //   code: ({ className, children }) => {
            //     //const match = /language-(\w+)/.exec(className || "");
            //     return (
            //       <pre
            //         className="bg-gray-900 rounded-lg overflow-x-auto"
            //         style={{ color: "red", marginBottom: 0 }}
            //       >
            //         <code className={className}>{children}</code>
            //       </pre>
            //     );
            //   },
            //   ul: ({ children }) => (
            //     <ul className="list-disc pl-5 mb-4">{children}</ul>
            //   ),
            //   ol: ({ children }) => (
            //     <ol className="list-decimal pl-5 mb-4">{children}</ol>
            //   ),
            //   li: ({ children }) => <li className="mb-1">{children}</li>,
            //   a: ({ children, href }) => (
            //     <a
            //       href={href}
            //       target="_blank"
            //       rel="noopener noreferrer"
            //       className="text-blue-400 hover:underline"
            //     >
            //       {children}
            //     </a>
            //   ),
          }
        }
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
