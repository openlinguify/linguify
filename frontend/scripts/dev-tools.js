#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// CLI for rapid development
const args = process.argv.slice(2);
const command = args[0];

const templates = {
  component: (name) => `import React from 'react';

interface ${name}Props {
  className?: string;
}

const ${name}: React.FC<${name}Props> = ({ className }) => {
  return (
    <div className={className}>
      ${name} Component
    </div>
  );
};

export default ${name};`,

  hook: (name) => `import { useState, useEffect } from 'react';

export const ${name} = () => {
  const [state, setState] = useState(null);

  useEffect(() => {
    // Hook logic here
  }, []);

  return { state };
};`,

  api: (name) => `import { apiClient } from '@/core/api/optimizedApiClient';

export const ${name}API = {
  getAll: async () => {
    const response = await apiClient.get('/${name.toLowerCase()}');
    return response.data;
  },
  
  getById: async (id: string) => {
    const response = await apiClient.get(\`/${name.toLowerCase()}/\${id}\`);
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await apiClient.post('/${name.toLowerCase()}', data);
    return response.data;
  },
  
  update: async (id: string, data: any) => {
    const response = await apiClient.put(\`/${name.toLowerCase()}/\${id}\`, data);
    return response.data;
  },
  
  delete: async (id: string) => {
    const response = await apiClient.delete(\`/${name.toLowerCase()}/\${id}\`);
    return response.data;
  },
};`,

  page: (name) => `'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';

export default function ${name}Page() {
  const { t } = useTranslation();
  
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">${name}</h1>
      <div>
        {/* Page content */}
      </div>
    </div>
  );
}`
};

const createFile = (filePath, content) => {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(filePath, content);
  console.log(`✅ Created: ${filePath}`);
};

const commands = {
  component: (name, location = 'components') => {
    const componentPath = path.join('src', location, name);
    const filePath = path.join(componentPath, `${name}.tsx`);
    const indexPath = path.join(componentPath, 'index.ts');
    
    createFile(filePath, templates.component(name));
    createFile(indexPath, `export { default } from './${name}';`);
  },
  
  hook: (name) => {
    const filePath = path.join('src', 'hooks', `${name}.ts`);
    createFile(filePath, templates.hook(name));
  },
  
  api: (name) => {
    const filePath = path.join('src', 'api', `${name}API.ts`);
    createFile(filePath, templates.api(name));
  },
  
  page: (name, route) => {
    const pagePath = path.join('src', 'app', route || name.toLowerCase());
    const filePath = path.join(pagePath, 'page.tsx');
    createFile(filePath, templates.page(name));
  },
  
  addon: (name) => {
    const addonPath = path.join('src', 'addons', name);
    const dirs = ['api', 'components', 'hooks', 'types'];
    
    dirs.forEach(dir => {
      const dirPath = path.join(addonPath, dir);
      fs.mkdirSync(dirPath, { recursive: true });
      createFile(path.join(dirPath, 'index.ts'), `// ${name} ${dir}`);
    });
    
    // Create main component
    const mainComponent = `${name.charAt(0).toUpperCase() + name.slice(1)}Main`;
    createFile(
      path.join(addonPath, 'components', `${mainComponent}.tsx`),
      templates.component(mainComponent)
    );
    
    console.log(`✅ Created addon: ${name}`);
  },
  
  analyze: () => {
    console.log('🔍 Analyzing bundle...');
    execSync('ANALYZE=true npm run build', { stdio: 'inherit' });
  },
  
  perf: () => {
    console.log('📊 Running performance tests...');
    execSync('npm run build && npm run start', { stdio: 'inherit' });
  }
};

// Help text
const showHelp = () => {
  console.log(`
Linguify Dev Tools

Usage: npm run dev-tools <command> [args]

Commands:
  component <name> [location]  - Create a new component
  hook <name>                  - Create a new hook
  api <name>                   - Create a new API module
  page <name> [route]          - Create a new page
  addon <name>                 - Create a new addon module
  analyze                      - Analyze bundle size
  perf                         - Run performance tests

Examples:
  npm run dev-tools component Button
  npm run dev-tools hook useAuth
  npm run dev-tools api User
  npm run dev-tools page Dashboard
  npm run dev-tools addon vocabulary
`);
};

// Execute command
if (!command || command === 'help') {
  showHelp();
} else if (commands[command]) {
  const cmdArgs = args.slice(1);
  commands[command](...cmdArgs);
} else {
  console.error(`Unknown command: ${command}`);
  showHelp();
}