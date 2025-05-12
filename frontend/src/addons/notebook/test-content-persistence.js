/**
 * Test script for verifying notebook content persistence
 * 
 * This is a browser console script for testing note data persistence
 * Copy and paste it into the browser console when on the notebook page
 */

(function() {
  console.log('Starting notebook content persistence test...');
  
  // Helper function to log a note's content
  function logNoteContent(note, label) {
    console.log(`--- ${label || 'Note Content'} ---`);
    console.log(`Title: "${note.title}"`);
    console.log(`Content length: ${note.content?.length || 0} chars`);
    console.log(`Translation: "${note.translation || ''}"`);
    console.log(`Example sentences: ${note.example_sentences?.length || 0}`);
    console.log(`Related words: ${note.related_words?.length || 0}`);
    console.log(`Last updated: ${note.updated_at}`);
    console.log('------------------------');
  }
  
  // Get selected note data from UI
  function getSelectedNoteFromState() {
    // Find the Notebook component in React DevTools
    // This is a simplified approach - in practice may need more complex traversal
    let selectedNote = null;
    
    // Try to get from React DevTools
    if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
      console.log('React DevTools detected, attempting to find selected note...');
      // Implementation would depend on internal structure
    }
    
    // Fallback to data attributes or DOM structure
    const titleElement = document.querySelector('input[placeholder="Note title"]');
    if (titleElement) {
      console.log(`Current note title in UI: "${titleElement.value}"`);
    }
    
    // Look for other elements
    const contentElement = document.querySelector('[contenteditable="true"]');
    if (contentElement) {
      console.log(`Content element found with ${contentElement.textContent.length} chars`);
    }
    
    return selectedNote;
  }
  
  // Test API client directly
  async function testAPI() {
    console.log('Testing notebook API...');
    
    try {
      // Get all notes
      const response = await fetch('/api/v1/notebook/notes/');
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      const notes = await response.json();
      console.log(`Retrieved ${notes.length} notes from API`);
      
      if (notes.length > 0) {
        // Get first note details
        const firstNoteId = notes[0].id;
        console.log(`Getting details for note #${firstNoteId}`);
        
        const detailResponse = await fetch(`/api/v1/notebook/notes/${firstNoteId}/`);
        if (!detailResponse.ok) {
          throw new Error(`API detail request failed: ${detailResponse.status}`);
        }
        
        const noteDetail = await detailResponse.json();
        logNoteContent(noteDetail, 'Note from API');
        
        // Compare with what's in the UI
        const uiNote = getSelectedNoteFromState();
        if (uiNote) {
          logNoteContent(uiNote, 'Note from UI');
        }
        
        return {
          apiNote: noteDetail,
          uiNote
        };
      }
    } catch (error) {
      console.error('API test failed:', error);
    }
  }
  
  // Run tests
  testAPI().then(results => {
    console.log('Test completed!');
    
    if (results?.apiNote) {
      // Add verification tips
      console.log('Verification steps:');
      console.log('1. Check that the note content from API has the expected data');
      console.log('2. Make changes to the note and save');
      console.log('3. Refresh the page and verify changes persisted');
      console.log('4. Run this test again to confirm data consistency');
    }
  });
  
  // Add global access for manual testing
  window.notebookTest = {
    logNoteContent,
    testAPI,
    getSelectedNoteFromState
  };
  
  console.log('Test script loaded. Access functions via window.notebookTest');
})();