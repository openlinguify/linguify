(function($) {
    $(document).ready(function() {
        // Sélecteur du champ de type de leçon
        var lessonTypeField = $('#id_lesson_type');
        // Conteneur du champ de profession
        var professionalFieldContainer = $('.field-professional_field').closest('.form-row');
        // Ensemble de champs professionnel
        var professionalFieldset = $('.professional-settings').closest('fieldset');
        
        // Fonction pour mettre à jour la visibilité
        function updateProfessionalFieldVisibility() {
            var isVisible = lessonTypeField.val() === 'professional';
            
            if (isVisible) {
                professionalFieldContainer.show();
                professionalFieldset.show();
                $('#id_professional_field').prop('disabled', false);
                $('#id_professional_field').attr('required', 'required');
            } else {
                professionalFieldContainer.hide();
                professionalFieldset.hide();
                $('#id_professional_field').prop('disabled', true);
                $('#id_professional_field').removeAttr('required');
            }
        }
        
        // Exécuter la fonction au chargement
        updateProfessionalFieldVisibility();
        
        // Ajouter un écouteur d'événement pour le changement de type
        lessonTypeField.on('change', updateProfessionalFieldVisibility);
    });
})(django.jQuery);