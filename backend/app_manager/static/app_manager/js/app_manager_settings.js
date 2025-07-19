function configureApp(appCode, appName) {
    // TODO: Remplacer par une vraie modal de configuration
    const response = confirm(`Voulez-vous configurer l'application "${appName}" (${appCode}) ?\n\nCette fonctionnalité ouvrira bientôt une fenêtre de configuration dédiée.`);
    
    if (response) {
        // Pour l'instant, afficher un message informatif
        alert(`Configuration de "${appName}" en cours de développement.\n\nCode de l'application: ${appCode}\n\nFonctionnalités à venir:\n- Paramètres spécifiques à l'app\n- Gestion des permissions\n- Configuration avancée`);
    }
}

// Gestion du formulaire de boutique d'applications
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form[method="post"]');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Récupérer les valeurs des checkboxes
            const autoUpdates = form.querySelector('input[name="auto_updates"]').checked;
            const communityApps = form.querySelector('input[name="community_apps"]').checked;
            
            // Afficher un message de confirmation
            alert(`Paramètres sauvegardés !\n\nMises à jour automatiques: ${autoUpdates ? 'Activées' : 'Désactivées'}\nApplications communautaires: ${communityApps ? 'Activées' : 'Désactivées'}`);
            
            // Envoyer les données au serveur
            setTimeout(() => {
                form.submit();
            }, 1000);
        });
    }
});