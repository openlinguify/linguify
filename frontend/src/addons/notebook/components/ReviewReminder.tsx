import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  BrainCircuit,
  Clock,
  CheckCircle,
  Bell,
  BellRing,
  Calendar,
  Loader2,
  Sparkles,
  BarChart2,
  ListChecks,
  AlertCircle,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { notebookAPI } from '../api/notebookAPI';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Note } from '@/addons/notebook/types';
import LoadingIndicator from './LoadingIndicator';
import { formatDistanceToNow } from 'date-fns';

interface ReviewReminderProps {
  onReviewNote?: (noteId: number) => void;
  className?: string;
}

interface ReviewStats {
  total_notes: number;
  due_today: number;
  upcoming: number;
  reviewed_today: number;
  reviewed_week: number;
  average_interval: number;
  streak_days: number;
}

const ReviewReminder: React.FC<ReviewReminderProps> = ({
  onReviewNote,
  className = '',
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [dueNotes, setDueNotes] = useState<Note[]>([]);
  const [reviewStats, setReviewStats] = useState<ReviewStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [activeTab, setActiveTab] = useState('due');
  const [isCompleting, setIsCompleting] = useState<number | null>(null);
  
  // Fetch due notes on mount and when dialog opens
  useEffect(() => {
    if (showDialog) {
      fetchDueNotes();
      fetchReviewStats();
    }
  }, [showDialog]);
  
  // Fetch notes that are due for review
  const fetchDueNotes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const notes = await notebookAPI.getDueForReview();
      setDueNotes(notes);
    } catch (error) {
      console.error('Error fetching due notes:', error);
      setError('Could not load notes due for review');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Fetch review statistics
  const fetchReviewStats = async () => {
    try {
      const stats = await notebookAPI.getReviewStats();
      setReviewStats(stats);
    } catch (error) {
      console.error('Error fetching review statistics:', error);
      // Don't set error state for statistics to allow notes to still show
    }
  };
  
  // Mark a note as reviewed
  const handleReviewComplete = async (noteId: number, successful: boolean = true) => {
    try {
      setIsCompleting(noteId);
      
      await notebookAPI.markReviewed(noteId, successful);
      
      // Update the due notes list
      setDueNotes(prev => prev.filter(note => note.id !== noteId));
      
      // Refresh statistics
      fetchReviewStats();
      
      // Notify parent component if callback provided
      if (onReviewNote) {
        onReviewNote(noteId);
      }
    } catch (error) {
      console.error('Error marking note as reviewed:', error);
    } finally {
      setIsCompleting(null);
    }
  };
  
  // Render a due note card
  const renderNoteCard = (note: Note) => (
    <motion.div
      key={note.id}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="mb-3">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-start">
            <CardTitle className="text-base">{note.title}</CardTitle>
            <Badge 
              variant="outline" 
              className="ml-2 shrink-0"
            >
              {note.language?.toUpperCase() || 'NOTE'}
            </Badge>
          </div>
          <CardDescription className="line-clamp-2">
            {note.content.substring(0, 100)}
            {note.content.length > 100 ? '...' : ''}
          </CardDescription>
        </CardHeader>
        <CardFooter className="pt-2 flex justify-between">
          <div className="text-xs text-gray-500 flex items-center">
            <Clock className="h-3 w-3 mr-1" />
            {note.last_reviewed_at 
              ? `Last: ${formatDistanceToNow(new Date(note.last_reviewed_at), { addSuffix: true })}`
              : 'Never reviewed'}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="h-8 border-amber-200 hover:bg-amber-50 text-amber-700 dark:border-amber-800 dark:hover:bg-amber-900/20 dark:text-amber-400"
              onClick={() => handleReviewComplete(note.id, false)}
              disabled={isCompleting === note.id}
            >
              Still Learning
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-8 border-green-200 hover:bg-green-50 text-green-700 dark:border-green-800 dark:hover:bg-green-900/20 dark:text-green-400"
              onClick={() => handleReviewComplete(note.id, true)}
              disabled={isCompleting === note.id}
            >
              {isCompleting === note.id ? (
                <Loader2 className="h-4 w-4 animate-spin mr-1" />
              ) : (
                <CheckCircle className="h-4 w-4 mr-1" />
              )}
              Mark as Known
            </Button>
          </div>
        </CardFooter>
      </Card>
    </motion.div>
  );
  
  // Render the review statistics
  const renderReviewStats = () => {
    if (!reviewStats) {
      return (
        <div className="flex justify-center p-4">
          <LoadingIndicator message="Loading statistics..." size="small" />
        </div>
      );
    }
    
    return (
      <div className="p-4 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Card className="bg-blue-50 dark:bg-blue-900/20">
            <CardContent className="p-4">
              <div className="flex flex-col items-center text-center">
                <BrainCircuit className="h-6 w-6 mb-2 text-blue-600 dark:text-blue-400" />
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {reviewStats.due_today}
                </div>
                <p className="text-xs text-blue-800 dark:text-blue-300">Due Today</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-purple-50 dark:bg-purple-900/20">
            <CardContent className="p-4">
              <div className="flex flex-col items-center text-center">
                <Calendar className="h-6 w-6 mb-2 text-purple-600 dark:text-purple-400" />
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {reviewStats.upcoming}
                </div>
                <p className="text-xs text-purple-800 dark:text-purple-300">Coming Soon</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-green-50 dark:bg-green-900/20">
            <CardContent className="p-4">
              <div className="flex flex-col items-center text-center">
                <ListChecks className="h-6 w-6 mb-2 text-green-600 dark:text-green-400" />
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {reviewStats.reviewed_today}
                </div>
                <p className="text-xs text-green-800 dark:text-green-300">Reviewed Today</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-amber-50 dark:bg-amber-900/20">
            <CardContent className="p-4">
              <div className="flex flex-col items-center text-center">
                <BarChart2 className="h-6 w-6 mb-2 text-amber-600 dark:text-amber-400" />
                <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                  {reviewStats.streak_days}
                </div>
                <p className="text-xs text-amber-800 dark:text-amber-300">Day Streak</p>
              </div>
            </CardContent>
          </Card>
        </div>
        
        <Card>
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Review Progress</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Total Notes</span>
                <span className="font-medium">{reviewStats.total_notes}</span>
              </div>
              
              <div className="flex justify-between text-sm">
                <span>Reviewed This Week</span>
                <span className="font-medium">{reviewStats.reviewed_week}</span>
              </div>
              
              <div className="flex justify-between text-sm">
                <span>Average Interval</span>
                <span className="font-medium">{reviewStats.average_interval} days</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };
  
  // Render due notes list
  const renderDueNotes = () => {
    if (isLoading) {
      return (
        <div className="flex justify-center p-6">
          <LoadingIndicator message="Loading due notes..." size="medium" />
        </div>
      );
    }
    
    if (error) {
      return (
        <div className="flex flex-col items-center justify-center p-6 text-center">
          <AlertCircle className="h-8 w-8 text-red-500 mb-2" />
          <h3 className="text-base font-medium">Something went wrong</h3>
          <p className="text-sm text-gray-500 mt-1">{error}</p>
          <Button
            variant="outline"
            size="sm"
            className="mt-4"
            onClick={fetchDueNotes}
          >
            Try Again
          </Button>
        </div>
      );
    }
    
    if (dueNotes.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center p-6 text-center">
          <Sparkles className="h-8 w-8 text-green-500 mb-2" />
          <h3 className="text-base font-medium">All caught up!</h3>
          <p className="text-sm text-gray-500 mt-1">
            No notes are due for review right now.
          </p>
        </div>
      );
    }
    
    return (
      <div className="p-4">
        <AnimatePresence>
          {dueNotes.map(note => renderNoteCard(note))}
        </AnimatePresence>
      </div>
    );
  };
  
  // Get button appearance based on due note count
  const getButtonAppearance = () => {
    if (isLoading) {
      return { icon: <Loader2 className="h-4 w-4 animate-spin mr-1" />, text: 'Loading...' };
    }
    
    if (reviewStats && reviewStats.due_today > 0) {
      return { 
        icon: <BellRing className="h-4 w-4 mr-1 text-amber-500" />, 
        text: `${reviewStats.due_today} due for review`,
        className: "border-amber-300 hover:bg-amber-50 text-amber-800 dark:border-amber-800 dark:hover:bg-amber-900/20 dark:text-amber-300"
      };
    }
    
    return { 
      icon: <Bell className="h-4 w-4 mr-1" />, 
      text: 'Review Notes' 
    };
  };
  
  // Fetch initial data to show badge
  useEffect(() => {
    const fetchInitialStats = async () => {
      try {
        const stats = await notebookAPI.getReviewStats();
        setReviewStats(stats);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching initial stats:', error);
        setIsLoading(false);
      }
    };
    
    fetchInitialStats();
  }, []);
  
  const buttonAppearance = getButtonAppearance();
  
  return (
    <Dialog open={showDialog} onOpenChange={setShowDialog}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`h-8 ${buttonAppearance.className || ''} ${className}`}
        >
          {buttonAppearance.icon}
          {buttonAppearance.text}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <BrainCircuit className="h-5 w-5 mr-2 text-indigo-500" />
            Spaced Repetition Review
          </DialogTitle>
          <DialogDescription>
            Review your notes using spaced repetition to improve memory retention
          </DialogDescription>
        </DialogHeader>
        
        <Tabs 
          defaultValue="due" 
          value={activeTab} 
          onValueChange={(v) => setActiveTab(v)}
          className="w-full"
        >
          <TabsList className="w-full grid grid-cols-2">
            <TabsTrigger value="due" className="text-sm">
              Due for Review
            </TabsTrigger>
            <TabsTrigger value="stats" className="text-sm">
              Statistics
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="due">
            {renderDueNotes()}
          </TabsContent>
          
          <TabsContent value="stats">
            {renderReviewStats()}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default ReviewReminder;