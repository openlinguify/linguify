// apps/revision/static/src/js/app.js
import { RevisionApp } from "./views/RevisionApp.js";
import { RevisionService } from "./services/revision_service.js";

// Configuration globale
const { Component, Environment, mount, loadFile } = owl;

// Initialisation des services
const env = {
    services: {
        revision: new RevisionService(),
        user: window.userService || {},
        notification: window.notificationService || {},
    },
    debug: window.DEBUG || false,
};

// Chargement des templates XML
async function loadTemplates() {
    try {
        const templatesPath = '/static/src/xml/revision_templates.xml';
        await loadFile(templatesPath);
        console.log('📄 Templates revision chargés avec succès');
    } catch (error) {
        console.error('❌ Erreur lors du chargement des templates revision:', error);
        throw error;
    }
}

// Initialisation de l'application
async function initRevisionApp() {
    try {
        await loadTemplates();
        
        const revisionContainer = document.getElementById('revision-app');
        if (!revisionContainer) {
            throw new Error('Container #revision-app non trouvé');
        }

        const app = await mount(RevisionApp, revisionContainer, { env });
        console.log('🎯 Application Revision/Flashcard initialisée avec succès');
        
        return app;
    } catch (error) {
        console.error('❌ Erreur lors de l\'initialisation de l\'application revision:', error);
        
        // Affichage d'un message d'erreur user-friendly
        const container = document.getElementById('revision-app');
        if (container) {
            container.innerHTML = `
                <div style="padding: 40px; text-align: center; background: white; margin: 20px; border-radius: 8px; border: 1px solid #fecaca; background: #fef2f2;">
                    <h2 style="color: #ef4444; margin: 0 0 15px;">❌ Erreur de chargement</h2>
                    <p style="color: #6b7280; margin-bottom: 20px;">Impossible de charger l'application revision.</p>
                    <button onclick="window.location.reload()" style="background: #6366f1; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer;">
                        🔄 Recharger la page
                    </button>
                </div>
            `;
        }
    }
}

// Initialiser quand le DOM est prêt
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRevisionApp);
} else {
    initRevisionApp();
}

export { initRevisionApp };