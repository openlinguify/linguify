// frontend/src/app/(dashboard)/(apps)/revision/_components/EditCardModal.tsx

import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import type { Flashcard } from "@/types/revision";

interface EditCardModalProps {
    card: Flashcard;
    isOpen: boolean;
    onClose: () => void;
    onSave: (updatedCard: Partial<Flashcard>) => Promise<void>;
}

export default function EditCardModal({ card, isOpen, onClose, onSave }: EditCardModalProps) {
    const [formData, setFormData] = useState({
        front_text: card.front_text,
        back_text: card.back_text
    });
    const [isLoading, setIsLoading] = useState(false);
    const { toast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        
        try {
            await onSave(formData);
            toast({
                title: "Success",
                description: "Card updated successfully"
            });
            onClose();
        } catch (err) {
            toast({
                title: "Error",
                description: "Failed to update card",
                variant: "destructive"
            });
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <Card className="w-[90%] max-w-lg">
                <CardHeader>
                    <CardTitle>Edit Card</CardTitle>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="front_text">Front</Label>
                            <Textarea
                                id="front_text"
                                value={formData.front_text}
                                onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    front_text: e.target.value
                                }))}
                                placeholder="Front text"
                                className="min-h-[100px]"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="back_text">Back</Label>
                            <Textarea
                                id="back_text"
                                value={formData.back_text}
                                onChange={(e) => setFormData(prev => ({
                                    ...prev,
                                    back_text: e.target.value
                                }))}
                                placeholder="Back text"
                                className="min-h-[100px]"
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="flex justify-end space-x-2">
                        <Button 
                            type="button" 
                            variant="outline" 
                            onClick={onClose}
                            disabled={isLoading}
                        >
                            Cancel
                        </Button>
                        <Button 
                            type="submit"
                            disabled={isLoading || 
                                    !formData.front_text.trim() || 
                                    !formData.back_text.trim()}
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Saving...
                                </>
                            ) : 'Save Changes'}
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}