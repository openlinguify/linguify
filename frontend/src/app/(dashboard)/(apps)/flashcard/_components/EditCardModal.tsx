// src/app/(dashboard)/(apps)/flashcard/_components/EditCardModal.tsx

import React, { useState, useEffect } from "react";
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent, 
  CardFooter,
  CardDescription 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, Save, X, RotateCw, ArrowLeftRight } from "lucide-react";
import type { Flashcard } from "@/types/revision";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

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
    const [originalData, setOriginalData] = useState({
        front_text: card.front_text,
        back_text: card.back_text
    });
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<string>("edit");
    const [previewFlipped, setPreviewFlipped] = useState(false);
    const { toast } = useToast();

    // Reset form when card changes
    useEffect(() => {
        setFormData({
            front_text: card.front_text,
            back_text: card.back_text
        });
        setOriginalData({
            front_text: card.front_text,
            back_text: card.back_text
        });
    }, [card]);

    const handleChange = (field: string, value: string) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

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

    const handleReset = () => {
        setFormData(originalData);
        toast({
            title: "Reset",
            description: "Changes reverted to original"
        });
    };

    const handleFlipTexts = () => {
        setFormData({
            front_text: formData.back_text,
            back_text: formData.front_text
        });
        toast({
            title: "Flipped",
            description: "Front and back texts have been swapped"
        });
    };

    // Calculate if form has been modified
    const isModified = 
        formData.front_text !== originalData.front_text || 
        formData.back_text !== originalData.back_text;

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="w-[90%] max-w-2xl">
                <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                        <CardTitle>Edit Card</CardTitle>
                        <CardDescription>
                            Update front and back text, or switch between preview and edit mode
                        </CardDescription>
                    </div>
                    <Button 
                        variant="ghost" 
                        size="icon" 
                        onClick={onClose}
                        disabled={isLoading}
                    >
                        <X className="h-4 w-4" />
                        <span className="sr-only">Close</span>
                    </Button>
                </CardHeader>

                <Tabs value={activeTab} onValueChange={setActiveTab}>
                    <div className="px-6">
                        <TabsList className="w-full">
                            <TabsTrigger value="edit" className="flex-1">Edit</TabsTrigger>
                            <TabsTrigger value="preview" className="flex-1">Preview</TabsTrigger>
                        </TabsList>
                    </div>

                    <TabsContent value="edit">
                        <form onSubmit={handleSubmit}>
                            <CardContent className="space-y-4 pt-2">
                                <div className="flex justify-end gap-2">
                                    <Button 
                                        type="button" 
                                        size="sm" 
                                        variant="outline"
                                        onClick={handleReset}
                                        disabled={!isModified || isLoading}
                                    >
                                        <RotateCw className="mr-2 h-4 w-4" />
                                        Reset
                                    </Button>
                                    <Button 
                                        type="button" 
                                        size="sm" 
                                        variant="outline"
                                        onClick={handleFlipTexts}
                                        disabled={isLoading}
                                    >
                                        <ArrowLeftRight className="mr-2 h-4 w-4" />
                                        Flip
                                    </Button>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="front_text">Front</Label>
                                    <Textarea
                                        id="front_text"
                                        value={formData.front_text}
                                        onChange={(e) => handleChange('front_text', e.target.value)}
                                        placeholder="Front text"
                                        className="min-h-[100px]"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="back_text">Back</Label>
                                    <Textarea
                                        id="back_text"
                                        value={formData.back_text}
                                        onChange={(e) => handleChange('back_text', e.target.value)}
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
                                            !formData.back_text.trim() ||
                                            !isModified}
                                    className="bg-brand-purple hover:bg-brand-purple-dark"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Saving...
                                        </>
                                    ) : (
                                        <>
                                            <Save className="mr-2 h-4 w-4" />
                                            Save Changes
                                        </>
                                    )}
                                </Button>
                            </CardFooter>
                        </form>
                    </TabsContent>

                    <TabsContent value="preview">
                        <CardContent className="space-y-4 pt-2">
                            <div className="flex justify-center mb-2">
                                <Button 
                                    variant="outline" 
                                    size="sm"
                                    onClick={() => setPreviewFlipped(prev => !prev)}
                                >
                                    <RotateCw className="mr-2 h-4 w-4" />
                                    Flip Card
                                </Button>
                            </div>
                            <div 
                                className="flex items-center justify-center p-8 border rounded-lg min-h-[250px] bg-white shadow-sm cursor-pointer transition-all duration-300"
                                onClick={() => setPreviewFlipped(prev => !prev)}
                            >
                                <div className="text-center">
                                    <h3 className="text-sm text-gray-500 uppercase mb-2">
                                        {previewFlipped ? "BACK" : "FRONT"}
                                    </h3>
                                    <p className="text-2xl font-medium">
                                        {previewFlipped ? formData.back_text : formData.front_text}
                                    </p>
                                    <p className="text-xs text-gray-400 mt-4">Click to flip</p>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter className="flex justify-between">
                            <Button 
                                variant="outline" 
                                onClick={() => setActiveTab("edit")}
                            >
                                Back to Edit
                            </Button>
                            <Button 
                                onClick={onClose}
                            >
                                Close
                            </Button>
                        </CardFooter>
                    </TabsContent>
                </Tabs>
            </Card>
        </div>
    );
}