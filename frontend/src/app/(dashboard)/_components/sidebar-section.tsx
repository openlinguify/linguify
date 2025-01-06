import { Crown } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarSectionProps {
  children: React.ReactNode;
  label?: string;
  premiumRequired?: boolean;
}

export const SidebarSection = ({
  children,
  label,
  premiumRequired = false,
}: SidebarSectionProps) => {
  return (
    <div className="flex flex-col space-y-2">
      {label && (
        <div className="flex items-center gap-x-2 px-6 py-2">
          <span className={cn(
            "text-sm font-semibold",
            premiumRequired ? "text-amber-700" : "text-slate-500"
          )}>
            {label}
          </span>
          {premiumRequired && (
            <Crown size={14} className="text-amber-700" />
          )}
        </div>
      )}
      <div className="flex flex-col">
        {children}
      </div>
    </div>
  );
};