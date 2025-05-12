import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';
import rehypeHighlight from 'rehype-highlight';
import remarkGfm from 'remark-gfm';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Bold,
  Italic,
  List,
  ListOrdered,
  Code,
  Link as LinkIcon,
  Image,
  Quote,
  Divide,
  Type,
  Languages,
  Check,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  minHeight?: string;
  maxHeight?: string;
  language?: string;
  isTranslation?: boolean;
}

const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  value,
  onChange,
  placeholder = 'Write your content here...',
  className = '',
  minHeight = '300px',
  maxHeight = '60vh',
  language,
  isTranslation = false,
}) => {
  const [mode, setMode] = useState<'write' | 'preview'>('write');
  const [fullscreen, setFullscreen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [selectionStart, setSelectionStart] = useState(0);
  const [selectionEnd, setSelectionEnd] = useState(0);

  // Tracking textarea selection
  const handleSelect = () => {
    if (textareaRef.current) {
      setSelectionStart(textareaRef.current.selectionStart);
      setSelectionEnd(textareaRef.current.selectionEnd);
    }
  };

  // Update selection
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.addEventListener('select', handleSelect);
      textarea.addEventListener('click', handleSelect);
      textarea.addEventListener('keyup', handleSelect);
      
      return () => {
        textarea.removeEventListener('select', handleSelect);
        textarea.removeEventListener('click', handleSelect);
        textarea.removeEventListener('keyup', handleSelect);
      };
    }
  }, []);

  // Markdown formatting helpers
  const insertMarkdown = (prefix: string, suffix: string = '') => {
    if (!textareaRef.current) return;
    
    const textarea = textareaRef.current;
    const start = selectionStart;
    const end = selectionEnd;
    const text = value;
    
    const newText = text.substring(0, start) + prefix + text.substring(start, end) + suffix + text.substring(end);
    onChange(newText);
    
    // Focus and set cursor position after update
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + prefix.length,
        end + prefix.length
      );
      handleSelect();
    }, 0);
  };

  // UI for editor toolbar
  const renderToolbar = () => (
    <div className="flex flex-wrap items-center gap-1 pb-2 border-b dark:border-gray-700">
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('**', '**')} 
        title="Bold"
      >
        <Bold className="h-4 w-4" />
      </Button>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('*', '*')} 
        title="Italic"
      >
        <Italic className="h-4 w-4" />
      </Button>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('- ')} 
        title="Bullet List"
      >
        <List className="h-4 w-4" />
      </Button>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('1. ')} 
        title="Ordered List"
      >
        <ListOrdered className="h-4 w-4" />
      </Button>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('`', '`')} 
        title="Inline Code"
      >
        <Code className="h-4 w-4" />
      </Button>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('\n```\n', '\n```\n')} 
        title="Code Block"
      >
        <Type className="h-4 w-4" />
      </Button>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('[', '](url)')} 
        title="Link"
      >
        <LinkIcon className="h-4 w-4" />
      </Button>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('![alt text](', ')')} 
        title="Image"
      >
        <Image className="h-4 w-4" />
      </Button>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('> ')} 
        title="Quote"
      >
        <Quote className="h-4 w-4" />
      </Button>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => insertMarkdown('\n---\n')} 
        title="Horizontal Rule"
      >
        <Divide className="h-4 w-4" />
      </Button>
      
      <div className="flex-1"></div>
      
      {language && (
        <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-gray-100 dark:bg-gray-800">
          <Languages className="h-3 w-3 text-gray-500 dark:text-gray-400" />
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {isTranslation ? 'Translation' : language.toUpperCase()}
          </span>
        </div>
      )}
      
      <Tabs value={mode} onValueChange={(v) => setMode(v as 'write' | 'preview')}>
        <TabsList className="h-8">
          <TabsTrigger value="write" className="text-xs px-2 py-1">
            Write
          </TabsTrigger>
          <TabsTrigger value="preview" className="text-xs px-2 py-1">
            Preview
          </TabsTrigger>
        </TabsList>
      </Tabs>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => setFullscreen(!fullscreen)} 
        title={fullscreen ? "Exit Fullscreen" : "Fullscreen"}
        className="ml-1"
      >
        {fullscreen ? (
          <Minimize2 className="h-4 w-4" />
        ) : (
          <Maximize2 className="h-4 w-4" />
        )}
      </Button>
    </div>
  );

  // Markdown preview renderer
  const renderMarkdownPreview = () => (
    <div 
      className="prose dark:prose-invert prose-sm max-w-none p-4 overflow-auto bg-gray-50 dark:bg-gray-800 rounded-md"
      style={{ minHeight, maxHeight: fullscreen ? '100%' : maxHeight }}
    >
      {value ? (
        <ReactMarkdown
          rehypePlugins={[rehypeSanitize, rehypeHighlight]}
          remarkPlugins={[remarkGfm]}
        >
          {value}
        </ReactMarkdown>
      ) : (
        <div className="text-gray-400 italic">Nothing to preview</div>
      )}
    </div>
  );

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className={`markdown-editor w-full ${fullscreen ? 'fixed inset-0 z-50 p-6 bg-white dark:bg-gray-900' : ''} ${className}`}
      >
        {renderToolbar()}
        
        {mode === 'write' ? (
          <Textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="mt-2 font-mono resize-none w-full rounded-md border-0 bg-transparent focus-visible:ring-0"
            style={{ 
              minHeight,
              maxHeight: fullscreen ? '100%' : maxHeight,
              height: fullscreen ? 'calc(100vh - 150px)' : undefined
            }}
          />
        ) : (
          renderMarkdownPreview()
        )}
        
        {fullscreen && (
          <div className="absolute bottom-6 right-6">
            <Button
              onClick={() => setFullscreen(false)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-lg"
            >
              <Check className="h-4 w-4 mr-1" />
              Done
            </Button>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
};

export default MarkdownEditor;