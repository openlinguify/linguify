#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { DOMParser } = require('xmldom');

// Paths
const templatesDir = path.join(__dirname, '../apps/language_learning/static/language_learning/src/templates');
const outputFile = path.join(__dirname, '../apps/language_learning/static/language_learning/src/assets.js');

console.log('🔧 Generating assets.js from XML templates...');

// Function to parse XML and extract template content
function parseXMLTemplate(xmlContent, filename) {
  try {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlContent, 'text/xml');

    const templateNodes = xmlDoc.getElementsByTagName('t');
    const templates = {};

    for (let i = 0; i < templateNodes.length; i++) {
      const node = templateNodes[i];
      const tName = node.getAttribute('t-name');
      if (tName) {
        // Get inner content without the outer <t> tag
        const content = node.toString()
          .replace(/^<t[^>]*>/, '')
          .replace(/<\/t>$/, '')
          .trim();
        templates[tName] = content;
        console.log(`  ✅ Found template: ${tName} in ${filename}`);
      }
    }

    return templates;
  } catch (error) {
    console.error(`❌ Error parsing ${filename}:`, error.message);
    return {};
  }
}

// Read all XML files in templates directory
const xmlFiles = fs.readdirSync(templatesDir).filter(file => file.endsWith('.xml'));
const allTemplates = {};

xmlFiles.forEach(filename => {
  const filePath = path.join(templatesDir, filename);
  const xmlContent = fs.readFileSync(filePath, 'utf8');
  const templates = parseXMLTemplate(xmlContent, filename);
  Object.assign(allTemplates, templates);
});

// Generate assets.js content
const assetsContent = `/** @odoo-module **/

import { xml } from "@odoo/owl";

/*
 * ⚠️  CE FICHIER EST GÉNÉRÉ AUTOMATIQUEMENT - NE PAS ÉDITER MANUELLEMENT ⚠️
 *
 * Les templates ci-dessous sont générés à partir des fichiers XML dans ./templates/
 *
 * Pour modifier un template :
 * 1. Éditez le fichier XML correspondant dans ./templates/
 * 2. Lancez: npm run build:language-learning
 * 3. Ce fichier sera automatiquement regénéré
 *
 * Fichiers source XML :
 * - ./templates/UnitCard.xml → language_learning.UnitCard
 * - ./templates/ProgressPanel.xml → language_learning.ProgressPanel
 * - ./templates/Navbar.xml → language_learning.Navbar
 * - ./templates/Dashboard.xml → language_learning.Dashboard
 */

export const templates = {
${Object.entries(allTemplates).map(([name, content]) =>
  `  "${name}": xml\`${content}\``
).join(',\n\n')}
};

console.log('🎯 Templates loaded from generated assets:', Object.keys(templates));
`;

// Write the generated file
fs.writeFileSync(outputFile, assetsContent);

console.log(`✅ Generated ${outputFile} with ${Object.keys(allTemplates).length} templates:`);
Object.keys(allTemplates).forEach(name => console.log(`   - ${name}`));
console.log('\n🚀 Run "npm run build:language-learning" to rebuild with new templates');