import React from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';
import rehypeHighlight from 'rehype-highlight';
import remarkGfm from 'remark-gfm';
import './markdown-styles.css';
import CodeBlock from './CodeBlock';

interface MarkdownPreviewProps {
  content: string;
  className?: string;
  truncate?: boolean;
  maxLength?: number;
}

const MarkdownPreview: React.FC<MarkdownPreviewProps> = ({
  content,
  className = '',
  truncate = false,
  maxLength = 150,
}) => {
  // If truncate is true, limit content length
  const displayContent = truncate && content.length > maxLength
    ? content.substring(0, maxLength) + '...'
    : content;

  if (!content) {
    return null;
  }

  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        rehypePlugins={[rehypeSanitize]}
        remarkPlugins={[remarkGfm]}
        className="text-sm"
        components={{
          // Override rendering for certain components when truncated
          h1: truncate ? ({ node, ...props }) => <span className="font-bold text-base" {...props} /> : undefined,
          h2: truncate ? ({ node, ...props }) => <span className="font-bold text-base" {...props} /> : undefined,
          h3: truncate ? ({ node, ...props }) => <span className="font-semibold" {...props} /> : undefined,
          pre: truncate
            ? ({ node, ...props }) => <span className="bg-gray-100 dark:bg-gray-800 px-1 rounded" {...props} />
            : undefined,
          code: ({ node, inline, className, children, ...props }) => {
            if (truncate) {
              return <span className="bg-gray-100 dark:bg-gray-800 px-1 rounded text-xs">{children}</span>;
            }

            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';

            return !inline && language ? (
              <CodeBlock
                language={language}
                value={String(children).replace(/\n$/, '')}
              />
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          img: truncate ? ({ node, ...props }) => <span className="text-blue-500">[Image]</span> : undefined,
        }}
      >
        {displayContent}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownPreview;