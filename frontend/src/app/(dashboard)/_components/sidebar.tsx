import { Logo } from "./header/logo";
import { SidebarRoutes } from "./sidebar-routes";
import { UserProgress } from "./user-progress";

export const Sidebar = () => {
  return (
    <div className="h-full border-r flex flex-col overflow-y-auto bg-white shadow-sm">
      <div className="p-6 border-b">
        <Logo />
      </div>
      <div className="flex flex-col w-full pt-4">
        <SidebarRoutes />
      </div>
      <div className="mt-auto p-6 border-t">
        <UserProgress />
      </div>
    </div>
  );
};