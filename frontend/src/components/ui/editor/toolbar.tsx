// src/components/ui/rich-editor/toolbar.tsx
import React from 'react';
import {
  Bold, Italic, Strikethrough, List, ListOrdered,
  Heading2, Quote, Undo, Redo, Link as LinkIcon,
  CheckSquare, Image as ImageIcon
} from 'lucide-react';
import { Toggle } from '../../toggle';
import { Separator } from '../../separator';
import { type Editor } from '@tiptap/react';

interface EditorToolbarProps {
  editor: Editor | null;
}

export function Toolbar({ editor }: EditorToolbarProps) {
  if (!editor) return null;

  const addImage = () => {
    // Create a file input element
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    
    // Handle file selection
    input.onchange = async (event) => {
      const file = (event.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      try {
        // Create a FormData object and append the file
        const formData = new FormData();
        formData.append('image', file);
        
        // For now, use a temporary URL for development
        // In production, this would upload to your server API
        const tempUrl = URL.createObjectURL(file);
        editor.chain().focus().setImage({ src: tempUrl }).run();
        
        // TODO: When backend API is ready, use this code instead:
        // const response = await fetch('/api/v1/notebook/upload-image', {
        //   method: 'POST',
        //   body: formData,
        // });
        // 
        // if (response.ok) {
        //   const data = await response.json();
        //   editor.chain().focus().setImage({ src: data.imageUrl }).run();
        // }
      } catch (error) {
        console.error('Failed to upload image:', error);
        alert('Failed to upload image. Please try again.');
      }
    };
    
    // Trigger file selection
    input.click();
  };

  const setLink = () => {
    const url = window.prompt('Enter URL:');
    if (url) {
      editor.chain().focus().setLink({ href: url }).run();
    }
  };

  return (
    <div className="p-2 border-b flex flex-wrap gap-2">
      {/* Text Formatting */}
      <Toggle
        size="sm"
        pressed={editor.isActive('bold')}
        onPressedChange={() => editor.chain().focus().toggleBold().run()}
      >
        <Bold className="h-4 w-4" />
      </Toggle>
      
      <Toggle
        size="sm"
        pressed={editor.isActive('italic')}
        onPressedChange={() => editor.chain().focus().toggleItalic().run()}
      >
        <Italic className="h-4 w-4" />
      </Toggle>
      
      <Toggle
        size="sm"
        pressed={editor.isActive('strike')}
        onPressedChange={() => editor.chain().focus().toggleStrike().run()}
      >
        <Strikethrough className="h-4 w-4" />
      </Toggle>

      <Separator orientation="vertical" className="h-6" />

      {/* Lists */}
      <Toggle
        size="sm"
        pressed={editor.isActive('bulletList')}
        onPressedChange={() => editor.chain().focus().toggleBulletList().run()}
      >
        <List className="h-4 w-4" />
      </Toggle>
      
      <Toggle
        size="sm"
        pressed={editor.isActive('orderedList')}
        onPressedChange={() => editor.chain().focus().toggleOrderedList().run()}
      >
        <ListOrdered className="h-4 w-4" />
      </Toggle>
      
      <Toggle
        size="sm"
        pressed={editor.isActive('taskList')}
        onPressedChange={() => editor.chain().focus().toggleTaskList().run()}
      >
        <CheckSquare className="h-4 w-4" />
      </Toggle>

      <Separator orientation="vertical" className="h-6" />

      {/* Headings and Block Quotes */}
      <Toggle
        size="sm"
        pressed={editor.isActive('heading', { level: 2 })}
        onPressedChange={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
      >
        <Heading2 className="h-4 w-4" />
      </Toggle>
      
      <Toggle
        size="sm"
        pressed={editor.isActive('blockquote')}
        onPressedChange={() => editor.chain().focus().toggleBlockquote().run()}
      >
        <Quote className="h-4 w-4" />
      </Toggle>

      <Separator orientation="vertical" className="h-6" />

      {/* Links and Images */}
      <Toggle
        size="sm"
        pressed={editor.isActive('link')}
        onPressedChange={setLink}
      >
        <LinkIcon className="h-4 w-4" />
      </Toggle>
      
      <Toggle
        size="sm"
        pressed={false}
        onPressedChange={addImage}
      >
        <ImageIcon className="h-4 w-4" />
      </Toggle>

      <Separator orientation="vertical" className="h-6" />

      {/* History */}
      <Toggle
        size="sm"
        disabled={!editor.can().undo()}
        onPressedChange={() => editor.chain().focus().undo().run()}
      >
        <Undo className="h-4 w-4" />
      </Toggle>
      
      <Toggle
        size="sm"
        disabled={!editor.can().redo()}
        onPressedChange={() => editor.chain().focus().redo().run()}
      >
        <Redo className="h-4 w-4" />
      </Toggle>
    </div>
  );
}