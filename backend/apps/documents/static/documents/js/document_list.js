// View mode toggle
function toggleViewMode() {
    const grid = document.getElementById('documents-grid');
    grid.classList.toggle('list-view');
}

// Sorting
function applySorting(value) {
    const url = new URL(window.location);
    url.searchParams.set('ordering', value);
    window.location = url;
}

// Filter handling
document.querySelectorAll('input[name="view-filter"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const url = new URL(window.location);
        
        if (this.id === 'my-docs') {
            url.searchParams.set('owner', 'me');
            url.searchParams.delete('shared');
        } else if (this.id === 'shared-docs') {
            url.searchParams.set('shared', 'true');
            url.searchParams.delete('owner');
        } else {
            url.searchParams.delete('owner');
            url.searchParams.delete('shared');
        }
        
        window.location = url;
    });
});

// Delete document handling
let deleteDocumentId = null;

document.addEventListener('click', function(e) {
    if (e.target.matches('[data-action="delete-document"]')) {
        e.preventDefault();
        
        deleteDocumentId = e.target.dataset.documentId;
        const documentTitle = e.target.dataset.documentTitle;
        
        document.getElementById('delete-document-title').textContent = documentTitle;
        
        const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
        modal.show();
    }
});

document.getElementById('confirm-delete').addEventListener('click', function() {
    if (deleteDocumentId) {
        fetch(`/documents/api/v1/documents/${deleteDocumentId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Erreur lors de la suppression');
            }
        })
        .catch(error => {
            console.error('Delete error:', error);
            alert('Erreur lors de la suppression');
        });
    }
});