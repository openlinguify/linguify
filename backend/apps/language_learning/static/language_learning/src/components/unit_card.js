/** @odoo-module **/

import { Component } from "@odoo/owl";

export class UnitCard extends Component {
  static template = "language_learning.UnitCard";

  static props = {
    unit: Object,
    isActive: { type: Boolean, optional: true },
    onUnitClick: { type: Function, optional: true }
  };

  onClick() {
    if (this.props.onUnitClick) {
      this.props.onUnitClick(this.props.unit.id);
    }
  }

  get progressWidth() {
    return `${this.props.unit.progress_percentage || 0}%`;
  }

  get progressClass() {
    const percentage = this.props.unit.progress_percentage || 0;
    if (percentage === 100) return 'bg-success';
    if (percentage >= 50) return 'bg-primary';
    if (percentage > 0) return 'bg-warning';
    return 'bg-secondary';
  }
}