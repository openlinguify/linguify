import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  X, 
  Plus, 
  Tag, 
  Check, 
  Search, 
  Palette, 
  Filter, 
  PlusCircle,
  Trash
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Command,
  CommandInput,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

export interface TagItem {
  id: number;
  name: string;
  color: string;
}

interface TagEditorProps {
  allTags: TagItem[];
  selectedTags: number[];
  onAddTag: (name: string, color: string) => Promise<TagItem | undefined>;
  onSelectTag: (tagId: number) => void;
  onRemoveTag: (tagId: number) => void;
  onDeleteTag?: (tagId: number) => Promise<void>;
  disabled?: boolean;
  className?: string;
}

interface TagCategoryGroup {
  name: string;
  tags: TagItem[];
}

const TAG_COLORS = [
  // Gray
  { name: "gray", value: "#6B7280" },
  // Red
  { name: "red", value: "#EF4444" },
  // Orange
  { name: "orange", value: "#F97316" },
  // Amber
  { name: "amber", value: "#F59E0B" },
  // Yellow
  { name: "yellow", value: "#EAB308" },
  // Lime
  { name: "lime", value: "#84CC16" },
  // Green
  { name: "green", value: "#22C55E" },
  // Emerald
  { name: "emerald", value: "#10B981" },
  // Teal
  { name: "teal", value: "#14B8A6" },
  // Cyan
  { name: "cyan", value: "#06B6D4" },
  // Sky
  { name: "sky", value: "#0EA5E9" },
  // Blue
  { name: "blue", value: "#3B82F6" },
  // Indigo
  { name: "indigo", value: "#6366F1" },
  // Violet
  { name: "violet", value: "#8B5CF6" },
  // Purple
  { name: "purple", value: "#A855F7" },
  // Fuchsia
  { name: "fuchsia", value: "#D946EF" },
  // Pink
  { name: "pink", value: "#EC4899" },
  // Rose
  { name: "rose", value: "#F43F5E" },
];

