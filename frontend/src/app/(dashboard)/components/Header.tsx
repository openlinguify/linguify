"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
    GlobeIcon,
    MenuIcon,
    User,
    BookOpen,
    Trophy,
    Settings,
    Bell,
    LogOut,
} from "lucide-react";
import {
    Select,
    SelectTrigger,
    SelectContent,
    SelectItem,
    SelectValue,
} from "@/components/ui/select";

const Header: React.FC = () => {
    const [language, setLanguage] = useState("en");

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
            <div className="container flex h-16 items-center justify-between">
                {/* Logo and Main Navigation */}
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <GlobeIcon className="h-8 w-8 text-sky-500" />
                        <span className="text-2xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
                            Linguify
                        </span>
                    </div>
                    <nav className="hidden md:flex gap-6">
                        <NavItem href="/learn" icon={BookOpen} label="Learn" />
                        <NavItem href="/progress" icon={Trophy} label="Progress" />
                    </nav>
                </div>

                {/* Right Side Actions */}
                <div className="flex items-center gap-4">
                    <Select value={language} onValueChange={setLanguage}>
                        <SelectTrigger className="w-32 border border-gray-300 rounded-lg">
                            <SelectValue placeholder="Language" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="en">English</SelectItem>
                            <SelectItem value="fr">French</SelectItem>
                            <SelectItem value="es">Spanish</SelectItem>
                        </SelectContent>
                    </Select>

                    <Button variant="ghost" size="icon">
                        <Bell className="h-5 w-5 text-gray-600 hover:text-sky-600" />
                    </Button>

                    <Button 
                        variant="ghost" 
                        className="text-gray-600 hover:text-sky-600 hover:bg-sky-50"
                    >
                        <Settings className="h-4 w-4 mr-2" />
                        Settings
                    </Button>

                    <Button 
                        className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700 text-white shadow-sm hover:shadow-md transition-all duration-200"
                    >
                        <User className="h-4 w-4 mr-2" />
                        Profile
                    </Button>

                    <Button variant="ghost" size="icon" aria-label="Logout">
                        <LogOut className="h-5 w-5" />
                    </Button>
                </div>
            </div>
        </header>
    );
};

const NavItem = ({
    href,
    icon: Icon,
    label,
}: {
    href: string;
    icon: React.ComponentType<{ className?: string }>;
    label: string;
}) => (
    <a
        href={href}
        className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-sky-600 transition-colors"
    >
        <Icon className="h-4 w-4" />
        {label}
    </a>
);

export default Header;
