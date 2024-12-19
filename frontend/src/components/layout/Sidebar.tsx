import { useState } from 'react';
import {
    BookOpen,
    MessageSquare,
    Grid,
    GraduationCap,
    Users,
    Settings,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';

// Types
type MenuItem = {
    id: string;
    icon: React.ReactNode;
    label: string;
    gradient: string;
    notifications?: number;
    subItems?: { id: string; label: string }[];
};

const Sidebar = ({ isExpanded, setIsExpanded }: {
    isExpanded: boolean;
    setIsExpanded: (value: boolean) => void;
}) => {
    const [activeItem, setActiveItem] = useState('dashboard');
    const [expandedGroup, setExpandedGroup] = useState<string | null>(null);

    const menuItems: MenuItem[] = [
        {
            id: 'dashboard',
            icon: <Grid size={24} />,
            label: 'Dashboard',
            gradient: 'from-purple-500 to-orange-300'
        },
        {
            id: 'learn',
            icon: <GraduationCap size={24} />,
            label: 'Learn',
            gradient: 'from-blue-500 to-cyan-300',
            notifications: 3,
            subItems: [
                { id: 'courses', label: 'Mes cours' },
                { id: 'progress', label: 'Progression' },
                { id: 'certificates', label: 'Certificats' }
            ]
        },
        {
            id: 'study',
            icon: <BookOpen size={24} />,
            label: 'Study',
            gradient: 'from-green-500 to-emerald-300',
            subItems: [
                { id: 'materials', label: 'Matériel' },
                { id: 'exercises', label: 'Exercices' },
                { id: 'notes', label: 'Notes' }
            ]
        },
        {
            id: 'chat',
            icon: <MessageSquare size={24} />,
            label: 'Chat',
            gradient: 'from-yellow-500 to-orange-300',
            notifications: 2
        },
        {
            id: 'coach',
            icon: <Users size={24} />,
            label: 'Coach',
            gradient: 'from-red-500 to-pink-300'
        },
        {
            id: 'settings',
            icon: <Settings size={24} />,
            label: 'Settings',
            gradient: 'from-gray-500 to-gray-300'
        }
    ];

    const handleItemClick = (itemId: string) => {
        setActiveItem(itemId);
        if (expandedGroup === itemId) {
            setExpandedGroup(null);
        } else {
            setExpandedGroup(itemId);
        }
    };

    return (
        <div
            className={`fixed left-0 top-0 h-screen bg-white shadow-lg transition-all duration-300 
      ${isExpanded ? 'w-64' : 'w-20'} flex flex-col`}
        >
            <div className="flex items-center p-4 border-b">
                <div className="w-8 h-8 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg flex-shrink-0" />
                {isExpanded && <span className="ml-3 text-lg font-medium">Dashboard</span>}
            </div>
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="absolute -right-3 top-16 w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center text-white shadow-lg hover:bg-purple-600 transition-colors"
            >
                {isExpanded ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
            </button>
            <div className="flex-1 overflow-y-auto py-4">
                {menuItems.map((item) => (
                    <div key={item.id} className="mb-2">
                        <button
                            onClick={() => handleItemClick(item.id)}
                            className={`w-full text-left px-4 py-3 flex items-center transition-colors
                ${activeItem === item.id ? 'bg-purple-50' : 'hover:bg-gray-50'}
                ${isExpanded ? 'pr-6' : 'justify-center'}`}
                        >
                            <div className={`relative flex items-center justify-center w-8 h-8 rounded-lg 
                bg-gradient-to-br ${item.gradient}`}>
                                <div className="text-white">{item.icon}</div>
                                {item.notifications && (
                                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-white text-xs flex items-center justify-center">
                    {item.notifications}
                  </span>
                                )}
                            </div>
                            {isExpanded && (
                                <span className="ml-3 text-sm font-medium text-gray-700">{item.label}</span>
                            )}
                        </button>
                        {isExpanded && item.subItems && expandedGroup === item.id && (
                            <div className="ml-12 mt-2 space-y-2">
                                {item.subItems.map((subItem) => (
                                    <button
                                        key={subItem.id}
                                        onClick={() => setActiveItem(subItem.id)}
                                        className={`w-full text-left px-4 py-2 text-sm transition-colors rounded-lg
                      ${activeItem === subItem.id ? 'bg-purple-100 text-purple-700' : 'text-gray-600 hover:bg-gray-50'}`}
                                    >
                                        {subItem.label}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Sidebar;




import React from "react";

const Sidebar = ({
                     searchTerm,
                     setSearchTerm,
                     filterCategory,
                     setFilterCategory,
                     sortOption,
                     setSortOption,
                     categories,
                 }: {
    searchTerm: string;
    setSearchTerm: (value: string) => void;
    filterCategory: string;
    setFilterCategory: (value: string) => void;
    sortOption: string;
    setSortOption: (value: string) => void;
    categories: string[];
}) => {
    return (
        <div className="bg-light p-4" style={{ width: "250px" }}>
            <h4>Menu</h4>
            <ul className="list-unstyled">
                <li>
                    <input
                        type="text"
                        className="form-control mb-3"
                        placeholder="Rechercher un cours..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </li>
                <li>
                    <select
                        className="form-control mb-3"
                        value={filterCategory}
                        onChange={(e) => setFilterCategory(e.target.value)}
                    >
                        <option value="all">Toutes les catégories</option>
                        {categories.map((category) => (
                            <option key={category} value={category}>
                                {category}
                            </option>
                        ))}
                    </select>
                </li>
                <li>
                    <select
                        className="form-control"
                        value={sortOption}
                        onChange={(e) => setSortOption(e.target.value)}
                    >
                        <option value="none">Trier par</option>
                        <option value="title">Titre</option>
                        <option value="category">Catégorie</option>
                    </select>
                </li>
            </ul>
        </div>
    );
};

export default Sidebar;
