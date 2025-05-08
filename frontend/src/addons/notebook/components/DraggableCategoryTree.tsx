// src/addons/notebook/components/DraggableCategoryTree.tsx
import React, { useState, useCallback, useEffect } from 'react';
import { ChevronRight, ChevronDown, Folder, FolderOpen, Plus, Edit, Trash2, Library, Move } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { CategoryTreeProps, Category } from '@/addons/notebook/types';
import { notebookAPI } from '../api/notebookAPI';
import { gradientText } from "@/styles/gradient_style";

export function DraggableCategoryTree({ 
  categories, 
  selectedCategory, 
  onSelect 
}: CategoryTreeProps) {
  const [expandedCategories, setExpandedCategories] = useState<number[]>([]);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [newDialogOpen, setNewDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [parentCategory, setParentCategory] = useState<number | null>(null);
  const [categoryName, setCategoryName] = useState('');
  const [categoryDescription, setCategoryDescription] = useState('');
  const [categoryOrder, setCategoryOrder] = useState<Category[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  
  // Initialize and maintain category order
  useEffect(() => {
    setCategoryOrder(categories);
  }, [categories]);

  // Auto-expand categories with subcategories on first render
  useEffect(() => {
    if (categories.length > 0 && expandedCategories.length === 0) {
      const initialExpanded: number[] = [];
      
      const findCategoriesWithSubcategories = (cats: Category[]) => {
        cats.forEach(cat => {
          if (cat.subcategories && cat.subcategories.length > 0) {
            initialExpanded.push(cat.id);
            findCategoriesWithSubcategories(cat.subcategories);
          }
        });
      };
      
      findCategoriesWithSubcategories(categories);
      setExpandedCategories(initialExpanded);
    }
  }, [categories, expandedCategories.length]);
  
  const toggleExpanded = useCallback((categoryId: number, e?: React.MouseEvent) => {
    e?.stopPropagation();
    setExpandedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  }, []);

  const handleNewCategory = useCallback(() => {
    setEditingCategory(null);
    setParentCategory(null);
    setCategoryName('');
    setCategoryDescription('');
    setNewDialogOpen(true);
  }, []);

  const handleNewSubcategory = useCallback((parentId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingCategory(null);
    setParentCategory(parentId);
    setCategoryName('');
    setCategoryDescription('');
    setNewDialogOpen(true);
  }, []);

  const handleEditCategory = useCallback((category: Category, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingCategory(category);
    setCategoryName(category.name);
    setCategoryDescription(category.description || '');
    setEditDialogOpen(true);
  }, []);

  const handleCreateCategory = async () => {
    if (!categoryName.trim()) return;
    
    try {
      await notebookAPI.createCategory({
        name: categoryName,
        description: categoryDescription,
        parent: parentCategory,
      });
      setNewDialogOpen(false);
      // Refresh categories would be handled by parent component
    } catch (error) {
      console.error('Failed to create category:', error);
    }
  };

  const handleUpdateCategory = async () => {
    if (!editingCategory || !categoryName.trim()) return;
    
    try {
      await notebookAPI.updateCategory(editingCategory.id, {
        name: categoryName,
        description: categoryDescription,
      });
      setEditDialogOpen(false);
      // Refresh categories would be handled by parent component
    } catch (error) {
      console.error('Failed to update category:', error);
    }
  };

  const handleDeleteCategory = async (categoryId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this category? All notes in this category will be moved to uncategorized.')) {
      return;
    }
    
    try {
      await notebookAPI.deleteCategory(categoryId);
      // Refresh categories would be handled by parent component
    } catch (error) {
      console.error('Failed to delete category:', error);
    }
  };

  // Handle drag and drop
  const handleDragEnd = async (result: DropResult) => {
    setIsDragging(false);
    
    // Dropped outside the list or no destination
    if (!result.destination) {
      return;
    }
    
    // If the item didn't move, don't do anything
    if (result.destination.index === result.source.index) {
      return;
    }
    
    // Get the dragged category ID
    const draggedCategoryId = parseInt(result.draggable.id.split('-')[1]);
    
    // Extract parent ID if present
    const parentId = result.droppableId === 'root' 
      ? null 
      : parseInt(result.droppableId.split('-')[1]);
    
    // Update local state
    const updatedCategories = [...categoryOrder];
    const [reorderedItem] = updatedCategories.splice(result.source.index, 1);
    updatedCategories.splice(result.destination.index, 0, reorderedItem);
    setCategoryOrder(updatedCategories);
    
    // Update on the server
    try {
      await notebookAPI.moveCategory(draggedCategoryId, parentId);
    } catch (error) {
      console.error('Failed to update category order:', error);
      // Revert the local state in case of error
      setCategoryOrder(categories);
    }
  };

  const handleDragStart = () => {
    setIsDragging(true);
  };

  const renderDraggableCategory = (category: Category, index: number, level = 0) => {
    const isExpanded = expandedCategories.includes(category.id);
    const isSelected = selectedCategory === category.id;
    const hasSubcategories = category.subcategories && category.subcategories.length > 0;
    
    return (
      <Draggable 
        key={`cat-${category.id}`} 
        draggableId={`cat-${category.id}`} 
        index={index}
      >
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.draggableProps}
            className={`select-none ${snapshot.isDragging ? 'opacity-70' : ''}`}
          >
            <div 
              className={`
                flex items-center py-1.5 px-2 my-0.5 group transition-all
                ${isSelected 
                  ? 'bg-gradient-to-r from-indigo-50 to-indigo-100 text-indigo-800 dark:from-indigo-900/30 dark:to-indigo-900/20 dark:text-indigo-300 rounded-md' 
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700/50 rounded-md'}
              `}
              style={{ paddingLeft: `${(level * 12) + 8}px` }}
              onClick={() => onSelect(category.id)}
            >
              {hasSubcategories ? (
                <button
                  onClick={(e) => toggleExpanded(category.id, e)}
                  className="mr-1 focus:outline-none"
                >
                  {isExpanded ? (
                    <ChevronDown className={`h-4 w-4 ${isSelected ? 'text-indigo-500' : 'text-gray-400'}`} />
                  ) : (
                    <ChevronRight className={`h-4 w-4 ${isSelected ? 'text-indigo-500' : 'text-gray-400'}`} />
                  )}
                </button>
              ) : (
                <span className="w-5"></span>
              )}
              
              {isExpanded ? (
                <FolderOpen className={`h-4 w-4 mr-2 ${isSelected ? 'text-indigo-500' : 'text-indigo-400'}`} />
              ) : (
                <Folder className={`h-4 w-4 mr-2 ${isSelected ? 'text-indigo-500' : 'text-indigo-400'}`} />
              )}
              
              <span className="flex-1 truncate text-sm">
                {category.name}
                {category.notes_count > 0 && (
                  <Badge 
                    variant="outline" 
                    className={`ml-2 h-4 min-w-4 text-[10px] px-1 py-0 rounded-full ${
                      isSelected 
                        ? 'bg-indigo-100 text-indigo-700 border-indigo-300 dark:bg-indigo-900/30 dark:text-indigo-300 dark:border-indigo-700' 
                        : 'bg-gray-100 text-gray-600 border-gray-300 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700'
                    }`}
                  >
                    {category.notes_count}
                  </Badge>
                )}
              </span>
              
              <div {...provided.dragHandleProps} className="px-1 cursor-move">
                <Move className="h-4 w-4 text-gray-400" />
              </div>
              
              <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => handleNewSubcategory(category.id, e)}
                  className="p-1 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 rounded-full"
                  title="Add subcategory"
                >
                  <Plus className="h-3 w-3 text-indigo-500" />
                </button>
                <button
                  onClick={(e) => handleEditCategory(category, e)}
                  className="p-1 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 rounded-full"
                  title="Edit category"
                >
                  <Edit className="h-3 w-3 text-indigo-500" />
                </button>
                <button
                  onClick={(e) => handleDeleteCategory(category.id, e)}
                  className="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-full"
                  title="Delete category"
                >
                  <Trash2 className="h-3 w-3 text-red-500" />
                </button>
              </div>
            </div>
            
            {isExpanded && hasSubcategories && (
              <Droppable droppableId={`parent-${category.id}`} type="category">
                {(droppableProvided) => (
                  <div 
                    ref={droppableProvided.innerRef}
                    {...droppableProvided.droppableProps}
                    className="ml-2"
                  >
                    {category.subcategories.map((subcategory, subIndex) => 
                      renderDraggableCategory(subcategory, subIndex, level + 1)
                    )}
                    {droppableProvided.placeholder}
                  </div>
                )}
              </Droppable>
            )}
          </div>
        )}
      </Draggable>
    );
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center mb-4">
        <h3 className={`${gradientText} font-bold flex items-center`}>
          <Library className="h-4 w-4 mr-2 text-indigo-500" />
          Categories
        </h3>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleNewCategory}
          className="border-gray-200 hover:border-indigo-500 hover:text-indigo-600 dark:border-gray-700 dark:hover:border-indigo-500 dark:hover:text-indigo-400"
        >
          <Plus className="h-4 w-4 mr-1" />
          New
        </Button>
      </div>
      
      <div className="overflow-auto max-h-[calc(100vh-200px)] pr-1">
        {categories.length === 0 ? (
          <div className="text-center py-8 px-4">
            <div className="mx-auto w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-3">
              <Folder className="h-6 w-6 text-gray-400" />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No categories yet. Create one to organize your notes.
            </p>
            <Button 
              variant="outline" 
              size="sm" 
              className="mt-3 border-dashed border-gray-300 hover:border-indigo-500 dark:border-gray-700 dark:hover:border-indigo-500"
              onClick={handleNewCategory}
            >
              <Plus className="h-4 w-4 mr-1" />
              Create Category
            </Button>
          </div>
        ) : (
          <DragDropContext 
            onDragEnd={handleDragEnd}
            onDragStart={handleDragStart}
          >
            <Droppable droppableId="root" type="category">
              {(provided) => (
                <div 
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`${isDragging ? 'bg-gray-50 dark:bg-gray-800/50 rounded-lg' : ''}`}
                >
                  {categoryOrder.map((category, index) => 
                    renderDraggableCategory(category, index)
                  )}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        )}
      </div>
      
      {/* New Category Dialog */}
      <Dialog open={newDialogOpen} onOpenChange={setNewDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className={gradientText}>
              {parentCategory ? 'Create Subcategory' : 'Create Category'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Category Name</label>
              <Input
                value={categoryName}
                onChange={e => setCategoryName(e.target.value)}
                placeholder="Enter category name"
                className="border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Description (optional)</label>
              <Input
                value={categoryDescription}
                onChange={e => setCategoryDescription(e.target.value)}
                placeholder="Enter description"
                className="border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
              />
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
              onClick={handleCreateCategory}
              className="bg-indigo-600 hover:bg-indigo-700 text-white"
            >
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Edit Category Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className={gradientText}>Edit Category</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Category Name</label>
              <Input
                value={categoryName}
                onChange={e => setCategoryName(e.target.value)}
                placeholder="Enter category name"
                className="border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Description (optional)</label>
              <Input
                value={categoryDescription}
                onChange={e => setCategoryDescription(e.target.value)}
                placeholder="Enter description"
                className="border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
              />
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
              onClick={handleUpdateCategory}
              className="bg-indigo-600 hover:bg-indigo-700 text-white"
            >
              Update
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}