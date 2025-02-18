"use client";

import { Progress } from "@/components/ui/progress";

interface UserProgressProps {
  value?: number;
  label?: string;
}

export const UserProgress = ({
  value = 90,
  label = "Progress",
}: UserProgressProps) => {
  return (
    <div className="flex flex-col space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm text-muted-foreground font-medium">
          {label}
        </span>
        <span className="text-sm font-semibold bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
          {value}%
        </span>
      </div>
      <Progress value={value} />
    </div>
  );
};