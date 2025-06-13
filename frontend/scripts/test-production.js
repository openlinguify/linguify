#!/usr/bin/env node

/**
 * Script to test production behavior locally
 * Usage: node scripts/test-production.js
 */

const { spawn } = require('child_process');
const chalk = require('chalk');

console.log(chalk.blue('🚀 Starting production test environment...'));

// Set production environment variables
const env = {
  ...process.env,
  NODE_ENV: 'production',
  NEXT_PUBLIC_APP_URL: 'https://www.openlinguify.com',
  // Add other production env vars here
};

// First build the app
console.log(chalk.yellow('📦 Building application...'));
const build = spawn('npm', ['run', 'build'], { 
  env, 
  stdio: 'inherit',
  shell: true 
});

build.on('close', (code) => {
  if (code !== 0) {
    console.error(chalk.red('❌ Build failed'));
    process.exit(1);
  }

  console.log(chalk.green('✅ Build successful'));
  console.log(chalk.yellow('🌐 Starting production server...'));

  // Then start the production server
  const start = spawn('npm', ['run', 'start'], { 
    env, 
    stdio: 'inherit',
    shell: true 
  });

  start.on('close', (code) => {
    console.log(chalk.blue('👋 Production server stopped'));
  });
});

// Handle Ctrl+C
process.on('SIGINT', () => {
  console.log(chalk.yellow('\n👋 Shutting down...'));
  process.exit(0);
});