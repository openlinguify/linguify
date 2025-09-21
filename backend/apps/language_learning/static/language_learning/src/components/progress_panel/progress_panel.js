/** @odoo-module **/

import { Component } from "@odoo/owl";

export class ProgressPanel extends Component {
    static template = "language_learning.ProgressPanel";
    static props = {
        userStreak: Number,
        unitsCount: Number,
        completedUnitsCount: { type: Number, optional: true },
        onContinueLearning: { type: Function, optional: true }
    };

    onContinueClick() {
        if (this.props.onContinueLearning) {
            this.props.onContinueLearning();
        }
    }

    get completedUnits() {
        return this.props.completedUnitsCount || 0;
    }

    get streakIcon() {
        if (this.props.userStreak >= 30) return '🔥';
        if (this.props.userStreak >= 7) return '⚡';
        if (this.props.userStreak >= 3) return '✨';
        return '🌟';
    }
}