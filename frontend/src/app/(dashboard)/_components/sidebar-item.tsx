"use client";

import { LucideIcon } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

interface SidebarItemProps {
  icon: LucideIcon;
  label: string;
  href: string;
};

export const SidebarItem = ({
  icon: Icon,
  label,
  href,
}: SidebarItemProps) => {
  const pathname = usePathname();
  const router = useRouter();
  
  const isActive = pathname === href;
  
  const onClick = () => {
    router.push(href);
  };

  return (
    <button
      onClick={onClick}
      type="button"
      className={cn(
        "flex items-center gap-x-2 text-slate-500 text-sm font-medium pl-6 transition-all",
        "w-full h-12 relative",
        "hover:bg-slate-100/50",
        isActive && "text-sky-700 bg-sky-100/50 hover:bg-sky-100/50 hover:text-sky-700",
        href.includes("premium") && "text-amber-700 hover:text-amber-800"
      )}
    >
      <div className="flex items-center gap-x-2">
        <Icon 
          size={20} 
          className={cn(
            "text-slate-500",
            isActive && "text-sky-700",
            href.includes("premium") && "text-amber-700"
          )}
        />
        {label}
      </div>
      {isActive && (
        <div 
          className={cn(
            "absolute right-0 top-0 h-full w-1",
            href.includes("premium") ? "bg-amber-700" : "bg-sky-700"
          )}
        />
      )}
    </button>
  );
}