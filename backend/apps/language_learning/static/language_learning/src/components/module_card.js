/** @odoo-module **/

import { Component } from "@odoo/owl";

export class ModuleCard extends Component {
  static template = "language_learning.ModuleCard";

  static props = {
    module: Object,
    onModuleClick: { type: Function, optional: true }
  };

  onClick() {
    if (this.props.onModuleClick) {
      this.props.onModuleClick(this.props.module.id);
    }
  }

  get difficultyBadgeClass() {
    const moduleType = this.props.module.module_type;
    switch (moduleType) {
      case 'vocabulary': return 'bg-success';
      case 'grammar': return 'bg-primary';
      case 'listening': return 'bg-info';
      case 'speaking': return 'bg-warning';
      case 'reading': return 'bg-secondary';
      case 'writing': return 'bg-dark';
      case 'culture': return 'bg-light text-dark';
      case 'review': return 'bg-danger';
      default: return 'bg-secondary';
    }
  }
}