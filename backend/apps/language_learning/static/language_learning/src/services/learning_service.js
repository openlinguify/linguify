/** @odoo-module **/

import { reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";

/**
 * Service pour gérer les données d'apprentissage des langues
 */
export const learningService = {
    dependencies: [],

    start() {
        const state = reactive({
            selectedLanguage: 'EN',
            selectedLanguageName: 'English',
            courseUnits: [],
            activeUnit: null,
            activeUnitModules: [],
            userStreak: 0,
            isLoading: false,
            error: null
        });

        /**
         * Charger les données depuis le backend Django
         */
        async function loadData(data) {
            state.isLoading = true;
            try {
                if (data) {
                    Object.assign(state, {
                        selectedLanguage: data.selectedLanguage || 'EN',
                        selectedLanguageName: data.selectedLanguageName || 'English',
                        courseUnits: data.courseUnits || [],
                        activeUnit: data.activeUnit || null,
                        activeUnitModules: data.activeUnitModules || [],
                        userStreak: data.userStreak || 0,
                        error: null
                    });
                }
            } catch (error) {
                state.error = error.message;
                console.error('Error loading learning data:', error);
            } finally {
                state.isLoading = false;
            }
        }

        /**
         * Mettre à jour la progression d'un module
         */
        async function updateModuleProgress(moduleId, isCompleted) {
            try {
                // Simulation d'appel API - à remplacer par vrai appel Django
                const response = await fetch(`/api/learning/modules/${moduleId}/progress/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    },
                    body: JSON.stringify({ is_completed: isCompleted })
                });

                if (response.ok) {
                    // Mettre à jour l'état local
                    const moduleIndex = state.activeUnitModules.findIndex(m => m.id === moduleId);
                    if (moduleIndex !== -1) {
                        state.activeUnitModules[moduleIndex].is_completed = isCompleted;
                    }
                }
            } catch (error) {
                console.error('Error updating module progress:', error);
                state.error = error.message;
            }
        }

        /**
         * Changer d'unité active
         */
        function setActiveUnit(unitId) {
            const unit = state.courseUnits.find(u => u.id === unitId);
            if (unit) {
                state.activeUnit = unit;
                // TODO: Charger les modules de cette unité
            }
        }

        return {
            state,
            loadData,
            updateModuleProgress,
            setActiveUnit
        };
    }
};

registry.category("services").add("learning", learningService);