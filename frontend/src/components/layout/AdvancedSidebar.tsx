import { useState } from "react";
import {
    BookOpen,
    MessageSquare,
    Grid,
    GraduationCap,
    Users,
    Settings,
    ChevronLeft,
    ChevronRight,
} from "lucide-react";

// Types
interface MenuItem {
    id: string;
    icon: React.ReactNode;
    label: string;
    gradient: string;
    notifications?: number;
    subItems?: { id: string; label: string }[];
}

interface SidebarProps {
    isExpanded: boolean;
    setIsExpanded: (value: boolean) => void;
}

const AdvancedSidebar: React.FC<SidebarProps> = ({ isExpanded, setIsExpanded }) => {
    const [activeItem, setActiveItem] = useState<string>("dashboard");
    const [expandedGroup, setExpandedGroup] = useState<string | null>(null);

    const menuItems: MenuItem[] = [
        {
            id: "dashboard",
            icon: <Grid size={24} />,
            label: "Dashboard",
            gradient: "from-purple-500 to-orange-300",
        },
        {
            id: "learn",
            icon: <GraduationCap size={24} />,
            label: "Learn",
            gradient: "from-blue-500 to-cyan-300",
            notifications: 3,
            subItems: [
                { id: "courses", label: "Mes cours" },
                { id: "progress", label: "Progression" },
                { id: "certificates", label: "Certificats" },
            ],
        },
        // Additional menu items...
    ];

    const handleItemClick = (itemId: string) => {
        setActiveItem(itemId);
        setExpandedGroup((prev) => (prev === itemId ? null : itemId));
    };

    return (
        <div
            className={`fixed left-0 top-0 h-screen bg-white shadow-lg transition-all duration-300 ${
                isExpanded ? "w-64" : "w-20"
            } flex flex-col`}
        >
            <div className="flex items-center p-4 border-b">
                <div className="w-8 h-8 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg flex-shrink-0" />
                {isExpanded && <span className="ml-3 text-lg font-medium">Dashboard</span>}
            </div>
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="absolute -right-3 top-16 w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center text-white shadow-lg hover:bg-purple-600 transition-colors"
                aria-expanded={isExpanded}
            >
                {isExpanded ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
            </button>
            <div className="flex-1 overflow-y-auto py-4">
                {menuItems.map((item) => (
                    <SidebarItem
                        key={item.id}
                        item={item}
                        isExpanded={isExpanded}
                        activeItem={activeItem}
                        expandedGroup={expandedGroup}
                        handleItemClick={handleItemClick}
                    />
                ))}
            </div>
        </div>
    );
};

export default AdvancedSidebar;

interface SidebarItemProps {
    item: MenuItem;
    isExpanded: boolean;
    activeItem: string;
    expandedGroup: string | null;
    handleItemClick: (itemId: string) => void;
}

const SidebarItem: React.FC<SidebarItemProps> = ({
                                                     item,
                                                     isExpanded,
                                                     activeItem,
                                                     expandedGroup,
                                                     handleItemClick,
                                                 }) => {
    return (
        <div className="mb-2">
            <button
                onClick={() => handleItemClick(item.id)}
                className={`w-full text-left px-4 py-3 flex items-center transition-colors ${
                    activeItem === item.id ? "bg-purple-50" : "hover:bg-gray-50"
                } ${isExpanded ? "pr-6" : "justify-center"}`}
                aria-expanded={expandedGroup === item.id}
            >
                <div
                    className={`relative flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br ${item.gradient}`}
                >
                    {item.icon}
                    {item.notifications && (
                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-white text-xs flex items-center justify-center">
              {item.notifications}
            </span>
                    )}
                </div>
                {isExpanded && <span className="ml-3 text-sm font-medium">{item.label}</span>}
            </button>
            {isExpanded && item.subItems && expandedGroup === item.id && (
                <div className="ml-12 mt-2 space-y-2">
                    {item.subItems.map((subItem) => (
                        <button
                            key={subItem.id}
                            onClick={() => handleItemClick(subItem.id)}
                            className={`w-full text-left px-4 py-2 text-sm transition-colors rounded-lg ${
                                activeItem === subItem.id ? "bg-purple-100 text-purple-700" : "text-gray-600 hover:bg-gray-50"
                            }`}
                        >
                            {subItem.label}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};
