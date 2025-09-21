/** @odoo-module **/

import { mount, whenReady } from "@odoo/owl";
import { makeEnv, startServices } from "@web/env";
import { LearningDashboard } from "./components/learning_dashboard/learning_dashboard";
import { templates } from "@web/core/assets";

// Import services
import "./services/learning_service";

console.log('🚀 Language Learning OWL App Starting...');

async function startApp() {
    try {
        console.log('📦 Setting up OWL environment...');

        // Créer l'environnement OWL avec les services
        const env = makeEnv();
        await startServices(env);

        console.log('🎯 Mounting LearningDashboard component...');

        // Monter le composant principal
        const appContainer = document.getElementById('language-learning-app');
        if (!appContainer) {
            throw new Error('Container #language-learning-app not found');
        }

        await mount(LearningDashboard, appContainer, {
            env,
            templates,
            dev: true,
            name: "Language Learning"
        });

        console.log('✅ Language Learning OWL app mounted successfully!');

    } catch (error) {
        console.error('❌ Error starting Language Learning app:', error);

        // Fallback: afficher un message d'erreur
        const appContainer = document.getElementById('language-learning-app');
        if (appContainer) {
            appContainer.innerHTML = `
                <div class="alert alert-danger m-4">
                    <h5><i class="bi bi-exclamation-triangle"></i> Erreur de chargement</h5>
                    <p>Impossible de charger l'interface d'apprentissage.</p>
                    <small class="text-muted">Erreur: ${error.message}</small>
                </div>
            `;
        }
    }
}

// Démarrer l'app quand le DOM est prêt
whenReady(startApp);