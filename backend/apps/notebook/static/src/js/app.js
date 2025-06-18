/**
 * Notebook App - Point d'entrée OWL
 * Architecture similaire à openlinguify
 */

import { NotebookApp } from "./views/NotebookApp.js";
import { NotebookService } from "./services/notebook_service.js";

// Configuration de l'environnement OWL
const env = {
    services: {
        notebook: new NotebookService(),
        user: window.userService, // Service utilisateur global
        notification: window.notificationService,
    },
    debug: window.DEBUG || false,
};

// Charger les templates XML
async function loadTemplates() {
    const response = await fetch('/static/notebook/src/xml/templates.xml');
    const xmlText = await response.text();
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, "text/xml");
    
    // Enregistrer chaque template dans OWL
    const templateNodes = xmlDoc.querySelectorAll("template");
    const templates = {};
    templateNodes.forEach(node => {
        const name = node.getAttribute("id");
        templates[name] = node.innerHTML;
    });
    
    return templates;
}

// Démarrer l'application
document.addEventListener('DOMContentLoaded', async () => {
    const templates = await loadTemplates();
    
    const { mount } = owl;
    const app = new NotebookApp();
    await mount(app, document.getElementById('notebook-app'), { 
        env,
        templates,
        dev: env.debug 
    });
    
    console.log('Notebook OWL App started');
});