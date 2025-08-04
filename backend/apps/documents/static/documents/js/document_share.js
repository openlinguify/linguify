document.addEventListener('DOMContentLoaded', function() {
    // Add share form submission
    document.getElementById('add-share-form').addEventListener('submit', function(e) {
        e.preventDefault();
        addShare();
    });
});

function addShare() {
    const form = document.getElementById('add-share-form');
    const formData = new FormData(form);
    
    fetch(`/documents/api/v1/documents/{{ document.id }}/share/`, {
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
            alert(data.message || 'Erreur lors du partage');
        }
    })
    .catch(error => {
        console.error('Add share error:', error);
        alert('Erreur lors du partage');
    });
}

function changePermission(shareId, currentPermission) {
    document.getElementById('change-share-id').value = shareId;
    document.getElementById('new-permission-level').value = currentPermission;
    
    const modal = new bootstrap.Modal(document.getElementById('changePermissionModal'));
    modal.show();
}

function confirmChangePermission() {
    const shareId = document.getElementById('change-share-id').value;
    const newPermission = document.getElementById('new-permission-level').value;
    
    fetch(`/documents/api/v1/shares/${shareId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            permission_level: newPermission
        })
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Erreur lors du changement de permissions');
        }
    })
    .catch(error => {
        console.error('Change permission error:', error);
        alert('Erreur lors du changement de permissions');
    });
}

function removeShare(shareId, userName) {
    if (confirm(`Retirer l'accès de ${userName} ?`)) {
        fetch(`/documents/api/v1/shares/${shareId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Erreur lors de la suppression du partage');
            }
        })
        .catch(error => {
            console.error('Remove share error:', error);
            alert('Erreur lors de la suppression du partage');
        });
    }
}

function extendExpiration(shareId) {
    const newDate = prompt('Nouvelle date d\'expiration (YYYY-MM-DD HH:MM):');
    if (newDate) {
        fetch(`/documents/api/v1/shares/${shareId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                expires_at: newDate
            })
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Erreur lors de la modification de l\'expiration');
            }
        })
        .catch(error => {
            console.error('Extend expiration error:', error);
            alert('Erreur lors de la modification de l\'expiration');
        });
    }
}

function copyShareLink() {
    const link = `${window.location.origin}/documents/{{ document.id }}/`;
    navigator.clipboard.writeText(link).then(() => {
        alert('Lien copié dans le presse-papiers !');
    }).catch(() => {
        alert('Erreur lors de la copie du lien');
    });
}

function generateShareCode() {
    alert('Fonctionnalité QR Code à implémenter');
}

function exportShareList() {
    const shares = [];
    document.querySelectorAll('.share-item').forEach(item => {
        const name = item.querySelector('.collaborator-name').textContent;
        const email = item.querySelector('.collaborator-email').textContent;
        const permission = item.querySelector('.permission-badge .badge').textContent;
        shares.push(`${name} (${email}) - ${permission}`);
    });
    
    const content = `Liste des collaborateurs pour: {{ document.title }}\n\n${shares.join('\n')}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'collaborateurs_{{ document.title|slugify }}.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
