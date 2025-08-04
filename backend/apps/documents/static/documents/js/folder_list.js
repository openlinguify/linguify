document.addEventListener('DOMContentLoaded', function() {
    // Calculate statistics
    calculateStatistics();
});

function calculateStatistics() {
    const rows = document.querySelectorAll('.folders-table tbody tr');
    let totalDocuments = 0;
    let emptyFolders = 0;
    let nestedFolders = 0;
    
    rows.forEach(row => {
        const documentCount = parseInt(row.querySelector('.document-count strong').textContent);
        totalDocuments += documentCount;
        
        if (documentCount === 0) {
            emptyFolders++;
        }
        
        if (row.querySelector('.parent-folder')) {
            nestedFolders++;
        }
    });
    
    document.getElementById('total-documents').textContent = totalDocuments;
    document.getElementById('empty-folders').textContent = emptyFolders;
    document.getElementById('nested-folders').textContent = nestedFolders;
}

function createFolder() {
    const form = document.getElementById('create-folder-form');
    const formData = new FormData(form);
    
    fetch('/documents/api/v1/folders/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.id) {
            location.reload();
        } else {
            alert('Erreur lors de la création du dossier');
        }
    })
    .catch(error => {
        console.error('Create folder error:', error);
        alert('Erreur lors de la création du dossier');
    });
}

function editFolder(id, name, description, parentId) {
    document.getElementById('edit-folder-id').value = id;
    document.getElementById('edit-folder-name').value = name;
    document.getElementById('edit-folder-description').value = description;
    document.getElementById('edit-folder-parent').value = parentId || '';
    
    // Remove the current folder from parent options to prevent circular reference
    const parentSelect = document.getElementById('edit-folder-parent');
    Array.from(parentSelect.options).forEach(option => {
        if (option.value == id) {
            option.disabled = true;
        } else {
            option.disabled = false;
        }
    });
    
    const modal = new bootstrap.Modal(document.getElementById('editFolderModal'));
    modal.show();
}

function updateFolder() {
    const form = document.getElementById('edit-folder-form');
    const formData = new FormData(form);
    const folderId = document.getElementById('edit-folder-id').value;
    
    fetch(`/documents/api/v1/folders/${folderId}/`, {
        method: 'PATCH',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.id) {
            location.reload();
        } else {
            alert('Erreur lors de la modification du dossier');
        }
    })
    .catch(error => {
        console.error('Update folder error:', error);
        alert('Erreur lors de la modification du dossier');
    });
}

function deleteFolder(id, name, documentCount) {
    document.getElementById('delete-folder-id').value = id;
    document.getElementById('delete-folder-name').textContent = name;
    
    const warningDiv = document.getElementById('delete-folder-warning');
    const confirmButton = document.getElementById('confirm-delete-folder');
    
    if (documentCount > 0) {
        document.getElementById('delete-folder-documents-count').textContent = documentCount;
        warningDiv.style.display = 'block';
        confirmButton.disabled = true;
    } else {
        warningDiv.style.display = 'none';
        confirmButton.disabled = false;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('deleteFolderModal'));
    modal.show();
}

function confirmDeleteFolder() {
    const folderId = document.getElementById('delete-folder-id').value;
    
    fetch(`/documents/api/v1/folders/${folderId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Erreur lors de la suppression du dossier');
        }
    })
    .catch(error => {
        console.error('Delete folder error:', error);
        alert('Erreur lors de la suppression du dossier');
    });
}

function importFolders() {
    alert('Fonctionnalité d\'import à implémenter');
    // Ici on pourrait ouvrir un modal pour uploader un fichier JSON/CSV
}

function exportFolders() {
    // Export folder structure as JSON
    const folders = [];
    document.querySelectorAll('.folders-table tbody tr').forEach(row => {
        const folderName = row.querySelector('.folder-name .name').textContent;
        const description = row.querySelector('.folder-description').textContent;
        const parent = row.querySelector('.parent-folder')?.textContent || 'Racine';
        const docCount = row.querySelector('.document-count strong').textContent;
        
        folders.push({
            name: folderName,
            description: description,
            parent: parent,
            document_count: docCount
        });
    });
    
    const dataStr = JSON.stringify(folders, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'structure_dossiers_linguify.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}