const TagEditor: React.FC<TagEditorProps> = ({
  allTags,
  selectedTags,
  onAddTag,
  onSelectTag,
  onRemoveTag,
  onDeleteTag,
  disabled = false,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [newTagColor, setNewTagColor] = useState(TAG_COLORS[0].value);
  const [isCreating, setIsCreating] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentTab, setCurrentTab] = useState<'all' | 'selected'>('all');
  const [categorySections, setCategorySections] = useState<TagCategoryGroup[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isCreating && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isCreating]);

  // Group tags by first letter
  useEffect(() => {
    const tagsToGroup = currentTab === 'selected'
      ? allTags.filter(tag => selectedTags.includes(tag.id))
      : allTags;
    
    // Filter by search if present
    const filteredTags = searchText
      ? tagsToGroup.filter(tag => 
          tag.name.toLowerCase().includes(searchText.toLowerCase()))
      : tagsToGroup;
    
    // Sort alphabetically
    const sortedTags = [...filteredTags].sort((a, b) => 
      a.name.localeCompare(b.name));
    
    // Group by first letter
    const groups: Record<string, TagItem[]> = {};
    sortedTags.forEach(tag => {
      const firstChar = tag.name.charAt(0).toUpperCase();
      if (!groups[firstChar]) {
        groups[firstChar] = [];
      }
      groups[firstChar].push(tag);
    });
    
    // Convert to array for rendering
    const newCategorySections = Object.entries(groups).map(([key, tags]) => ({
      name: key,
      tags
    })).sort((a, b) => a.name.localeCompare(b.name));
    
    setCategorySections(newCategorySections);
  }, [allTags, selectedTags, currentTab, searchText]);

  // Create new tag
  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;
    
    try {
      setIsSubmitting(true);
      const tag = await onAddTag(newTagName.trim(), newTagColor);
      
      if (tag) {
        onSelectTag(tag.id);
        setNewTagName('');
        // Select a random color for the next tag
        setNewTagColor(TAG_COLORS[Math.floor(Math.random() * TAG_COLORS.length)].value);
        setIsCreating(false);
      }
    } catch (error) {
      console.error('Error creating tag:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getTagStyle = (color: string) => {
    return {
      backgroundColor: `${color}20`, // color with 20% opacity
      borderColor: `${color}40`, // color with 40% opacity
      color: `${color}`
    };
  };

  // Render selected tags
  const renderSelectedTags = () => {
    if (selectedTags.length === 0) {
      return <div className="text-gray-500 dark:text-gray-400 text-sm">No tags selected</div>;
    }
    
    return (
      <div className="flex flex-wrap gap-2 mt-2">
        <AnimatePresence>
          {selectedTags.map(tagId => {
            const tag = allTags.find(t => t.id === tagId);
            if (!tag) return null;
            
            return (
              <motion.div
                key={tag.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.2 }}
              >
                <Badge
                  variant="outline"
                  className="flex items-center gap-1 py-1"
                  style={getTagStyle(tag.color)}
                >
                  <div
                    className="h-2 w-2 rounded-full" 
                    style={{ backgroundColor: tag.color }}
                  />
                  <span>{tag.name}</span>
                  {!disabled && (
                    <button
                      className="ml-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 p-0.5"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemoveTag(tag.id);
                      }}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  )}
                </Badge>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    );
  };

  // Render create tag form
  const renderCreateTagForm = () => (
    <div className="p-4 border-t">
      <h3 className="text-sm font-medium mb-2">Create New Tag</h3>
      
      <div className="flex gap-2 mb-2">
        <div className="flex items-center border rounded-md overflow-hidden flex-1">
          <div className="flex items-center justify-center p-2">
            <div 
              className="h-4 w-4 rounded-full cursor-pointer" 
              style={{ backgroundColor: newTagColor }}
              onClick={() => document.getElementById('color-picker-button')?.click()}
            />
          </div>
          
          <Input
            ref={inputRef}
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            placeholder="Tag name..."
            className="border-0 h-9 flex-1"
            disabled={isSubmitting}
          />
          
          <div className="flex pr-2">
            <Popover>
              <PopoverTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-8 w-8"
                  id="color-picker-button"
                >
                  <Palette className="h-4 w-4 text-gray-500" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-64 p-3">
                <div className="grid grid-cols-6 gap-2">
                  {TAG_COLORS.map(color => (
                    <TooltipProvider key={color.name}>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button
                            className="h-6 w-6 rounded-full cursor-pointer hover:ring-2 ring-offset-2 transition-all"
                            style={{ backgroundColor: color.value }}
                            onClick={() => setNewTagColor(color.value)}
                            aria-selected={newTagColor === color.value}
                          >
                            {newTagColor === color.value && (
                              <Check className="h-3 w-3 text-white mx-auto" />
                            )}
                          </button>
                        </TooltipTrigger>
                        <TooltipContent>
                          {color.name}
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  ))}
                </div>
              </PopoverContent>
            </Popover>
          </div>
        </div>
      </div>
      
      <div className="flex justify-end gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsCreating(false)}
          className="h-8"
        >
          Cancel
        </Button>
        
        <Button
          size="sm"
          className="h-8"
          disabled={!newTagName.trim() || isSubmitting}
          onClick={handleCreateTag}
        >
          {isSubmitting ? (
            <span className="flex items-center">
              <span className="mr-1">Creating</span>
              <span className="animate-pulse">...</span>
            </span>
          ) : (
            <span className="flex items-center">
              <PlusCircle className="h-3 w-3 mr-1" />
              Create
            </span>
          )}
        </Button>
      </div>
    </div>
  );

  return (
    <div className={`tag-editor ${className}`}>
      <div className="flex items-center gap-2 mb-2">
        <Button
          variant="outline"
          size="sm"
          className="h-8"
          onClick={() => setIsOpen(true)}
          disabled={disabled}
        >
          <Tag className="h-4 w-4 mr-1" />
          Manage Tags
        </Button>
        
        {selectedTags.length > 0 && (
          <Badge variant="secondary" className="h-5 px-2 py-0 flex items-center">
            {selectedTags.length} {selectedTags.length === 1 ? 'tag' : 'tags'}
          </Badge>
        )}
      </div>
      
      {renderSelectedTags()}
      
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverContent className="w-80 p-0" align="start">
          <div className="p-2 border-b">
            <div className="flex items-center">
              <Search className="h-4 w-4 text-gray-500 mr-2" />
              <Input
                placeholder="Search tags..."
                className="border-0 h-8 focus-visible:ring-0 p-0 text-sm"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
              />
            </div>
          </div>
          
          <div className="border-b">
            <Tabs 
              defaultValue="all" 
              value={currentTab} 
              onValueChange={(v) => setCurrentTab(v as 'all' | 'selected')}
              className="w-full"
            >
              <TabsList className="w-full grid grid-cols-2">
                <TabsTrigger value="all" className="text-xs">
                  All Tags ({allTags.length})
                </TabsTrigger>
                <TabsTrigger value="selected" className="text-xs">
                  Selected ({selectedTags.length})
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
          
          <Command>
            <CommandList className="max-h-[200px] overflow-auto">
              {categorySections.length === 0 ? (
                <CommandEmpty>
                  {searchText
                    ? 'No tags found'
                    : currentTab === 'selected'
                      ? 'No tags selected'
                      : 'No tags available'}
                </CommandEmpty>
              ) : (
                <>
                  {categorySections.map(section => (
                    <CommandGroup key={section.name} heading={section.name}>
                      {section.tags.map(tag => {
                        const isSelected = selectedTags.includes(tag.id);
                        return (
                          <CommandItem
                            key={tag.id}
                            onSelect={() => onSelectTag(tag.id)}
                            className="flex items-center justify-between cursor-pointer"
                          >
                            <div className="flex items-center gap-2">
                              <div
                                className="h-3 w-3 rounded-full"
                                style={{ backgroundColor: tag.color }}
                              />
                              <span>{tag.name}</span>
                            </div>
                            
                            <div className="flex items-center gap-1">
                              {isSelected && (
                                <div className="text-green-500">
                                  <Check className="h-4 w-4" />
                                </div>
                              )}
                              
                              {onDeleteTag && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7 text-gray-500 hover:text-red-500"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    if (window.confirm(`Delete tag "${tag.name}"?`)) {
                                      onDeleteTag(tag.id);
                                    }
                                  }}
                                >
                                  <Trash className="h-3 w-3" />
                                </Button>
                              )}
                            </div>
                          </CommandItem>
                        );
                      })}
                    </CommandGroup>
                  ))}
                </>
              )}
            </CommandList>
            
            <CommandSeparator />
            
            {isCreating ? (
              renderCreateTagForm()
            ) : (
              <div className="p-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setIsCreating(true)}
                  disabled={disabled}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  <span>Create new tag</span>
                </Button>
              </div>
            )}
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
};

export default TagEditor;