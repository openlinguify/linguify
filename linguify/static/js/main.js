    <!-- Ajoutez vos scripts JS à la fin du corps si nécessaire -->
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js" integrity="sha384-I7E8VVD/ismYTF4hNIPjVp/Zjvgyol6VFvRkX/vR+Vc4jQkC+hVqc2pM8ODewa9r" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-+0n0l4+Zb2UWpJ6j7U5p/RVv2v6p5Z6p7j5g8n7Zq5" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js" integrity="sha384-0pUGZvbkm6XF6gxjEnlmuGrJXVbNuzT9qBBavbLwCsOGabYfZo0T0to5eqruptLy" crossorigin="anonymous"></script>



// Fonction pour gérer la recherche côté client
function search() {
    // Récupérer le terme de recherche saisi par l'utilisateur
    var searchTerm = document.getElementById("searchInput").value;

    // Envoyer une requête AJAX au backend
    $.ajax({
        type: 'GET',
        url: '/search/',
        data: {
            'query': searchTerm
        },
        success: function (response) {
            // Mettre à jour les résultats de la recherche avec les données filtrées
            $('#wordList').html(response);
        },
        error: function (error) {
            console.log(error);
        }
    });
}

// Fonction pour gérer l'envoi de commentaire
const handleCommentSubmission = () => {
    // Récupérer le commentaire saisi par l'utilisateur
    const comment = document.getElementById("comment-input").value;

    // Afficher le commentaire à l'utilisateur (ou effectuer d'autres actions)
    alert("Votre commentaire : " + comment);

    // Effacer le champ de commentaire après l'envoi
    document.getElementById("comment-input").value = "";
};

// Ajout d'un gestionnaire d'événement au chargement du document
document.addEventListener("DOMContentLoaded", () => {
    // Ajout d'un gestionnaire d'événement pour le bouton d'envoi de commentaire
    const submitButton = document.getElementById("submit-comment");
    submitButton.addEventListener("click", handleCommentSubmission);
});
