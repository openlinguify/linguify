// Original path: frontend/src/app/dashboard/apps/notebook/_components/NotebookWrapper.tsx
'use client';

import React, { useState } from 'react';
import NotebookClient from './NotebookClient';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/shared/components/ui/tabs';
import { Input } from '@/shared/components/ui/input';
import { Search, Filter } from 'lucide-react';

export default function NotebookWrapper() {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  
  return (
    <div className="space-y-6">
      {/* Search and Filter Bar */}
      <div className="flex gap-4 items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <Input
            type="text"
            placeholder="Search notes..."
            className="pl-10 w-full"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <button className="p-2 hover:bg-gray-100 rounded">
          <Filter size={20} />
        </button>
      </div>

      <Tabs defaultValue="all" className="w-full" onValueChange={setActiveFilter}>
        <TabsList>
          <TabsTrigger value="all">All Notes</TabsTrigger>
          <TabsTrigger value="recent">Recent</TabsTrigger>
          <TabsTrigger value="favorites">Favorites</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-6">
          <NotebookClient searchTerm={searchTerm} filter={activeFilter} />
        </TabsContent>

        <TabsContent value="recent" className="mt-6">
          <NotebookClient searchTerm={searchTerm} filter="recent" />
        </TabsContent>

        <TabsContent value="favorites" className="mt-6">
          <NotebookClient searchTerm={searchTerm} filter="favorites" />
        </TabsContent>
      </Tabs>
    </div>
  );
}