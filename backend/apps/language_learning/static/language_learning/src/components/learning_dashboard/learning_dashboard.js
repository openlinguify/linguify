/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { UnitCard } from "../unit_card/unit_card";
import { ProgressPanel } from "../progress_panel/progress_panel";
import { Navbar } from "../navbar/navbar";

export class LearningDashboard extends Component {
    static template = "language_learning.LearningDashboard";
    static components = { UnitCard, ProgressPanel, Navbar };

    setup() {
        this.learningService = useService("learning");
        this.state = useState({
            isReady: false
        });

        onWillStart(async () => {
            // Charger les données initiales depuis le template
            await this.loadInitialData();
            this.state.isReady = true;
        });
    }

    async loadInitialData() {
        try {
            const dataScript = document.getElementById('language-learning-data');
            if (dataScript) {
                const data = JSON.parse(dataScript.textContent);
                await this.learningService.loadData(data);
                console.log('✅ Learning data loaded successfully');
            }
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
        }
    }

    get learningState() {
        return this.learningService.state;
    }

    onUnitClick(unitId) {
        this.learningService.setActiveUnit(unitId);
    }

    onModuleComplete(moduleId) {
        this.learningService.updateModuleProgress(moduleId, true);
    }
}