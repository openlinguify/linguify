// Test script to verify notebook API functionality

/**
 * This script provides a simple way to test the notebook API functionality
 * manually from the browser console. It can be run by copying and pasting
 * into the browser console when on the notebook page.
 * 
 * Usage:
 * 1. Open the notebook page in the browser
 * 2. Open the browser console (F12 or Ctrl+Shift+I)
 * 3. Copy and paste this entire script into the console
 * 4. Run the tests using the provided test functions
 */

// Initialize test module
const NotebookTests = (function() {
  // Configuration
  const API_BASE = '/api/v1/notebook';
  
  // Test note data
  const TEST_NOTE = {
    title: "Test Note " + new Date().toISOString(),
    content: "This is a test note created at " + new Date().toTimeString(),
    note_type: "VOCABULARY",
    language: "fr",
    priority: "MEDIUM",
    example_sentences: ["Je suis une phrase d'exemple."],
    related_words: ["test", "exemple"]
  };
  
  // Storage for created entities to clean up later
  let createdNotes = [];
  let createdCategories = [];
  
  // Helper function to make API requests
  async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE}/${endpoint}`;
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'include'
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(data);
    }
    
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      if (response.status === 204) {
        return null; // No content
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error in API request to ${url}:`, error);
      throw error;
    }
  }
  
  // Test: Create a note
  async function testCreateNote() {
    console.log("📝 Testing note creation...");
    try {
      const note = await apiRequest('notes/', 'POST', TEST_NOTE);
      console.log("✅ Note created successfully:", note);
      createdNotes.push(note.id);
      return note;
    } catch (error) {
      console.error("❌ Failed to create note:", error);
      throw error;
    }
  }
  
  // Test: Get all notes
  async function testGetNotes() {
    console.log("📚 Testing notes retrieval...");
    try {
      const notes = await apiRequest('notes/');
      console.log(`✅ Retrieved ${notes.length} notes successfully`);
      return notes;
    } catch (error) {
      console.error("❌ Failed to get notes:", error);
      throw error;
    }
  }
  
  // Test: Update a note
  async function testUpdateNote(noteId) {
    if (!noteId && createdNotes.length > 0) {
      noteId = createdNotes[0];
    }
    
    if (!noteId) {
      console.error("❌ No note ID provided for update test");
      return;
    }
    
    console.log(`✏️ Testing note update for ID ${noteId}...`);
    const updateData = {
      title: "Updated Test Note " + new Date().toISOString(),
      content: "This note was updated at " + new Date().toTimeString()
    };
    
    try {
      const updatedNote = await apiRequest(`notes/${noteId}/`, 'PATCH', updateData);
      console.log("✅ Note updated successfully:", updatedNote);
      return updatedNote;
    } catch (error) {
      console.error("❌ Failed to update note:", error);
      throw error;
    }
  }
  
  // Test: Delete a note
  async function testDeleteNote(noteId) {
    if (!noteId && createdNotes.length > 0) {
      noteId = createdNotes[0];
      // Remove from tracked list
      createdNotes = createdNotes.filter(id => id !== noteId);
    }
    
    if (!noteId) {
      console.error("❌ No note ID provided for delete test");
      return;
    }
    
    console.log(`🗑️ Testing note deletion for ID ${noteId}...`);
    
    try {
      await apiRequest(`notes/${noteId}/`, 'DELETE');
      console.log("✅ Note deleted successfully");
      return true;
    } catch (error) {
      console.error("❌ Failed to delete note:", error);
      throw error;
    }
  }
  
  // Test: Create a category
  async function testCreateCategory() {
    console.log("📂 Testing category creation...");
    const categoryData = {
      name: "Test Category " + new Date().toISOString(),
      description: "This is a test category"
    };
    
    try {
      const category = await apiRequest('categories/', 'POST', categoryData);
      console.log("✅ Category created successfully:", category);
      createdCategories.push(category.id);
      return category;
    } catch (error) {
      console.error("❌ Failed to create category:", error);
      throw error;
    }
  }
  
  // Test: Get all categories
  async function testGetCategories() {
    console.log("📁 Testing categories retrieval...");
    try {
      const categories = await apiRequest('categories/');
      console.log(`✅ Retrieved ${categories.length} categories successfully`);
      return categories;
    } catch (error) {
      console.error("❌ Failed to get categories:", error);
      throw error;
    }
  }
  
  // Run all tests in sequence
  async function runAllTests() {
    console.log("🧪 Starting notebook API tests...");
    
    try {
      // Create and verify a category
      const category = await testCreateCategory();
      
      // Create, update, and delete a note
      const note = await testCreateNote();
      if (note) {
        await testUpdateNote(note.id);
        await testDeleteNote(note.id);
      }
      
      // Get all notes to verify
      await testGetNotes();
      
      // Get all categories to verify
      await testGetCategories();
      
      console.log("✅ All tests completed successfully!");
    } catch (error) {
      console.error("❌ Test sequence failed:", error);
    }
  }
  
  // Clean up created test data
  async function cleanupTestData() {
    console.log("🧹 Cleaning up test data...");
    
    // Delete all created notes
    for (const noteId of createdNotes) {
      try {
        await apiRequest(`notes/${noteId}/`, 'DELETE');
        console.log(`✅ Deleted test note ${noteId}`);
      } catch (error) {
        console.error(`❌ Failed to delete test note ${noteId}:`, error);
      }
    }
    
    // Delete all created categories
    for (const categoryId of createdCategories) {
      try {
        await apiRequest(`categories/${categoryId}/`, 'DELETE');
        console.log(`✅ Deleted test category ${categoryId}`);
      } catch (error) {
        console.error(`❌ Failed to delete test category ${categoryId}:`, error);
      }
    }
    
    // Reset tracking arrays
    createdNotes = [];
    createdCategories = [];
    
    console.log("🧹 Cleanup complete");
  }
  
  // Return public API
  return {
    createNote: testCreateNote,
    getNotes: testGetNotes,
    updateNote: testUpdateNote,
    deleteNote: testDeleteNote,
    createCategory: testCreateCategory,
    getCategories: testGetCategories,
    runAllTests,
    cleanup: cleanupTestData
  };
})();

// Instructions for manual testing in console
console.log(`
Notebook API Test Utilities

Available test functions:
- NotebookTests.createNote()
- NotebookTests.getNotes()
- NotebookTests.updateNote(noteId)
- NotebookTests.deleteNote(noteId)
- NotebookTests.createCategory()
- NotebookTests.getCategories()

Run all tests:
- NotebookTests.runAllTests()

Clean up test data:
- NotebookTests.cleanup()
`);

// Make tests available globally
window.NotebookTests = NotebookTests;