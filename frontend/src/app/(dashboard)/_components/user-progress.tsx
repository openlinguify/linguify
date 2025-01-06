"use client";

import { Progress } from "@/components/ui/progress";

export const UserProgress = () => {
  // This would normally be fetched from your backend
  const progress = 65;

  return (
    <div className="flex flex-col space-y-4">
      <div className="flex justify-between text-sm">
        <span className="text-slate-500 font-medium">Course Progress</span>
        <span className="text-sky-700 font-semibold">{progress}%</span>
      </div>
      <Progress value={progress} className="h-2" />
    </div>
  );
};