import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface MatchingItem {
  id: string;
  text: string;
}

interface MatchingQuestionData {
  id: string;
  question: string;
  target_items: MatchingItem[];
  native_items: MatchingItem[];
  explanation?: string;
}

interface MatchingQuestionProps {
  data: MatchingQuestionData;
  onAnswer: (answer: Record<string, string>) => void;
  savedAnswer?: Record<string, string>;
}

const MatchingQuestion: React.FC<MatchingQuestionProps> = ({
  data,
  onAnswer,
  savedAnswer,
}) => {
  const [selectedPairs, setSelectedPairs] = useState<Record<string, string>>({});
  const [activeItem, setActiveItem] = useState<{
    side: 'target' | 'native';
    id: string;
  } | null>(null);
  const [showValidation, setShowValidation] = useState(false);

  // Restore saved answer if available
  useEffect(() => {
    if (savedAnswer && Object.keys(savedAnswer).length > 0) {
      setSelectedPairs(savedAnswer);
    }
  }, [savedAnswer]);

  const handleItemClick = (side: 'target' | 'native', id: string) => {
    // If this item is already paired, remove the pairing
    if (side === 'target' && selectedPairs[id]) {
      const newPairs = { ...selectedPairs };
      delete newPairs[id];
      setSelectedPairs(newPairs);
      setActiveItem(null);
      return;
    }

    if (side === 'native') {
      const targetKey = Object.keys(selectedPairs).find(
        (key) => selectedPairs[key] === id
      );
      if (targetKey) {
        const newPairs = { ...selectedPairs };
        delete newPairs[targetKey];
        setSelectedPairs(newPairs);
        setActiveItem(null);
        return;
      }
    }

    // If no active item, set this as active
    if (!activeItem) {
      setActiveItem({ side, id });
      return;
    }

    // If same item clicked again, unselect it
    if (activeItem.side === side && activeItem.id === id) {
      setActiveItem(null);
      return;
    }

    // If clicking on the other side when an item is active, create a pairing
    if (activeItem.side !== side) {
      if (side === 'native' && activeItem.side === 'target') {
        // Target -> Native pairing
        setSelectedPairs((prev) => ({
          ...prev,
          [activeItem.id]: id,
        }));
      } else if (side === 'target' && activeItem.side === 'native') {
        // Native -> Target pairing
        setSelectedPairs((prev) => ({
          ...prev,
          [id]: activeItem.id,
        }));
      }
      setActiveItem(null);
    } else {
      // If clicking on the same side, change the active item
      setActiveItem({ side, id });
    }
  };

  const handleSubmit = () => {
    const allTargetItemsMatched = data.target_items.every(
      (item) => selectedPairs[item.id]
    );

    if (!allTargetItemsMatched) {
      setShowValidation(true);
      return;
    }

    onAnswer(selectedPairs);
  };

  const clearAllPairs = () => {
    setSelectedPairs({});
    setActiveItem(null);
    setShowValidation(false);
  };

  const getTargetItemStatus = (id: string) => {
    if (activeItem?.side === 'target' && activeItem.id === id) {
      return 'active';
    }
    if (selectedPairs[id]) {
      return 'matched';
    }
    return 'normal';
  };

  const getNativeItemStatus = (id: string) => {
    if (activeItem?.side === 'native' && activeItem.id === id) {
      return 'active';
    }
    const isMatched = Object.values(selectedPairs).includes(id);
    if (isMatched) {
      return 'matched';
    }
    return 'normal';
  };

  const isAllMatched = data.target_items.every((item) => selectedPairs[item.id]);
  const matchedCount = Object.keys(selectedPairs).length;
  const totalCount = data.target_items.length;

  return (
    <div className="space-y-6">
      <div className="text-lg font-medium mb-2">{data.question}</div>

      <div className="flex flex-col gap-4 md:flex-row">
        {/* Left Column - Target Language Items */}
        <div className="flex-1">
          <h3 className="text-sm font-medium mb-2">Items to Match</h3>
          <div className="space-y-2">
            {data.target_items.map((item) => (
              <Card
                key={item.id}
                className={cn(
                  "p-3 cursor-pointer transition-colors",
                  getTargetItemStatus(item.id) === 'active'
                    ? 'bg-blue-100 dark:bg-blue-900'
                    : getTargetItemStatus(item.id) === 'matched'
                    ? 'bg-green-100 dark:bg-green-900'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                )}
                onClick={() => handleItemClick('target', item.id)}
              >
                <div className="flex items-center justify-between">
                  <span>{item.text}</span>
                  {selectedPairs[item.id] && (
                    <span className="text-xs text-gray-500">
                      ↔️ Matched
                    </span>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Right Column - Native Language Items */}
        <div className="flex-1">
          <h3 className="text-sm font-medium mb-2">Match With</h3>
          <div className="space-y-2">
            {data.native_items.map((item) => (
              <Card
                key={item.id}
                className={cn(
                  "p-3 cursor-pointer transition-colors",
                  getNativeItemStatus(item.id) === 'active'
                    ? 'bg-blue-100 dark:bg-blue-900'
                    : getNativeItemStatus(item.id) === 'matched'
                    ? 'bg-green-100 dark:bg-green-900'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                )}
                onClick={() => handleItemClick('native', item.id)}
              >
                <div className="flex items-center justify-between">
                  <span>{item.text}</span>
                  {Object.values(selectedPairs).includes(item.id) && (
                    <span className="text-xs text-gray-500">
                      ↔️ Matched
                    </span>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Matching Progress */}
      <div className="mt-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-sm font-medium">Your Matches ({matchedCount}/{totalCount})</h3>
          {matchedCount > 0 && (
            <Button variant="outline" size="sm" onClick={clearAllPairs}>
              Clear All
            </Button>
          )}
        </div>

        {Object.keys(selectedPairs).length > 0 ? (
          <div className="space-y-2">
            {Object.entries(selectedPairs).map(([targetId, nativeId]) => {
              const targetItem = data.target_items.find(
                (item) => item.id === targetId
              );
              const nativeItem = data.native_items.find(
                (item) => item.id === nativeId
              );

              if (!targetItem || !nativeItem) return null;

              return (
                <Card key={targetId} className="p-3 bg-green-50 dark:bg-green-900/30">
                  <div className="flex justify-between">
                    <div className="flex-1">{targetItem.text}</div>
                    <div className="flex-none px-2">↔️</div>
                    <div className="flex-1 text-right">{nativeItem.text}</div>
                  </div>
                </Card>
              );
            })}
          </div>
        ) : (
          <Card className="p-3 bg-gray-50 dark:bg-gray-800/50 text-center text-gray-500">
            No matches yet. Select an item from each column to create a match.
          </Card>
        )}
      </div>

      {/* Validation Error */}
      {showValidation && !isAllMatched && (
        <div className="mt-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-md">
          Please match all items before submitting.
        </div>
      )}

      <div className="flex justify-end mt-6">
        <Button onClick={handleSubmit}>Submit</Button>
      </div>
    </div>
  );
};

export default MatchingQuestion;