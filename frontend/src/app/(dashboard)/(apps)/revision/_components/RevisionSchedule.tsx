// frontend/src/app/%28dashboard%29/%28apps%29/revision/_components/RevisionSchedule.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Clock, Brain, CheckCircle2 } from "lucide-react";

interface ScheduleItem {
  id: string;
  words: string[];
  dueDate: Date;
  completed: boolean;
}

const MOCK_SCHEDULE: ScheduleItem[] = [
  {
    id: "1",
    words: ["hello", "world", "computer"],
    dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24),
    completed: false,
  },
  {
    id: "2",
    words: ["book", "pencil", "desk"],
    dueDate: new Date(Date.now() + 1000 * 60 * 60 * 48),
    completed: false,
  },
  {
    id: "3",
    words: ["cat", "dog", "bird"],
    dueDate: new Date(Date.now() - 1000 * 60 * 60 * 24),
    completed: true,
  },
];

function formatDueDate(date: Date): string {
  const now = new Date();
  const diff = date.getTime() - now.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (days < 0) return "Overdue";
  if (days === 0) return "Today";
  if (days === 1) return "Tomorrow";
  return `In ${days} days`;
}

export default function RevisionSchedule() {
  const totalItems = MOCK_SCHEDULE.length;
  const completedItems = MOCK_SCHEDULE.filter(item => item.completed).length;
  const progressPercentage = (completedItems / totalItems) * 100;

  return (
    <div className="space-y-6">
      {/* Progress Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-sky-600" />
            Revision Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Progress value={progressPercentage} className="w-full h-2" />
            <div className="flex justify-between text-sm text-gray-600">
              <span>{completedItems} completed</span>
              <span>{totalItems - completedItems} remaining</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Schedule List */}
      <div className="space-y-4">
        {MOCK_SCHEDULE.map((item) => (
          <Card key={item.id} className={item.completed ? "opacity-60" : ""}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">
                      Revision Set {item.id}
                    </h3>
                    <Badge variant={item.completed ? "secondary" : "default"}>
                      {item.completed ? (
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                      ) : (
                        <Clock className="w-3 h-3 mr-1" />
                      )}
                      {formatDueDate(item.dueDate)}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">
                    {item.words.join(", ")}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}