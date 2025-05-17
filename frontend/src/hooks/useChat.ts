"use client";

import { useState, useEffect } from "react";

export interface ChatMessage {
  id: string;
  content: string;
  sender: string;
  timestamp: Date;
}

export interface Conversation {
  id: string;
  name: string;
  lastMessage?: string;
  unreadCount?: number;
}

export function useChat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);

  const sendMessage = async (content: string) => {
    // TODO: Implement message sending
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      sender: "current-user",
      timestamp: new Date(),
    };
    setMessages([...messages, newMessage]);
  };

  const searchUsers = async (query: string) => {
    // TODO: Implement user search
    setSearchResults([]);
  };

  const startConversation = async (userId: string) => {
    // TODO: Implement conversation creation
    const newConversation: Conversation = {
      id: Date.now().toString(),
      name: "New Conversation",
    };
    setConversations([...conversations, newConversation]);
    setSelectedConversation(newConversation);
  };

  return {
    conversations,
    selectedConversation,
    setSelectedConversation,
    messages,
    loading,
    searchResults,
    sendMessage,
    searchUsers,
    startConversation,
  };
}