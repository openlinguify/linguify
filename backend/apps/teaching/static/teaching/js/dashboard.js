function bookWithTeacher(teacherId) {
    // Redirect to booking page with pre-selected teacher
    window.location.href = `/teaching/book/?teacher=${teacherId}`;
}

function startLesson(lessonId) {
    fetch(`/api/teaching/lessons/${lessonId}/start/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.meeting_url) {
            window.open(data.meeting_url, '_blank');
        }
        location.reload();
    })
    .catch(error => {
        alert('Erreur lors du démarrage du cours');
        console.error('Error:', error);
    });
}

function cancelLesson(lessonId) {
    if (confirm('Êtes-vous sûr de vouloir annuler ce cours ?')) {
        const reason = prompt('Raison de l\'annulation (optionnel):') || 'Annulé par l\'étudiant';
        
        fetch(`/api/teaching/lessons/${lessonId}/cancel/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ reason: reason })
        })
        .then(response => response.json())
        .then(data => {
            alert('Cours annulé avec succès');
            location.reload();
        })
        .catch(error => {
            alert('Erreur lors de l\'annulation');
            console.error('Error:', error);
        });
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
