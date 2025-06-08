// src/addons/quizz/components/questions/MatchingQuestion.tsx
'use client';

import React, { useState } from 'react';
import { DndContext, DragEndEvent, DragOverlay, useDraggable, useDroppable } from '@dnd-kit/core';
import { arrayMove, SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface MatchingPair {
  id: string;
  left: string;
  right: string;
}

interface MatchingQuestionProps {
  question: {
    id: number;
    text: string;
    pairs: MatchingPair[];
  };
  value: Record<string, string>;
  onChange: (value: Record<string, string>) => void;
}

const MatchingQuestion: React.FC<MatchingQuestionProps> = ({
  question,
  value,
  onChange,
}) => {
  const [leftItems] = useState(question.pairs.map(p => ({ id: p.id, text: p.left })));
  const [rightItems, setRightItems] = useState(
    question.pairs.map(p => ({ id: p.id, text: p.right }))
      .sort(() => Math.random() - 0.5) // Shuffle right items
  );

  const handleDragEnd = useCallback((result: DropResult) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;

    if (destination.droppableId === source.droppableId) {
      // Reordering within the same list
      if (destination.droppableId === 'right-items') {
        const newRightItems = Array.from(rightItems);
        const [reorderedItem] = newRightItems.splice(source.index, 1);
        newRightItems.splice(destination.index, 0, reorderedItem);
        setRightItems(newRightItems);
      }
    } else {
      // Moving between lists (matching)
      if (source.droppableId === 'right-items' && destination.droppableId.startsWith('match-')) {
        const leftItemId = destination.droppableId.replace('match-', '');
        const rightItem = rightItems[source.index];
        
        const newValue = { ...value, [leftItemId]: rightItem.id };
        onChange(newValue);
      }
    }
  }, [rightItems, value, onChange]);

  const getMatchedItem = (leftItemId: string) => {
    const matchedId = value[leftItemId];
    return rightItems.find(item => item.id === matchedId);
  };

  const getUnmatchedRightItems = () => {
    const matchedIds = Object.values(value);
    return rightItems.filter(item => !matchedIds.includes(item.id));
  };

  const removeMatch = (leftItemId: string) => {
    const newValue = { ...value };
    delete newValue[leftItemId];
    onChange(newValue);
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column - Items to match */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700 mb-3">Éléments à associer</h4>
          {leftItems.map((leftItem) => (
            <Droppable key={leftItem.id} droppableId={`match-${leftItem.id}`}>
              {(provided, snapshot) => {
                const matchedItem = getMatchedItem(leftItem.id);
                return (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`min-h-[60px] p-3 border-2 border-dashed rounded-lg transition-colors ${
                      snapshot.isDraggingOver
                        ? 'border-purple-400 bg-purple-50'
                        : matchedItem
                        ? 'border-green-400 bg-green-50'
                        : 'border-gray-300 bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{leftItem.text}</span>
                      {matchedItem && (
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary" className="bg-green-100 text-green-800">
                            {matchedItem.text}
                          </Badge>
                          <button
                            onClick={() => removeMatch(leftItem.id)}
                            className="text-red-500 hover:text-red-700 text-sm"
                          >
                            ✕
                          </button>
                        </div>
                      )}
                    </div>
                    {provided.placeholder}
                  </div>
                );
              }}
            </Droppable>
          ))}
        </div>

        {/* Right Column - Available options */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700 mb-3">Options disponibles</h4>
          <Droppable droppableId="right-items">
            {(provided, snapshot) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className={`min-h-[200px] p-3 border-2 border-dashed rounded-lg transition-colors ${
                  snapshot.isDraggingOver
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-gray-300 bg-gray-50'
                }`}
              >
                {getUnmatchedRightItems().map((item, index) => (
                  <Draggable key={item.id} draggableId={item.id} index={index}>
                    {(provided, snapshot) => (
                      <Card
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className={`p-3 mb-2 cursor-move transition-shadow ${
                          snapshot.isDragging
                            ? 'shadow-lg bg-white'
                            : 'hover:shadow-md'
                        }`}
                      >
                        {item.text}
                      </Card>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </div>

        {/* Instructions */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700 mb-3">Instructions</h4>
          <div className="p-4 bg-blue-50 rounded-lg text-sm">
            <p className="mb-2">💡 <strong>Comment faire :</strong></p>
            <ul className="space-y-1 text-gray-600">
              <li>• Glissez les éléments de droite vers les cases de gauche</li>
              <li>• Cliquez sur ✕ pour annuler une association</li>
              <li>• Toutes les associations doivent être faites</li>
            </ul>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg text-sm">
            <p><strong>Progression :</strong></p>
            <p className="text-green-600">
              {Object.keys(value).length} / {leftItems.length} associations
            </p>
          </div>
        </div>
      </div>
    </DragDropContext>
  );
};

export default MatchingQuestion;