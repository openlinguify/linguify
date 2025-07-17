/**
 * Community Settings JavaScript
 * Handles community-specific settings functionality
 */

function initializeCommunitySettings() {
    console.log('[Community Settings] Initializing community-specific settings...');
    
    // Profile visibility
    const visibilitySelect = document.querySelector('select[name="profile_visibility"]');
    if (visibilitySelect) {
        visibilitySelect.addEventListener('change', () => {
            const visibility = visibilitySelect.value;
            const visibilityText = {
                'public': 'Profil public - visible par tous',
                'friends': 'Profil visible par les amis uniquement',
                'private': 'Profil privé'
            };
            showTemporaryMessage(visibilityText[visibility], 'info');
            
            // Update dependent settings
            const activityShareCheckbox = document.querySelector('input[name="share_learning_activity"]');
            if (visibility === 'private' && activityShareCheckbox) {
                activityShareCheckbox.checked = false;
                activityShareCheckbox.disabled = true;
            } else if (activityShareCheckbox) {
                activityShareCheckbox.disabled = false;
            }
        });
    }
    
    // Email digest frequency
    const digestSelect = document.querySelector('select[name="email_digest_frequency"]');
    if (digestSelect) {
        digestSelect.addEventListener('change', () => {
            const frequency = digestSelect.value;
            const frequencyText = {
                'daily': 'Résumé quotidien',
                'weekly': 'Résumé hebdomadaire', 
                'monthly': 'Résumé mensuel',
                'never': 'Jamais'
            };
            showTemporaryMessage(`Fréquence des emails: ${frequencyText[frequency]}`, 'info');
        });
    }
    
    // Friend requests toggle
    const friendRequestsToggle = document.querySelector('input[name="allow_friend_requests"]');
    if (friendRequestsToggle) {
        friendRequestsToggle.addEventListener('change', () => {
            const status = friendRequestsToggle.checked ? 'activées' : 'désactivées';
            showTemporaryMessage(`Demandes d'amis ${status}`, 'info');
        });
    }
    
    // Community features toggles
    const communityToggles = [
        { name: 'show_online_status', message: 'Statut en ligne' },
        { name: 'allow_direct_messages', message: 'Messages directs' },
        { name: 'share_learning_activity', message: 'Partage d\'activité' },
        { name: 'participate_challenges', message: 'Participation aux défis' }
    ];
    
    communityToggles.forEach(toggle => {
        const element = document.querySelector(`input[name="${toggle.name}"]`);
        if (element) {
            element.addEventListener('change', () => {
                const status = element.checked ? 'activé' : 'désactivé';
                showTemporaryMessage(`${toggle.message} ${status}`, 'info');
            });
        }
    });
    
    console.log('[Community Settings] Community settings initialized successfully');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeCommunitySettings();
});