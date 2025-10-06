(function($) {
    $(document).ready(function() {
        // Fonction pour afficher/masquer les champs selon le type de destinataire
        function toggleRecipientFields() {
            const recipientType = $('#id_recipient_type').val();

            // Masquer tous les champs par défaut
            $('.field-selected_users').hide();
            $('.field-custom_recipients').hide();

            // Afficher le champ approprié
            if (recipientType === 'selected') {
                $('.field-selected_users').show();
            } else if (recipientType === 'custom') {
                $('.field-custom_recipients').show();
            }
        }

        // Exécuter au chargement de la page
        toggleRecipientFields();

        // Exécuter quand le type de destinataire change
        $('#id_recipient_type').change(toggleRecipientFields);
    });
})(django.jQuery || jQuery);
