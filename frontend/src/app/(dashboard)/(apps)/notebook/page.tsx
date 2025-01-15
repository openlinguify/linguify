// Original path: frontend/src/app/dashboard/apps/notebook/page.tsx
import { Metadata } from 'next';
import React from 'react';
import NotebookWrapper from './_components/NotebookWrapper';

export const metadata: Metadata = {
  title: 'Notebook',
  description: 'Organize and manage your thoughts',
};

const NotebookPage = async () => {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">My Notes</h1>
        <p className="text-sm text-gray-600">Organize and manage your thoughts</p>
      </div>
      <NotebookWrapper />
    </div>
  );
};

export default NotebookPage;