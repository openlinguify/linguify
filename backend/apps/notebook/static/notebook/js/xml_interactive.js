/* XML Interactive Views JavaScript */

// Variables globales
let selectedNoteId = null;

// Obtenir le token CSRF
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Fonction pour faire des requêtes AJAX
async function makeAPICall(url, method, data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        const result = await response.json();

        if (result.success) {
            alert('✅ ' + result.message);
            location.reload(); // Recharger la page pour voir les changements
        } else {
            alert('❌ Erreur: ' + result.error);
        }
    } catch (error) {
        alert('❌ Erreur de connexion: ' + error.message);
    }
}

// Charger une note dans le formulaire d'édition
async function editItem(id, type) {
    if (type === 'note') {
        try {
            // Récupérer les données de la note depuis l'API
            const response = await fetch(`/api/v1/notebook/notes/${id}/`);
            const note = await response.json();

            // Remplir le formulaire
            document.getElementById('noteId').value = note.id;
            document.getElementById('noteTitle').value = note.title || '';
            document.getElementById('noteContent').value = note.content || '';
            document.getElementById('noteLanguage').value = note.language || '';
            document.getElementById('notePriority').value = note.priority || 'MEDIUM';

            selectedNoteId = id;

            // Mettre en surbrillance la carte sélectionnée
            document.querySelectorAll('.kanban-card').forEach(card => {
                card.classList.remove('selected');
            });
            document.querySelector(`[data-note-id="${id}"]`)?.classList.add('selected');

            // Scroll vers le formulaire sur mobile
            if (window.innerWidth < 768) {
                document.querySelector('.note-editor').scrollIntoView({ behavior: 'smooth' });
            }
        } catch (error) {
            alert('❌ Erreur lors du chargement de la note: ' + error.message);
        }
    } else {
        alert('Édition de ' + type + ' ID: ' + id + '\n\nFonctionnalité en cours de développement.');
    }
}

// Sauvegarder une note (création ou mise à jour)
async function saveNote() {
    const noteId = document.getElementById('noteId').value;
    const title = document.getElementById('noteTitle').value.trim();
    const content = document.getElementById('noteContent').value.trim();
    const language = document.getElementById('noteLanguage').value;
    const priority = document.getElementById('notePriority').value;

    if (!title) {
        alert('⚠️ Le titre est obligatoire');
        return;
    }

    const noteData = {
        title: title,
        content: content,
        language: language,
        priority: priority
    };

    try {
        let url, method;
        if (noteId) {
            // Mise à jour
            url = `/api/v1/notebook/xml/api/notes/${noteId}/update/`;
            method = 'POST';
        } else {
            // Création
            url = '/api/v1/notebook/notes/';
            method = 'POST';
        }

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(noteData)
        });

        const result = await response.json();

        if (response.ok) {
            alert('✅ Note sauvegardée avec succès!');
            clearForm();
            location.reload(); // Recharger pour voir les changements
        } else {
            alert('❌ Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    } catch (error) {
        alert('❌ Erreur de connexion: ' + error.message);
    }
}

// Vider le formulaire pour créer une nouvelle note
function clearForm() {
    document.getElementById('noteId').value = '';
    document.getElementById('noteTitle').value = '';
    document.getElementById('noteContent').value = '';
    document.getElementById('noteLanguage').value = '';
    document.getElementById('notePriority').value = 'MEDIUM';
    selectedNoteId = null;

    // Enlever la sélection des cartes
    document.querySelectorAll('.kanban-card').forEach(card => {
        card.classList.remove('selected');
    });
}

// Actualiser les données
function refreshData() {
    location.reload();
}

// Supprimer une note
function deleteItem(id, type) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
        if (type === 'note') {
            const url = `/api/v1/notebook/xml/api/notes/${id}/delete/`;
            makeAPICall(url, 'DELETE');
        } else {
            alert('Suppression de ' + type + ' ID: ' + id + '\n\nFonctionnalité en cours de développement.');
        }
    }
}

// Dupliquer une note
function duplicateItem(id, type) {
    if (type === 'note') {
        const url = `/api/v1/notebook/xml/api/notes/${id}/duplicate/`;
        makeAPICall(url, 'POST');
    } else {
        alert('Duplication de ' + type + ' ID: ' + id + '\n\nFonctionnalité en cours de développement.');
    }
}

// Partager une note
function shareItem(id) {
    alert('Partage de la note ID: ' + id + '\n\nFonctionnalité en cours de développement.');
}

// Marquer comme révisé
function markReviewed(id) {
    const url = `/api/v1/notebook/xml/api/notes/${id}/update/`;
    makeAPICall(url, 'POST', { review_count: 1 });
}

// Épingler/Désépingler une note
function togglePin(id) {
    const url = `/api/v1/notebook/xml/api/notes/${id}/update/`;
    // Note: il faudrait récupérer l'état actuel pour basculer
    makeAPICall(url, 'POST', { is_pinned: true });
}

// Archiver/Désarchiver une note
function toggleArchive(id) {
    const url = `/api/v1/notebook/xml/api/notes/${id}/update/`;
    // Note: il faudrait récupérer l'état actuel pour basculer
    makeAPICall(url, 'POST', { is_archived: true });
}

// Toggle sidebar sur mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('show');
}

// Initialisation quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    // Ajouter un bouton mobile pour ouvrir la sidebar
    if (window.innerWidth < 768) {
        const mobileBtn = document.createElement('button');
        mobileBtn.className = 'btn btn-primary position-fixed';
        mobileBtn.style.cssText = 'top: 80px; left: 10px; z-index: 1041;';
        mobileBtn.innerHTML = '☰ Menu';
        mobileBtn.onclick = toggleSidebar;
        document.body.appendChild(mobileBtn);
    }

    // Fermer la sidebar en cliquant à l'extérieur sur mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth < 768) {
            const sidebar = document.querySelector('.sidebar');
            if (!sidebar.contains(e.target) && !e.target.closest('.mobile-menu-btn')) {
                sidebar.classList.remove('show');
            }
        }
    });
});