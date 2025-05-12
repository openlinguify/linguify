import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  Share2, 
  Users, 
  Copy, 
  User, 
  Check, 
  Loader2, 
  Mail, 
  Send, 
  Trash, 
  Clock, 
  AlertCircle,
  Link as LinkIcon,
} from 'lucide-react';
import { Note } from '@/addons/notebook/types';
import { notebookAPI } from '../api/notebookAPI';
import { useToast } from '@/components/ui/use-toast';
import { format } from 'date-fns';

interface ShareNoteDialogProps {
  note: Note;
  onUpdateSharing: () => void;
  className?: string;
}

interface SharedUser {
  id: number;
  username: string;
  email: string;
  shared_at: string;
  can_edit: boolean;
}

const ShareNoteDialog: React.FC<ShareNoteDialogProps> = ({
  note,
  onUpdateSharing,
  className = '',
}) => {
  const { toast } = useToast();
  
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('share');
  const [sharedUsers, setSharedUsers] = useState<SharedUser[]>([]);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  
  // Share form state
  const [shareEmail, setShareEmail] = useState('');
  const [canEdit, setCanEdit] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [shareError, setShareError] = useState<string | null>(null);
  
  // Link sharing state
  const [linkSharing, setLinkSharing] = useState({
    enabled: false,
    link: '',
    isLoading: false,
    expiration: 7, // days
  });
  
  // Load shared users when dialog opens
  useEffect(() => {
    if (isOpen) {
      loadSharedUsers();
      checkLinkSharing();
    }
  }, [isOpen, note.id]);
  
  // Load shared users for a note
  const loadSharedUsers = async () => {
    if (!note.id) return;
    
    try {
      setIsLoadingUsers(true);
      setLoadError(null);
      
      const users = await notebookAPI.getSharedUsers(note.id);
      setSharedUsers(users);
    } catch (error) {
      console.error('Error loading shared users:', error);
      setLoadError('Could not load sharing information');
    } finally {
      setIsLoadingUsers(false);
    }
  };
  
  // Check if link sharing is enabled for this note
  const checkLinkSharing = async () => {
    if (!note.id) return;
    
    try {
      setLinkSharing(prev => ({ ...prev, isLoading: true }));
      
      const linkData = await notebookAPI.getLinkSharing(note.id);
      
      setLinkSharing({
        enabled: linkData.enabled,
        link: linkData.link || '',
        isLoading: false,
        expiration: linkData.expiration_days || 7,
      });
    } catch (error) {
      console.error('Error checking link sharing:', error);
      setLinkSharing(prev => ({ 
        ...prev, 
        enabled: false, 
        link: '', 
        isLoading: false 
      }));
    }
  };
  
  // Share note with a user by email
  const handleShareWithUser = async () => {
    if (!shareEmail.trim() || !validateEmail(shareEmail)) {
      setShareError('Please enter a valid email address');
      return;
    }
    
    try {
      setIsSharing(true);
      setShareError(null);
      
      await notebookAPI.shareNote(note.id, shareEmail, canEdit);
      
      toast({
        title: 'Note shared',
        description: `Shared with ${shareEmail} successfully`,
        variant: 'default',
      });
      
      // Clear form
      setShareEmail('');
      setCanEdit(false);
      
      // Reload shared users
      loadSharedUsers();
      
      // Notify parent component
      onUpdateSharing();
    } catch (error) {
      console.error('Error sharing note:', error);
      
      let errorMessage = 'Could not share the note';
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      // Show specific errors for common issues
      if (errorMessage.includes('user') && errorMessage.includes('not found')) {
        errorMessage = 'No user found with this email address';
      } else if (errorMessage.includes('already shared')) {
        errorMessage = 'This note is already shared with this user';
      }
      
      setShareError(errorMessage);
    } finally {
      setIsSharing(false);
    }
  };
  
  // Toggle link sharing
  const handleToggleLinkSharing = async () => {
    try {
      setLinkSharing(prev => ({ ...prev, isLoading: true }));
      
      if (linkSharing.enabled) {
        // Disable link sharing
        await notebookAPI.disableLinkSharing(note.id);
        
        setLinkSharing({
          enabled: false,
          link: '',
          isLoading: false,
          expiration: 7,
        });
      } else {
        // Enable link sharing
        const result = await notebookAPI.enableLinkSharing(note.id, linkSharing.expiration);
        
        setLinkSharing({
          enabled: true,
          link: result.link,
          isLoading: false,
          expiration: linkSharing.expiration,
        });
      }
      
      // Notify parent
      onUpdateSharing();
    } catch (error) {
      console.error('Error toggling link sharing:', error);
      
      toast({
        title: 'Error',
        description: 'Could not update link sharing settings',
        variant: 'destructive',
      });
      
      setLinkSharing(prev => ({ ...prev, isLoading: false }));
    }
  };
  
  // Update link sharing expiration
  const handleUpdateExpiration = async () => {
    try {
      setLinkSharing(prev => ({ ...prev, isLoading: true }));
      
      const result = await notebookAPI.enableLinkSharing(note.id, linkSharing.expiration);
      
      setLinkSharing({
        enabled: true,
        link: result.link,
        isLoading: false,
        expiration: linkSharing.expiration,
      });
      
      toast({
        title: 'Expiration updated',
        description: `Sharing link will expire in ${linkSharing.expiration} days`,
        variant: 'default',
      });
    } catch (error) {
      console.error('Error updating expiration:', error);
      
      toast({
        title: 'Error',
        description: 'Could not update link expiration',
        variant: 'destructive',
      });
      
      setLinkSharing(prev => ({ ...prev, isLoading: false }));
    }
  };
  
  // Remove sharing for a user
  const handleRemoveSharing = async (userId: number) => {
    try {
      await notebookAPI.removeSharing(note.id, userId);
      
      toast({
        title: 'Sharing removed',
        description: 'User can no longer access this note',
        variant: 'default',
      });
      
      // Update the UI
      setSharedUsers(prev => prev.filter(user => user.id !== userId));
      
      // Notify parent
      onUpdateSharing();
    } catch (error) {
      console.error('Error removing sharing:', error);
      
      toast({
        title: 'Error',
        description: 'Could not remove sharing for this user',
        variant: 'destructive',
      });
    }
  };
  
  // Update sharing permissions for a user
  const handleUpdatePermission = async (userId: number, canEdit: boolean) => {
    try {
      await notebookAPI.updateSharing(note.id, userId, canEdit);
      
      toast({
        title: 'Permissions updated',
        description: canEdit 
          ? 'User can now edit this note' 
          : 'User can now only view this note',
        variant: 'default',
      });
      
      // Update the UI
      setSharedUsers(prev => 
        prev.map(user => 
          user.id === userId 
            ? { ...user, can_edit: canEdit } 
            : user
        )
      );
      
      // Notify parent
      onUpdateSharing();
    } catch (error) {
      console.error('Error updating permissions:', error);
      
      toast({
        title: 'Error',
        description: 'Could not update sharing permissions',
        variant: 'destructive',
      });
    }
  };
  
  // Copy sharing link to clipboard
  const handleCopyLink = () => {
    if (!linkSharing.link) return;
    
    navigator.clipboard.writeText(linkSharing.link).then(() => {
      toast({
        title: 'Link copied',
        description: 'Sharing link copied to clipboard',
        variant: 'default',
      });
    }).catch(() => {
      toast({
        title: 'Copy failed',
        description: 'Could not copy link to clipboard',
        variant: 'destructive',
      });
    });
  };
  
  // Email validation helper
  const validateEmail = (email: string) => {
    return /\S+@\S+\.\S+/.test(email);
  };
  
  // Render the "Share with User" tab
  const renderShareWithUserTab = () => (
    <div className="space-y-4 py-2">
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Share with a specific user</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Enter the email address of the user you want to share this note with
        </p>
      </div>
      
      <div className="space-y-4">
        <div>
          <Label htmlFor="email">Email address</Label>
          <div className="flex mt-1">
            <Input
              id="email"
              type="email"
              placeholder="Enter email address"
              value={shareEmail}
              onChange={(e) => {
                setShareEmail(e.target.value);
                setShareError(null); // Clear error when input changes
              }}
              className={shareError ? 'border-red-500' : ''}
            />
            <Button
              className="ml-2 shrink-0"
              disabled={isSharing || !shareEmail.trim()}
              onClick={handleShareWithUser}
            >
              {isSharing ? (
                <Loader2 className="h-4 w-4 animate-spin mr-1" />
              ) : (
                <Send className="h-4 w-4 mr-1" />
              )}
              Share
            </Button>
          </div>
          {shareError && (
            <p className="text-xs text-red-500 mt-1 flex items-center">
              <AlertCircle className="h-3 w-3 mr-1" />
              {shareError}
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <Checkbox 
            id="can-edit" 
            checked={canEdit}
            onCheckedChange={(checked) => setCanEdit(checked as boolean)}
          />
          <label
            htmlFor="can-edit"
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            Allow editing
          </label>
        </div>
      </div>
    </div>
  );
  
  // Render the "Link Sharing" tab
  const renderLinkSharingTab = () => (
    <div className="space-y-4 py-2">
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Share with link</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Anyone with the link will be able to view this note
        </p>
      </div>
      
      <div className="flex items-center space-x-2">
        <Checkbox 
          id="link-sharing" 
          checked={linkSharing.enabled}
          disabled={linkSharing.isLoading}
          onCheckedChange={() => handleToggleLinkSharing()}
        />
        <label
          htmlFor="link-sharing"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Enable link sharing
        </label>
        
        {linkSharing.isLoading && (
          <Loader2 className="h-4 w-4 animate-spin ml-2" />
        )}
      </div>
      
      {linkSharing.enabled && (
        <div className="space-y-4">
          <div>
            <Label htmlFor="link">Sharing link</Label>
            <div className="flex mt-1">
              <Input
                id="link"
                value={linkSharing.link}
                readOnly
                className="font-mono text-xs"
              />
              <Button
                variant="outline"
                size="icon"
                className="ml-2 shrink-0"
                onClick={handleCopyLink}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Link expires {linkSharing.expiration} days after creation
            </p>
          </div>
          
          <div>
            <Label htmlFor="expiration">Expiration (days)</Label>
            <div className="flex mt-1">
              <Input
                id="expiration"
                type="number"
                min="1"
                max="30"
                value={linkSharing.expiration}
                onChange={(e) => setLinkSharing(prev => ({ 
                  ...prev, 
                  expiration: parseInt(e.target.value) || 7 
                }))}
                className="w-20"
              />
              <Button
                variant="outline"
                className="ml-2"
                onClick={handleUpdateExpiration}
                disabled={linkSharing.isLoading}
              >
                Update
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
  
  // Render the "Shared Users" tab
  const renderSharedUsersTab = () => {
    if (isLoadingUsers) {
      return (
        <div className="py-8 flex justify-center">
          <div className="flex flex-col items-center">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400 mb-2" />
            <p className="text-sm text-gray-500">Loading shared users...</p>
          </div>
        </div>
      );
    }
    
    if (loadError) {
      return (
        <div className="py-8 flex justify-center">
          <div className="flex flex-col items-center">
            <AlertCircle className="h-8 w-8 text-red-500 mb-2" />
            <p className="text-sm text-red-500">{loadError}</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-4"
              onClick={loadSharedUsers}
            >
              Try Again
            </Button>
          </div>
        </div>
      );
    }
    
    if (sharedUsers.length === 0) {
      return (
        <div className="py-8 flex justify-center">
          <div className="flex flex-col items-center">
            <Users className="h-8 w-8 text-gray-400 mb-2" />
            <p className="text-sm text-gray-500">This note isn't shared with anyone yet.</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-4"
              onClick={() => setActiveTab('share')}
            >
              Share Now
            </Button>
          </div>
        </div>
      );
    }
    
    return (
      <div className="py-2">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Shared On</TableHead>
              <TableHead>Permissions</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sharedUsers.map(user => (
              <TableRow key={user.id}>
                <TableCell className="font-medium">
                  <div className="flex items-center">
                    <div className="h-8 w-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center mr-2">
                      <User className="h-4 w-4 text-gray-500" />
                    </div>
                    <div>
                      <p className="text-sm">{user.username}</p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center text-sm text-gray-500">
                    <Clock className="h-3 w-3 mr-1" />
                    {format(new Date(user.shared_at), 'MMM d, yyyy')}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge 
                    variant={user.can_edit ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => handleUpdatePermission(user.id, !user.can_edit)}
                  >
                    {user.can_edit ? "Can edit" : "Can view"}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                    onClick={() => handleRemoveSharing(user.id)}
                  >
                    <Trash className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`h-8 ${className}`}
        >
          <Share2 className="h-4 w-4 mr-1" />
          Share
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Share2 className="h-5 w-5 mr-2 text-indigo-500" />
            Share Note
          </DialogTitle>
          <DialogDescription>
            Share "{note.title}" with others
          </DialogDescription>
        </DialogHeader>
        
        <Tabs 
          defaultValue="share" 
          value={activeTab} 
          onValueChange={(v) => setActiveTab(v)}
          className="w-full"
        >
          <TabsList className="w-full grid grid-cols-3">
            <TabsTrigger value="share" className="text-xs">
              Share
            </TabsTrigger>
            <TabsTrigger value="link" className="text-xs">
              Link
            </TabsTrigger>
            <TabsTrigger value="users" className="text-xs">
              Shared With
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="share">
            {renderShareWithUserTab()}
          </TabsContent>
          
          <TabsContent value="link">
            {renderLinkSharingTab()}
          </TabsContent>
          
          <TabsContent value="users">
            {renderSharedUsersTab()}
          </TabsContent>
        </Tabs>
        
        <DialogFooter className="mt-6">
          <Button 
            variant="outline" 
            onClick={() => setIsOpen(false)}
          >
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ShareNoteDialog;