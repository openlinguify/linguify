'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { jobsApi, JobPosition, JobApplication } from '@/core/api/jobsApi';

interface ApplicationModalProps {
  isOpen: boolean;
  onClose: () => void;
  position: JobPosition;
}

export function ApplicationModal({ isOpen, onClose, position }: ApplicationModalProps) {
  const [formData, setFormData] = useState<Partial<JobApplication>>({
    position: position.id,
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    cover_letter: '',
    resume_file: undefined,
    portfolio_url: '',
    linkedin_url: '',
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Check if position is still open
  const isPositionClosed = !position.is_open;
  const getClosingReason = () => {
    if (position.closing_date) {
      const closingDate = new Date(position.closing_date);
      const now = new Date();
      if (closingDate < now) {
        return `Applications closed on ${closingDate.toLocaleDateString()}`;
      }
    }
    return 'This position is no longer accepting applications';
  };

  const handleInputChange = (field: keyof JobApplication, value: string | File) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      if (!allowedTypes.includes(file.type)) {
        setSubmitError('Please upload a PDF or Word document');
        return;
      }
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setSubmitError('File size must be less than 5MB');
        return;
      }
      setSubmitError(null);
      setFormData(prev => ({ ...prev, resume_file: file }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Validate required fields
      if (!formData.first_name || !formData.last_name || !formData.email) {
        throw new Error('Please fill in all required fields');
      }

      await jobsApi.submitApplication(formData as JobApplication);
      setSubmitSuccess(true);
      
      // Reset form after successful submission
      setTimeout(() => {
        onClose();
        setSubmitSuccess(false);
        setFormData({
          position: position.id,
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          cover_letter: '',
          resume_file: undefined,
          portfolio_url: '',
          linkedin_url: '',
        });
      }, 2000);

    } catch (error: any) {
      // Handle specific validation errors
      if (error.response?.data?.email) {
        setSubmitError(error.response.data.email[0]);
      } else if (error.response?.data?.message) {
        setSubmitError(error.response.data.message);
      } else if (error.response?.data && typeof error.response.data === 'object') {
        // Handle field-specific errors
        const fieldErrors = Object.values(error.response.data).flat();
        setSubmitError(fieldErrors.join(', '));
      } else {
        setSubmitError(error.message || 'Failed to submit application');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitSuccess) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-md">
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Application Submitted!
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Thank you for your interest. We'll review your application and get back to you soon.
            </p>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">
            Apply for {position.title}
          </DialogTitle>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {position.department_name} • {position.location}
          </p>
        </DialogHeader>

        {isPositionClosed ? (
          <div className="space-y-6">
            <div className="bg-red-50 border border-red-200 rounded-md p-6 text-center">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.502 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                Applications Closed
              </h3>
              <p className="text-red-700 text-sm">
                {getClosingReason()}
              </p>
              {position.closing_date && (
                <p className="text-red-600 text-xs mt-2">
                  Deadline was: {new Date(position.closing_date).toLocaleString()}
                </p>
              )}
            </div>
            <div className="flex justify-end">
              <Button type="button" variant="outline" onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {submitError && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <p className="text-red-800 text-sm">{submitError}</p>
              </div>
            )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="first_name">First Name *</Label>
              <Input
                id="first_name"
                type="text"
                value={formData.first_name || ''}
                onChange={(e) => handleInputChange('first_name', e.target.value)}
                required
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="last_name">Last Name *</Label>
              <Input
                id="last_name"
                type="text"
                value={formData.last_name || ''}
                onChange={(e) => handleInputChange('last_name', e.target.value)}
                required
                className="mt-1"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="email">Email Address *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email || ''}
              onChange={(e) => handleInputChange('email', e.target.value)}
              required
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="phone">Phone Number</Label>
            <Input
              id="phone"
              type="tel"
              value={formData.phone || ''}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="resume_file">Resume/CV (PDF or Word)</Label>
            <Input
              id="resume_file"
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileChange}
              className="mt-1"
            />
            {formData.resume_file && (
              <p className="text-sm text-gray-600 mt-1">
                Selected: {formData.resume_file.name}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="portfolio_url">Portfolio URL</Label>
            <Input
              id="portfolio_url"
              type="url"
              value={formData.portfolio_url || ''}
              onChange={(e) => handleInputChange('portfolio_url', e.target.value)}
              placeholder="https://..."
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="linkedin_url">LinkedIn Profile</Label>
            <Input
              id="linkedin_url"
              type="url"
              value={formData.linkedin_url || ''}
              onChange={(e) => handleInputChange('linkedin_url', e.target.value)}
              placeholder="https://linkedin.com/in/..."
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="cover_letter">Cover Letter (Optional)</Label>
            <Textarea
              id="cover_letter"
              value={formData.cover_letter || ''}
              onChange={(e) => handleInputChange('cover_letter', e.target.value)}
              placeholder="Tell us why you're interested in this position and why you'd be a great fit..."
              rows={6}
              className="mt-1"
            />
          </div>

          <div className="flex gap-3 justify-end">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting...' : 'Submit Application'}
            </Button>
          </div>
        </form>
        )}
      </DialogContent>
    </Dialog>
  );
}