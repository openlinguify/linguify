    function search() {
        // Get the value from the input element
        var searchTerm = document.getElementById("search-input").value;

        // Perform some processing or logic based on the search term
        // For example, you can use an if-else statement or a switch statement

        // Simulate a simple example by checking for specific search terms
        if (searchTerm === "apple") {
            document.getElementById("search-results").innerHTML =
                "Search term matched: apple";
        } else if (searchTerm === "banana") {
            document.getElementById("search-results").innerHTML =
                "Search term matched: banana";
        } else {
            document.getElementById("search-results").innerHTML =
                "No matching result for the search term: " + searchTerm;
        }
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

function search() {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById('searchInput');
    filter = input.value.toUpperCase();

    // Send AJAX request to the backend
    $.ajax({
        type: 'GET',
        url: '/search/',
        data: {
            'query': filter
        },
        success: function(response) {
            // Update the search results with the filtered data
            $('#wordList').html(response);
        },
        error: function(error) {
            console.log(error);
        }
    });
}
