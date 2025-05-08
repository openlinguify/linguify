"use client";

import React, { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { notebookAPI } from "@/addons/notebook/api/notebookAPI";

export default function NotebookWrapperSimple() {
  const [isLoading, setIsLoading] = useState(true);
  const [notes, setNotes] = useState([]);
  
  useEffect(() => {
    const fetchInitialData = async () => {
      setIsLoading(true);
      try {
        const notesData = await notebookAPI.getNotes();
        setNotes(notesData);
      } catch (error) {
        console.error("Failed to fetch notes:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  return (
    <div className="flex flex-col h-screen bg-white p-4">
      <h1 className="text-2xl font-bold mb-4">Notebook</h1>
      
      {isLoading ? (
        <div className="flex items-center justify-center h-32">
          <p>Loading...</p>
        </div>
      ) : (
        <div>
          <Button className="mb-4">
            <Plus className="mr-2 h-4 w-4" />
            New Note
          </Button>
          
          {notes.length === 0 ? (
            <p className="text-center text-gray-500">No notes yet. Create your first note!</p>
          ) : (
            <ul className="space-y-2">
              {notes.map((note: any) => (
                <li 
                  key={note.id} 
                  className="p-4 border rounded-md cursor-pointer hover:bg-gray-50"
                >
                  <h3 className="font-medium">{note.title}</h3>
                  <p className="text-sm text-gray-500 truncate">{note.content}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}