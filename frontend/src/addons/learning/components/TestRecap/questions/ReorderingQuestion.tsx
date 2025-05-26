import React, { useState, useEffect } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface ReorderItem {
  id: string;
  text: string;
}

interface ReorderingQuestionData {
  id: string;
  question: string;
  items: ReorderItem[];
  correct_order: string[]; // Array of item IDs in correct order
  explanation?: string;
}

interface ReorderingQuestionProps {
  data: ReorderingQuestionData;
  onAnswer: (answer: string[]) => void;
  savedAnswer?: string[];
}

const SortableItem = ({ id, text, index }: { id: string; text: string; index: number }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <Card
      ref={setNodeRef}
      style={style}
      className="p-3 mb-2 cursor-move bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
      {...attributes}
      {...listeners}
    >
      <div className="flex items-center">
        <div className="mr-3 text-gray-500">{index + 1}.</div>
        <div className="flex-1">{text}</div>
        <div className="text-gray-400">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="8" y1="6" x2="21" y2="6" />
            <line x1="8" y1="12" x2="21" y2="12" />
            <line x1="8" y1="18" x2="21" y2="18" />
            <line x1="3" y1="6" x2="3.01" y2="6" />
            <line x1="3" y1="12" x2="3.01" y2="12" />
            <line x1="3" y1="18" x2="3.01" y2="18" />
          </svg>
        </div>
      </div>
    </Card>
  );
};

const ReorderingQuestion: React.FC<ReorderingQuestionProps> = ({
  data,
  onAnswer,
  savedAnswer,
}) => {
  // Create a mapping of item IDs to their content for easy lookup
  const itemsMap = data.items.reduce((acc, item) => {
    acc[item.id] = item.text;
    return acc;
  }, {} as Record<string, string>);

  // Initialize items in a shuffled order if no saved answer
  const [items, setItems] = useState<string[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [showValidation, setShowValidation] = useState(false);

  // Setup sensors for drag and drop
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Initialize with saved answer or shuffled items
  useEffect(() => {
    if (!isInitialized) {
      if (savedAnswer && savedAnswer.length > 0) {
        setItems(savedAnswer);
      } else {
        // Get all item IDs
        const itemIds = data.items.map(item => item.id);
        
        // Shuffle the items
        const shuffled = [...itemIds].sort(() => Math.random() - 0.5);
        
        // Make sure the shuffled order is different from the correct order
        // if they happen to be the same after shuffling
        if (JSON.stringify(shuffled) === JSON.stringify(data.correct_order) && itemIds.length > 1) {
          // Swap the first two elements
          [shuffled[0], shuffled[1]] = [shuffled[1], shuffled[0]];
        }
        
        setItems(shuffled);
      }
      setIsInitialized(true);
    }
  }, [data.items, data.correct_order, savedAnswer, isInitialized]);

  // Handle drag end event
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    
    if (over && active.id !== over.id) {
      setItems((prevItems) => {
        const oldIndex = prevItems.indexOf(active.id as string);
        const newIndex = prevItems.indexOf(over.id as string);
        return arrayMove(prevItems, oldIndex, newIndex);
      });
      setShowValidation(false);
    }
  };

  // Handle submit
  const handleSubmit = () => {
    // Check if the order has been changed from initial shuffle
    if (JSON.stringify(items) === JSON.stringify(data.items.map(item => item.id))) {
      setShowValidation(true);
      return;
    }
    
    onAnswer(items);
  };

  // Handle Enter key press
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  // Reset the order
  const handleReset = () => {
    // Shuffle again
    const itemIds = data.items.map(item => item.id);
    const shuffled = [...itemIds].sort(() => Math.random() - 0.5);
    setItems(shuffled);
    setShowValidation(false);
  };

  // Check if the current order matches the correct order
  const isCurrentOrderCorrect = JSON.stringify(items) === JSON.stringify(data.correct_order);

  return (
    <div className="space-y-6" onKeyDown={handleKeyDown}>
      <div className="text-lg font-medium mb-2">{data.question}</div>
      
      <div className="mb-4">
        <p className="text-sm text-gray-500 mb-2">
          Drag and drop the items to reorder them into the correct sequence.
        </p>
        
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext items={items} strategy={verticalListSortingStrategy}>
            {items.map((id, index) => (
              <SortableItem
                key={id}
                id={id}
                text={itemsMap[id]}
                index={index}
              />
            ))}
          </SortableContext>
        </DndContext>
      </div>
      
      {showValidation && (
        <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-md">
          Please reorder the items before submitting.
        </div>
      )}
      
      <div className="flex justify-between">
        <Button variant="outline" onClick={handleReset}>
          Reset Order
        </Button>
        <Button onClick={handleSubmit}>
          Submit
        </Button>
      </div>
    </div>
  );
};

export default ReorderingQuestion;