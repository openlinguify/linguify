// src/addons/notebook/components/NoteTemplates.tsx
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Template, 
  Copy, 
  Plus, 
  Bookmark,
  Edit, 
  Trash2, 
  Languages, 
  BookOpenText,
  Check,
  Pencil,
  Star,
  StarOff
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Note } from '@/addons/notebook/types';
import { gradientText } from "@/styles/gradient_style";

interface NoteTemplate {
  id: string;
  title: string;
  description: string;
  content: string;
  note_type: string;
  language: string;
  isPinned: boolean;
  createdAt: string;
}

// Language options for the template
const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'fr', label: 'French' },
  { value: 'es', label: 'Spanish' },
  { value: 'de', label: 'German' },
  { value: 'it', label: 'Italian' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'nl', label: 'Dutch' },
];

interface NoteTemplatesProps {
  onSelectTemplate: (template: Partial<Note>) => void;
}

export function NoteTemplates({ onSelectTemplate }: NoteTemplatesProps) {
  const [templates, setTemplates] = useState<NoteTemplate[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<NoteTemplate | null>(null);
  const [newTemplate, setNewTemplate] = useState<Partial<NoteTemplate>>({
    title: '',
    description: '',
    content: '',
    note_type: 'VOCABULARY',
    language: 'fr',
    isPinned: false,
  });

  // Load templates from localStorage
  useEffect(() => {
    const savedTemplates = localStorage.getItem('note_templates');
    if (savedTemplates) {
      try {
        setTemplates(JSON.parse(savedTemplates));
      } catch (error) {
        console.error('Failed to parse templates:', error);
      }
    } else {
      // Initialize with some default templates
      const defaultTemplates = [
        {
          id: '1',
          title: 'Vocabulary Note',
          description: 'Template for vocabulary notes with translation and examples',
          content: '<h2>Definition</h2><p>Enter definition here</p><h2>Translation</h2><p>Enter translation here</p><h2>Example Sentences</h2><ul><li>Example 1</li><li>Example 2</li></ul>',
          note_type: 'VOCABULARY',
          language: 'fr',
          isPinned: true,
          createdAt: new Date().toISOString(),
        },
        {
          id: '2',
          title: 'Grammar Rule',
          description: 'Template for grammar rules with explanations and examples',
          content: '<h2>Grammar Rule</h2><p>Explain the rule here</p><h2>Usage</h2><p>When to use this rule</p><h2>Examples</h2><ul><li>Example 1</li><li>Example 2</li></ul>',
          note_type: 'GRAMMAR',
          language: 'fr',
          isPinned: false,
          createdAt: new Date().toISOString(),
        },
        {
          id: '3',
          title: 'Cultural Note',
          description: 'Template for cultural knowledge and context',
          content: '<h2>Cultural Concept</h2><p>Describe the cultural concept here</p><h2>Context</h2><p>Provide historical or social context</p><h2>Importance</h2><p>Why this is important to understand</p>',
          note_type: 'CULTURE',
          language: 'fr',
          isPinned: false,
          createdAt: new Date().toISOString(),
        },
      ];
      
      setTemplates(defaultTemplates);
      localStorage.setItem('note_templates', JSON.stringify(defaultTemplates));
    }
  }, []);

  // Save templates to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('note_templates', JSON.stringify(templates));
  }, [templates]);

  const handleCreateTemplate = () => {
    if (!newTemplate.title) return;
    
    const template: NoteTemplate = {
      id: Date.now().toString(),
      title: newTemplate.title || '',
      description: newTemplate.description || '',
      content: newTemplate.content || '',
      note_type: newTemplate.note_type || 'VOCABULARY',
      language: newTemplate.language || 'fr',
      isPinned: newTemplate.isPinned || false,
      createdAt: new Date().toISOString(),
    };
    
    setTemplates([...templates, template]);
    setNewTemplate({
      title: '',
      description: '',
      content: '',
      note_type: 'VOCABULARY',
      language: 'fr',
      isPinned: false,
    });
    setIsCreateDialogOpen(false);
  };

  const handleUpdateTemplate = () => {
    if (!selectedTemplate || !selectedTemplate.title) return;
    
    const updatedTemplates = templates.map(template => 
      template.id === selectedTemplate.id ? selectedTemplate : template
    );
    
    setTemplates(updatedTemplates);
    setIsEditDialogOpen(false);
  };

  const handleDeleteTemplate = (templateId: string) => {
    if (!confirm('Are you sure you want to delete this template?')) return;
    
    const updatedTemplates = templates.filter(template => template.id !== templateId);
    setTemplates(updatedTemplates);
  };

  const handleTogglePinned = (templateId: string) => {
    const updatedTemplates = templates.map(template => 
      template.id === templateId 
        ? { ...template, isPinned: !template.isPinned } 
        : template
    );
    
    setTemplates(updatedTemplates);
  };

  const handleEditTemplate = (template: NoteTemplate) => {
    setSelectedTemplate(template);
    setIsEditDialogOpen(true);
  };

  const handleUseTemplate = (template: NoteTemplate) => {
    onSelectTemplate({
      title: '',
      content: template.content,
      note_type: template.note_type,
      language: template.language,
      example_sentences: [],
      related_words: [],
    });
  };

  // Sort templates with pinned first, then by creation date
  const sortedTemplates = [...templates].sort((a, b) => {
    if (a.isPinned && !b.isPinned) return -1;
    if (!a.isPinned && b.isPinned) return 1;
    return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className={`${gradientText} font-bold flex items-center`}>
          <Template className="h-4 w-4 mr-2 text-indigo-500" />
          Note Templates
        </h3>
        
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button 
              variant="outline" 
              size="sm"
              className="border-gray-200 hover:border-indigo-500 hover:text-indigo-600"
            >
              <Plus className="h-4 w-4 mr-1" />
              New Template
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle className={gradientText}>Create Note Template</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Template Title</label>
                <Input
                  value={newTemplate.title || ''}
                  onChange={(e) => setNewTemplate({ ...newTemplate, title: e.target.value })}
                  placeholder="Enter template title"
                  className="border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input
                  value={newTemplate.description || ''}
                  onChange={(e) => setNewTemplate({ ...newTemplate, description: e.target.value })}
                  placeholder="Enter template description"
                  className="border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
              
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="text-sm font-medium">Note Type</label>
                  <Select 
                    value={newTemplate.note_type || 'VOCABULARY'} 
                    onValueChange={(value) => setNewTemplate({ ...newTemplate, note_type: value })}
                  >
                    <SelectTrigger className="border-gray-200 focus:ring-indigo-500 mt-2">
                      <BookOpenText className="h-4 w-4 mr-2 text-indigo-500" />
                      <SelectValue placeholder="Note Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="VOCABULARY">Vocabulary</SelectItem>
                      <SelectItem value="GRAMMAR">Grammar</SelectItem>
                      <SelectItem value="EXPRESSION">Expression</SelectItem>
                      <SelectItem value="CULTURE">Culture</SelectItem>
                      <SelectItem value="NOTE">General Note</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex-1">
                  <label className="text-sm font-medium">Language</label>
                  <Select 
                    value={newTemplate.language || 'fr'} 
                    onValueChange={(value) => setNewTemplate({ ...newTemplate, language: value })}
                  >
                    <SelectTrigger className="border-gray-200 focus:ring-indigo-500 mt-2">
                      <Languages className="h-4 w-4 mr-2 text-indigo-500" />
                      <SelectValue placeholder="Language" />
                    </SelectTrigger>
                    <SelectContent>
                      {LANGUAGE_OPTIONS.map(option => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Template Content (HTML)</label>
                <Textarea
                  value={newTemplate.content || ''}
                  onChange={(e) => setNewTemplate({ ...newTemplate, content: e.target.value })}
                  placeholder="Enter template content in HTML format"
                  className="min-h-[200px] border-gray-200 focus:border-indigo-500 focus:ring-indigo-500 font-mono text-sm"
                />
                <p className="text-xs text-gray-500">
                  Use HTML tags to structure your template. For example: &lt;h2&gt;Title&lt;/h2&gt;, &lt;p&gt;Text&lt;/p&gt;, &lt;ul&gt;&lt;li&gt;Item&lt;/li&gt;&lt;/ul&gt;
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="pin-template"
                  checked={newTemplate.isPinned || false}
                  onChange={(e) => setNewTemplate({ ...newTemplate, isPinned: e.target.checked })}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="pin-template" className="text-sm">
                  Pin this template to the top
                </label>
              </div>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button
                  variant="outline"
                  className="border-gray-200 hover:bg-gray-50"
                >
                  Cancel
                </Button>
              </DialogClose>
              <Button 
                onClick={handleCreateTemplate}
                className="bg-indigo-600 hover:bg-indigo-700 text-white"
              >
                Create Template
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      
      <div className="grid grid-cols-1 gap-4">
        {sortedTemplates.length === 0 ? (
          <div className="text-center py-8 px-4 border rounded-lg border-dashed border-gray-300 dark:border-gray-700">
            <div className="mx-auto w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-3">
              <Template className="h-6 w-6 text-gray-400" />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No templates yet. Create a template to quickly start new notes.
            </p>
            <Button 
              variant="outline" 
              size="sm" 
              className="mt-3 border-dashed border-gray-300 hover:border-indigo-500 dark:border-gray-700 dark:hover:border-indigo-500"
              onClick={() => setIsCreateDialogOpen(true)}
            >
              <Plus className="h-4 w-4 mr-1" />
              Create Template
            </Button>
          </div>
        ) : (
          sortedTemplates.map(template => (
            <div 
              key={template.id}
              className="border rounded-lg p-4 hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors relative group"
            >
              <div className="absolute top-2 right-2 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  onClick={() => handleTogglePinned(template.id)}
                  className="p-1 hover:bg-gray-100 rounded-full"
                  title={template.isPinned ? "Unpin template" : "Pin template"}
                >
                  {template.isPinned ? (
                    <Star className="h-4 w-4 text-yellow-500" />
                  ) : (
                    <StarOff className="h-4 w-4 text-gray-400" />
                  )}
                </button>
                <button 
                  onClick={() => handleEditTemplate(template)}
                  className="p-1 hover:bg-gray-100 rounded-full"
                  title="Edit template"
                >
                  <Pencil className="h-4 w-4 text-gray-500" />
                </button>
                <button 
                  onClick={() => handleDeleteTemplate(template.id)}
                  className="p-1 hover:bg-gray-100 rounded-full"
                  title="Delete template"
                >
                  <Trash2 className="h-4 w-4 text-red-500" />
                </button>
              </div>
              
              <div className="flex flex-col h-full">
                <div className="mb-2 flex items-center">
                  {template.isPinned && (
                    <Star className="h-4 w-4 text-yellow-500 mr-2" />
                  )}
                  <h4 className="font-medium text-lg">{template.title}</h4>
                </div>
                
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                  {template.description}
                </p>
                
                <div className="flex items-center text-xs text-gray-500 space-x-2 mb-4">
                  <div className="flex items-center">
                    <BookOpenText className="h-3 w-3 mr-1" />
                    <span>
                      {template.note_type.charAt(0) + template.note_type.slice(1).toLowerCase()}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <Languages className="h-3 w-3 mr-1" />
                    <span>
                      {LANGUAGE_OPTIONS.find(l => l.value === template.language)?.label || template.language}
                    </span>
                  </div>
                </div>
                
                <div className="mt-auto">
                  <Button 
                    variant="outline" 
                    size="sm"
                    className="w-full"
                    onClick={() => handleUseTemplate(template)}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Use Template
                  </Button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* Edit Template Dialog */}
      {selectedTemplate && (
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle className={gradientText}>Edit Template</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Template Title</label>
                <Input
                  value={selectedTemplate.title}
                  onChange={(e) => setSelectedTemplate({ ...selectedTemplate, title: e.target.value })}
                  placeholder="Enter template title"
                  className="border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input
                  value={selectedTemplate.description}
                  onChange={(e) => setSelectedTemplate({ ...selectedTemplate, description: e.target.value })}
                  placeholder="Enter template description"
                  className="border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
              
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="text-sm font-medium">Note Type</label>
                  <Select 
                    value={selectedTemplate.note_type} 
                    onValueChange={(value) => setSelectedTemplate({ ...selectedTemplate, note_type: value })}
                  >
                    <SelectTrigger className="border-gray-200 focus:ring-indigo-500 mt-2">
                      <BookOpenText className="h-4 w-4 mr-2 text-indigo-500" />
                      <SelectValue placeholder="Note Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="VOCABULARY">Vocabulary</SelectItem>
                      <SelectItem value="GRAMMAR">Grammar</SelectItem>
                      <SelectItem value="EXPRESSION">Expression</SelectItem>
                      <SelectItem value="CULTURE">Culture</SelectItem>
                      <SelectItem value="NOTE">General Note</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex-1">
                  <label className="text-sm font-medium">Language</label>
                  <Select 
                    value={selectedTemplate.language} 
                    onValueChange={(value) => setSelectedTemplate({ ...selectedTemplate, language: value })}
                  >
                    <SelectTrigger className="border-gray-200 focus:ring-indigo-500 mt-2">
                      <Languages className="h-4 w-4 mr-2 text-indigo-500" />
                      <SelectValue placeholder="Language" />
                    </SelectTrigger>
                    <SelectContent>
                      {LANGUAGE_OPTIONS.map(option => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Template Content (HTML)</label>
                <Textarea
                  value={selectedTemplate.content}
                  onChange={(e) => setSelectedTemplate({ ...selectedTemplate, content: e.target.value })}
                  placeholder="Enter template content in HTML format"
                  className="min-h-[200px] border-gray-200 focus:border-indigo-500 focus:ring-indigo-500 font-mono text-sm"
                />
                <p className="text-xs text-gray-500">
                  Use HTML tags to structure your template. For example: &lt;h2&gt;Title&lt;/h2&gt;, &lt;p&gt;Text&lt;/p&gt;, &lt;ul&gt;&lt;li&gt;Item&lt;/li&gt;&lt;/ul&gt;
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="pin-template-edit"
                  checked={selectedTemplate.isPinned}
                  onChange={(e) => setSelectedTemplate({ ...selectedTemplate, isPinned: e.target.checked })}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="pin-template-edit" className="text-sm">
                  Pin this template to the top
                </label>
              </div>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button
                  variant="outline"
                  className="border-gray-200 hover:bg-gray-50"
                >
                  Cancel
                </Button>
              </DialogClose>
              <Button 
                onClick={handleUpdateTemplate}
                className="bg-indigo-600 hover:bg-indigo-700 text-white"
              >
                Update Template
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}