import React, { useMemo } from 'react';
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
  // Utiliser useMemo pour éviter de tronquer et traiter le contenu à chaque rendu
  const displayContent = useMemo(() => {
    if (!content) return '';
    
    return truncate && content.length > maxLength
      ? content.substring(0, maxLength) + '...'
      : content;
  }, [content, truncate, maxLength]);

  // Mémoriser les composants pour éviter de les recréer à chaque rendu
  const markdownComponents = useMemo(() => ({
    // Override rendering for certain components when truncated
    h1: truncate ? ({ node, ...props }: { node?: any; [key: string]: any }) => <span className="font-bold text-base" {...props} /> : undefined,
    h2: truncate ? ({ node, ...props }: { node?: any; [key: string]: any }) => <span className="font-bold text-base" {...props} /> : undefined,
    h3: truncate ? ({ node, ...props }: { node?: any; [key: string]: any }) => <span className="font-semibold" {...props} /> : undefined,
    pre: truncate
      ? ({ node, ...props }: { node?: any; [key: string]: any }) => <span className="bg-gray-100 dark:bg-gray-800 px-1 rounded" {...props} />
      : undefined,
    code: ({ node, inline, className, children, ...props }: { node?: any; inline?: boolean; className?: string; children?: any; [key: string]: any }) => {
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
    img: truncate ? ({ node, ...props }: { node?: any; [key: string]: any }) => <span className="text-blue-500">[Image]</span> : undefined,
  }), [truncate]);

  if (!content) {
    return null;
  }

  return (
    <div className={`markdown-content text-sm ${className}`}>
      <ReactMarkdown
        rehypePlugins={[rehypeSanitize]}
        remarkPlugins={[remarkGfm]}
        components={markdownComponents}
      >
        {displayContent}
      </ReactMarkdown>
    </div>
  );
};

// Mémoriser le composant entier pour éviter les re-rendus inutiles quand les props ne changent pas
export default React.memo(MarkdownPreview);