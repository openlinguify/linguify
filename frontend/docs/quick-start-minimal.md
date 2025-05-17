# Quick Start Guide - Minimal Configuration

Quick reference for running Linguify frontend with minimal Next.js configuration.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy minimal config (if needed):
   ```bash
   cp next.config.minimal.ts next.config.ts
   ```

## Common Commands

```bash
# Development
npm run dev              # Start frontend only
npm run dev:all          # Start frontend + backend
npm run dev:turbo        # Start with Turbo mode

# Build & Production
npm run build            # Build for production
npm run start            # Start production server

# Code Quality
npm run lint             # Check code style
npm run type-check       # Check TypeScript types

# Maintenance
npm run clean            # Clean build & deps
npm run fix:webpack      # Fix webpack issues
```

## Minimal Config Features

The minimal configuration provides:
- ✅ CORS headers for authentication
- ✅ API proxy to backend (port 8000)
- ❌ No experimental features
- ❌ No custom webpack config
- ❌ No performance optimizations

## Environment Variables

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Typical Workflow

1. Start development:
   ```bash
   npm run dev:all
   ```

2. Make changes and test

3. Check types:
   ```bash
   npm run type-check
   ```

4. Build for production:
   ```bash
   npm run build
   npm run start
   ```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Webpack errors | `npm run fix:webpack` |
| Type errors | `npm run type-check` |
| Build issues | `npm run clean && npm install` |
| API connection | Check backend is running on :8000 |