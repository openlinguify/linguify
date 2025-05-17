// Debug script for webpack issues
const fs = require('fs');
const path = require('path');

// Check for potential issues
console.log('🔍 Debugging Webpack Issues...\n');

// 1. Check node_modules integrity
const nodeModulesPath = path.join(process.cwd(), 'node_modules');
if (!fs.existsSync(nodeModulesPath)) {
  console.error('❌ node_modules directory not found!');
  console.log('Run: npm install');
  process.exit(1);
}

// 2. Check for duplicate React versions
const checkDuplicateReact = () => {
  const reactPaths = [];
  
  function findReact(dir) {
    if (path.basename(dir) === 'react' && dir.includes('node_modules')) {
      reactPaths.push(dir);
    }
    
    try {
      const files = fs.readdirSync(dir);
      files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        if (stat.isDirectory() && !file.startsWith('.')) {
          findReact(filePath);
        }
      });
    } catch (e) {
      // Ignore permission errors
    }
  }
  
  findReact(nodeModulesPath);
  
  if (reactPaths.length > 1) {
    console.warn('⚠️  Multiple React versions found:');
    reactPaths.forEach(p => console.log(`   - ${p}`));
    console.log('\nThis might cause issues. Run: npm dedupe');
  }
};

// 3. Check for .next directory issues
const nextDir = path.join(process.cwd(), '.next');
if (fs.existsSync(nextDir)) {
  console.log('ℹ️  .next directory exists. Consider cleaning:');
  console.log('   rm -rf .next');
  console.log('   npm run dev');
}

// 4. Check Next.js version compatibility
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const nextVersion = packageJson.dependencies.next;
console.log(`\n📦 Next.js version: ${nextVersion}`);

// 5. Suggest fixes
console.log('\n🔧 Suggested fixes:');
console.log('1. Clear cache and reinstall:');
console.log('   rm -rf .next node_modules');
console.log('   npm install');
console.log('   npm run dev');
console.log('\n2. Use minimal config:');
console.log('   mv next.config.ts next.config.backup.ts');
console.log('   cp next.config.minimal.ts next.config.ts');
console.log('   npm run dev');
console.log('\n3. Check for circular dependencies:');
console.log('   npm ls');

checkDuplicateReact();