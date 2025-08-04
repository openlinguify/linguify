document.addEventListener('DOMContentLoaded', function() {
    // Preview functionality
    const contentField = document.getElementById('id_content');
    const previewDiv = document.getElementById('content-preview');
    
    function updatePreview() {
        const content = contentField.value;
        const contentType = document.getElementById('id_content_type').value;
        
        if (!content.trim()) {
            previewDiv.innerHTML = '<p class="text-muted">L\'aperçu apparaîtra ici...</p>';
            return;
        }
        
        if (contentType === 'markdown') {
            // Simple markdown to HTML conversion
            let html = content
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/gim, '<em>$1</em>')
                .replace(/`(.*?)`/gim, '<code>$1</code>')
                .replace(/\n\n/gim, '</p><p>')
                .replace(/\n/gim, '<br>');
            
            previewDiv.innerHTML = '<p>' + html + '</p>';
        } else if (contentType === 'html') {
            previewDiv.innerHTML = content;
        } else {
            previewDiv.innerHTML = '<pre>' + content + '</pre>';
        }
    }
    
    // Update preview on content change
    contentField.addEventListener('input', updatePreview);
    document.getElementById('id_content_type').addEventListener('change', updatePreview);
    
    // Initial preview
    updatePreview();
    
    // Save draft functionality
    document.getElementById('save-draft').addEventListener('click', function() {
        const formData = new FormData(document.getElementById('document-form'));
        formData.set('save_as_draft', 'true');
        
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (response.ok) {
                alert('Brouillon sauvegardé avec succès !');
            } else {
                alert('Erreur lors de la sauvegarde du brouillon');
            }
        })
        .catch(error => {
            console.error('Save draft error:', error);
            alert('Erreur lors de la sauvegarde du brouillon');
        });
    });
});

// Template loading functions
function loadTemplate(templateType) {
    const contentField = document.getElementById('id_content');
    const titleField = document.getElementById('id_title');
    
    const templates = {
        lesson: {
            title: 'Nouvelle leçon',
            content: `# Titre de la leçon

## Objectifs d'apprentissage
- Objectif 1
- Objectif 2
- Objectif 3

## Introduction
Brève introduction au sujet...

## Contenu principal

### Section 1
Contenu de la section...

### Section 2
Contenu de la section...

## Exercices pratiques
1. Exercice 1
2. Exercice 2

## Résumé
Points clés à retenir...

## Ressources supplémentaires
- Lien 1
- Lien 2`
        },
        essay: {
            title: 'Nouvel essai',
            content: `# Titre de l'essai

## Introduction
Présentation du sujet et de la problématique...

## Développement

### Argument 1
Développement du premier argument...

### Argument 2
Développement du deuxième argument...

### Argument 3
Développement du troisième argument...

## Conclusion
Synthèse et ouverture...

## Sources
- Source 1
- Source 2`
        },
        notes: {
            title: 'Notes de cours',
            content: `# Notes de cours - [Date]

## Sujet du cours
[Titre du cours ou du chapitre]

## Points clés
- Point important 1
- Point important 2
- Point important 3

## Définitions
**Terme 1**: Définition...
**Terme 2**: Définition...

## Exemples
1. Exemple pratique 1
2. Exemple pratique 2

## Questions/Réflexions
- Question 1
- Question 2

## À retenir
Points essentiels à mémoriser...`
        },
        blank: {
            title: 'Nouveau document',
            content: ''
        }
    };
    
    if (templates[templateType]) {
        if (confirm('Charger ce modèle ? Le contenu actuel sera remplacé.')) {
            titleField.value = templates[templateType].title;
            contentField.value = templates[templateType].content;
            
            // Update preview
            const event = new Event('input');
            contentField.dispatchEvent(event);
        }
    }
}

// Auto-save functionality
function autoSave() {
    const formData = new FormData(document.getElementById('document-form'));
    formData.set('auto_save', 'true');
    
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (response.ok) {
            // Visual feedback for auto-save
            const button = document.querySelector('[onclick="autoSave()"]');
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="bi bi-check-circle text-success"></i> Sauvegardé';
            button.disabled = true;
            
            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.disabled = false;
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Auto-save error:', error);
    });
}

// Set up auto-save every 2 minutes
let autoSaveInterval;
document.addEventListener('DOMContentLoaded', function() {
    // Only enable auto-save if editing existing document
    if (document.querySelector('#id_title').value) {
        autoSaveInterval = setInterval(autoSave, 120000); // 2 minutes
    }
});
