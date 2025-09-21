/** @odoo-module **/

import { xml } from "@odoo/owl";

// Import individual template files
import unitCardXML from 'raw-loader!./templates/UnitCard.xml';
import progressPanelXML from 'raw-loader!./templates/ProgressPanel.xml';
import navbarXML from 'raw-loader!./templates/Navbar.xml';
import dashboardXML from 'raw-loader!./templates/Dashboard.xml';

// Helper function to parse XML and extract templates
function parseTemplateXML(xmlContent) {
  const parser = new DOMParser();
  const xmlDoc = parser.parseFromString(xmlContent, 'text/xml');
  const templates = {};

  const templateNodes = xmlDoc.querySelectorAll('t[t-name]');
  templateNodes.forEach(node => {
    const name = node.getAttribute('t-name');
    const content = node.innerHTML;
    templates[name] = xml`${content}`;
  });

  return templates;
}

// Parse all template files and merge them
const allTemplates = {
  ...parseTemplateXML(unitCardXML),
  ...parseTemplateXML(progressPanelXML),
  ...parseTemplateXML(navbarXML),
  ...parseTemplateXML(dashboardXML)
};

export const templates = allTemplates;

console.log('🎯 Templates loaded from XML files:', Object.keys(templates));