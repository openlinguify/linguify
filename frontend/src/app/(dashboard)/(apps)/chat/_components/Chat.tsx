"use client";

import React, { useState } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useChat } from '@/hooks/useChat';
import { 
  Send, 
  Search,
  Settings,
  Phone,
  Video,
  Plus,
  Image,
  Mic,
  Smile,
  MoreVertical
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const MessengerChat = () => {
  const {
    conversations,
    selectedConversation,
    setSelectedConversation,
    messages,
    loading,
    searchResults,
    sendMessage,
    searchUsers,
    startConversation
  } = useChat();

  const [messageInput, setMessageInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [showNewChat, setShowNewChat] = useState(false);
  const [searchConversations, setSearchConversations] = useState("");

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    searchUsers(query);
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim()) return;
    
    sendMessage(messageInput);
    setMessageInput("");
  };

  const handleStartConversation = (userId: number) => {
    startConversation(userId.toString());
    setShowNewChat(false);
  };

  const getOtherParticipant = (conversation: any) => {
    return conversation.participants.find((p: any) => p.id !== 'me');
  };

  const filteredConversations = conversations.filter(conv => 
    getOtherParticipant(conv).name.toLowerCase().includes(searchConversations.toLowerCase())
  );

  return (
    <div className="h-[calc(100vh-4rem)] max-w-6xl mx-auto p-6">
      <Card className="grid grid-cols-[320px_1fr] h-full overflow-hidden">
        {/* Conversations List */}
        <div className="border-r flex flex-col">
          {/* Header */}
          <div className="p-4 border-b space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Messages</h2>
              <Dialog open={showNewChat} onOpenChange={setShowNewChat}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="icon" className="hover:bg-gray-100 dark:hover:bg-gray-800">
                    <Plus className="h-4 w-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>New Conversation</DialogTitle>
                  </DialogHeader>
                  <div className="mt-4 space-y-4">
                    <div className="relative">
                      <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search users..."
                        className="pl-8"
                        value={searchQuery}
                        onChange={(e) => handleSearch(e.target.value)}
                      />
                    </div>
                    <ScrollArea className="h-[300px]">
                      {searchResults.map(user => (
                        <div
                          key={user.id}
                          onClick={() => handleStartConversation(user.id)}
                          className="p-2 hover:bg-accent rounded-lg cursor-pointer"
                        >
                          <div className="flex items-center gap-3">
                            <Avatar>
                              <img src={user.avatar} alt={user.name} />
                            </Avatar>
                            <div>
                              <p className="font-medium">{user.name}</p>
                              <p className="text-sm text-muted-foreground">{user.status}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </ScrollArea>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search conversations..."
                className="pl-8"
                value={searchConversations}
                onChange={(e) => setSearchConversations(e.target.value)}
              />
            </div>
          </div>

          {/* Conversations List */}
          <ScrollArea className="flex-1">
            <div className="divide-y">
              {loading ? (
                // Loading skeletons
                (Array(5).fill(0).map((_, i) => (
                  <div key={i} className="p-4 flex items-center gap-3">
                    <Skeleton className="h-12 w-12 rounded-full" />
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-3 w-24" />
                    </div>
                  </div>
                )))
              ) : (
                filteredConversations.map(conversation => {
                  const otherParticipant = getOtherParticipant(conversation);
                  return (
                    <div
                      key={conversation.id}
                      onClick={() => setSelectedConversation(conversation)}
                      className={`p-4 flex items-center gap-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${
                        selectedConversation?.id === conversation.id ? 'bg-gray-50 dark:bg-gray-800' : ''
                      }`}
                    >
                      <div className="relative">
                        <Avatar>
                          <img src={otherParticipant.avatar} alt={otherParticipant.name} />
                        </Avatar>
                        {otherParticipant.online && (
                          <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-gray-900" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start">
                          <p className="font-medium truncate">{otherParticipant.name}</p>
                          <span className="text-xs text-muted-foreground">
                            {conversation.lastMessage ? new Date().toLocaleTimeString() : ''}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground truncate">
                          {conversation.lastMessage}
                        </p>
                      </div>
                      {(conversation.unreadCount ?? 0) > 0 && (
                        <Badge variant="secondary" className="rounded-full">
                          {conversation.unreadCount}
                        </Badge>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Chat Area */}
        <div className="flex flex-col h-full">
          {selectedConversation ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Avatar>
                    <img
                      src={getOtherParticipant(selectedConversation).avatar}
                      alt={getOtherParticipant(selectedConversation).name}
                    />
                  </Avatar>
                  <div>
                    <h3 className="font-medium">
                      {getOtherParticipant(selectedConversation).name}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {getOtherParticipant(selectedConversation).online ? 'Online' : 'Offline'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="icon" className="hover:bg-gray-100 dark:hover:bg-gray-800">
                    <Phone className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="hover:bg-gray-100 dark:hover:bg-gray-800">
                    <Video className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="hover:bg-gray-100 dark:hover:bg-gray-800">
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Messages Area */}
              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.sender === 'me' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <div
                        className={`max-w-[70%] rounded-lg p-3 ${
                          message.sender === 'me'
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-100 dark:bg-gray-800'
                        }`}
                      >
                        <p>{message.content}</p>
                        <span className="text-xs opacity-70 mt-1 block">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>

              {/* Message Input */}
              <form onSubmit={handleSendMessage} className="p-4 border-t">
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <Image className="h-4 w-4" />
                  </Button>
                  <Input
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    placeholder="Type a message..."
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <Smile className="h-4 w-4" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <Mic className="h-4 w-4" />
                  </Button>
                  <Button type="submit" size="icon" disabled={!messageInput.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </form>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center p-4">
              <div className="max-w-sm space-y-2">
                <h3 className="text-lg font-medium">Welcome to Messages</h3>
                <p className="text-sm text-muted-foreground">
                  Select a conversation or start a new one to begin messaging
                </p>
                <Button onClick={() => setShowNewChat(true)}>
                  Start a conversation
                </Button>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default MessengerChat;