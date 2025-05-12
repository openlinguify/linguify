import React, { useState } from 'react';
import { Clipboard, Check } from 'lucide-react';
import { highlight, languages } from 'prismjs';
import 'prismjs/components/prism-markup';
import './prism-theme.css';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-csharp';
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cpp';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-markdown';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-css';
import 'prismjs/components/prism-sass';
import 'prismjs/components/prism-less';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-php';
import 'prismjs/components/prism-ruby';
import 'prismjs/components/prism-rust';
import 'prismjs/components/prism-swift';
import 'prismjs/components/prism-dart';
import 'prismjs/components/prism-kotlin';

interface CodeBlockProps {
  language: string;
  value: string;
  className?: string;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ language, value, className = '' }) => {
  const [copied, setCopied] = useState(false);
  
  // Map markdown language identifiers to Prism language identifiers
  const languageMap: Record<string, string> = {
    'js': 'javascript',
    'ts': 'typescript',
    'py': 'python',
    'rb': 'ruby',
    'sh': 'bash',
    'shell': 'bash',
    'cs': 'csharp',
    'html': 'markup',
    'md': 'markdown',
    'yml': 'yaml',
    'jsx': 'jsx',
    'tsx': 'tsx',
  };
  
  // Get the language for highlighting
  const getLanguage = () => {
    const mappedLang = languageMap[language] || language;
    // Check if the language is supported by Prism
    if (languages[mappedLang]) {
      return mappedLang;
    }
    return 'text'; // Fallback
  };
  
  // Get syntax highlighted code
  const getHighlightedCode = () => {
    const lang = getLanguage();
    
    if (lang === 'text') {
      return value;
    }
    
    try {
      return highlight(value, languages[lang], lang);
    } catch (error) {
      console.warn(`Language '${lang}' is not supported for syntax highlighting`);
      return value;
    }
  };
  
  // Copy code to clipboard
  const copyToClipboard = () => {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  
  return (
    <div className={`code-block relative rounded-md overflow-hidden ${className}`}>
      <div className="code-header flex justify-between items-center py-1 px-4 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 font-mono">
          {language || 'text'}
        </div>
        <button
          onClick={copyToClipboard}
          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 focus:outline-none"
          title="Copy code"
        >
          {copied ? (
            <Check className="h-4 w-4 text-green-500" />
          ) : (
            <Clipboard className="h-4 w-4" />
          )}
        </button>
      </div>
      <pre className="m-0 p-4 bg-gray-50 dark:bg-gray-900 overflow-x-auto text-sm">
        {getLanguage() === 'text' ? (
          <code>{value}</code>
        ) : (
          <code
            dangerouslySetInnerHTML={{ __html: getHighlightedCode() }}
            className={`language-${getLanguage()}`}
          />
        )}
      </pre>
    </div>
  );
};

export default CodeBlock;