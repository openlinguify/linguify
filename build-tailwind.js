const fs = require('fs');
const path = require('path');

// Global Tailwind CSS build script for entire Linguify platform
async function buildTailwind() {
  try {
    const { exec } = require('child_process');
    const util = require('util');
    const execPromise = util.promisify(exec);

    console.log('🎨 Building Tailwind CSS for Linguify Platform...');
    
    // Global input and output paths
    const inputPath = './backend/static/css/tailwind-global.css';
    const outputPath = './backend/static/css/tailwind-built.css';
    const outputPathStatic = './backend/staticfiles/css/tailwind-built.css';
    
    // Create input file if it doesn't exist
    if (!fs.existsSync(inputPath)) {
      const inputDir = path.dirname(inputPath);
      if (!fs.existsSync(inputDir)) {
        fs.mkdirSync(inputDir, { recursive: true });
        console.log(`📁 Created directory: ${inputDir}`);
      }
      
      // Create base Tailwind CSS file
      const baseCSS = `@tailwind base;
@tailwind components; 
@tailwind utilities;

/* Linguify Custom Components */
@layer components {
  /* App Cards */
  .app-card-linguify {
    @apply bg-white border border-gray-200 rounded-2xl p-6 transition-all duration-300 hover:shadow-linguify hover:border-linguify-primary/20 cursor-pointer;
  }
  
  .app-card-linguify:hover {
    @apply transform -translate-y-1;
  }
  
  /* Buttons */
  .btn-linguify {
    @apply bg-linguify-primary hover:bg-linguify-primary-dark text-white font-medium px-6 py-3 rounded-lg transition-colors duration-200 inline-flex items-center justify-center;
  }
  
  .btn-linguify-outline {
    @apply border-2 border-linguify-primary text-linguify-primary hover:bg-linguify-primary hover:text-white font-medium px-6 py-3 rounded-lg transition-all duration-200 inline-flex items-center justify-center;
  }
  
  .btn-linguify-accent {
    @apply bg-linguify-accent hover:bg-linguify-accent/90 text-white font-medium px-6 py-3 rounded-lg transition-colors duration-200 inline-flex items-center justify-center;
  }
  
  /* Form Elements */
  .input-linguify {
    @apply w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linguify-primary/20 focus:border-linguify-primary transition-colors duration-200;
  }
  
  .textarea-linguify {
    @apply w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linguify-primary/20 focus:border-linguify-primary transition-colors duration-200 resize-none;
  }
  
  /* Cards & Containers */
  .card-linguify {
    @apply bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300;
  }
  
  .container-linguify {
    @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
  }
  
  /* Navigation */
  .nav-linguify {
    @apply bg-white/95 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50;
  }
  
  .nav-link-linguify {
    @apply text-gray-600 hover:text-linguify-primary px-3 py-2 text-sm font-medium transition-colors duration-200;
  }
  
  .nav-link-linguify.active {
    @apply text-linguify-primary bg-linguify-primary/5 rounded-md;
  }
  
  /* Flashcard Components */
  .flashcard-3d {
    @apply relative w-full h-64 perspective-1000 cursor-pointer;
  }
  
  .flashcard-inner {
    @apply relative w-full h-full transition-transform duration-600 transform-style-3d;
  }
  
  .flashcard-front,
  .flashcard-back {
    @apply absolute inset-0 w-full h-full backface-hidden rounded-xl border border-gray-200 bg-white flex items-center justify-center p-6 text-center;
  }
  
  .flashcard-back {
    @apply rotate-y-180 bg-linguify-primary/5;
  }
  
  .flashcard-3d.flipped .flashcard-inner {
    @apply rotate-y-180;
  }
  
  /* Progress Components */
  .progress-linguify {
    @apply bg-gray-200 rounded-full h-2 overflow-hidden;
  }
  
  .progress-bar-linguify {
    @apply bg-gradient-to-r from-linguify-primary to-linguify-accent h-full transition-all duration-300;
  }
  
  /* Study Mode Cards */
  .study-mode-card {
    @apply bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-linguify-primary hover:shadow-lg transition-all duration-300 cursor-pointer;
  }
  
  .study-mode-card.active {
    @apply border-linguify-primary bg-linguify-primary/5;
  }
  
  /* Loading States */
  .skeleton-linguify {
    @apply bg-gray-200 rounded animate-pulse;
  }
  
  .spinner-linguify {
    @apply animate-spin rounded-full border-2 border-gray-200 border-t-linguify-primary;
  }
  
  /* Notifications */
  .notification-linguify {
    @apply fixed top-4 right-4 max-w-sm bg-white border border-gray-200 rounded-lg p-4 shadow-lg z-50 animate-slide-in;
  }
  
  .notification-success {
    @apply border-l-4 border-l-linguify-success;
  }
  
  .notification-error {
    @apply border-l-4 border-l-linguify-danger;
  }
  
  .notification-warning {
    @apply border-l-4 border-l-linguify-warning;
  }
}

/* Custom utilities */
@layer utilities {
  .perspective-1000 {
    perspective: 1000px;
  }
  
  .transform-style-3d {
    transform-style: preserve-3d;
  }
  
  .backface-hidden {
    backface-visibility: hidden;
  }
  
  .rotate-y-180 {
    transform: rotateY(180deg);
  }
  
  /* Text utilities */
  .text-linguify-gradient {
    @apply bg-gradient-to-r from-linguify-primary to-linguify-accent bg-clip-text text-transparent;
  }
  
  /* Background utilities */
  .bg-linguify-gradient {
    @apply bg-gradient-to-r from-linguify-primary to-linguify-accent;
  }
  
  .bg-linguify-light-gradient {
    @apply bg-gradient-to-br from-linguify-light to-white;
  }
}
`;
      
      fs.writeFileSync(inputPath, baseCSS);
      console.log(`📝 Created Tailwind input file: ${inputPath}`);
    }
    
    // Ensure output directories exist
    const outputDir = path.dirname(outputPath);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
      console.log(`📁 Created directory: ${outputDir}`);
    }
    
    const outputDirStatic = path.dirname(outputPathStatic);
    if (!fs.existsSync(outputDirStatic)) {
      fs.mkdirSync(outputDirStatic, { recursive: true });
      console.log(`📁 Created directory: ${outputDirStatic}`);
    }
    
    // Build command
    const isProduction = process.env.NODE_ENV === 'production';
    const watchFlag = process.argv.includes('--watch');
    const command = `npx tailwindcss -i ${inputPath} -o ${outputPath} ${isProduction ? '--minify' : ''} ${watchFlag ? '--watch' : ''}`;
    
    console.log(`📦 Running: ${command}`);
    
    if (watchFlag) {
      console.log('👀 Watching for changes across all Linguify apps...');
      const child = exec(command);
      
      child.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          console.log(`🎨 ${output}`);
          
          // Copy to staticfiles for immediate use
          if (fs.existsSync(outputPath)) {
            fs.copyFileSync(outputPath, outputPathStatic);
            console.log('📋 Copied to staticfiles directory');
          }
        }
      });
      
      child.stderr.on('data', (data) => {
        console.error(`❌ ${data.toString().trim()}`);
      });
      
      child.on('close', (code) => {
        console.log(`🏁 Build process exited with code ${code}`);
      });
      
      // Keep process alive
      process.stdin.resume();
    } else {
      const { stdout, stderr } = await execPromise(command);
      if (stdout) console.log(`📤 ${stdout}`);
      if (stderr) console.error(`❌ ${stderr}`);
      
      // Copy to staticfiles
      if (fs.existsSync(outputPath)) {
        fs.copyFileSync(outputPath, outputPathStatic);
        console.log('📋 Copied to staticfiles directory');
      }
      
      console.log('✅ Tailwind CSS build complete for entire Linguify platform!');
      console.log(`📁 Output: ${outputPath}`);
      console.log(`📁 Static: ${outputPathStatic}`);
    }
    
  } catch (error) {
    console.error('❌ Build failed:', error.message);
    process.exit(1);
  }
}

buildTailwind();