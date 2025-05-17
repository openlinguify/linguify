# Frontend NPM Commands Documentation

This documentation covers all available npm commands for the Linguify frontend application using the minimal Next.js configuration.

## Available Commands

### Development Commands

#### `npm run dev`
Starts the development server in normal mode.
- **Usage**: `npm run dev`
- **Default Port**: 3000
- **Features**: Hot reloading, development mode optimizations

#### `npm run dev:turbo`
Starts the development server with Turbo mode enabled for faster compilation.
- **Usage**: `npm run dev:turbo`
- **Features**: Experimental faster compilation using Rust-based bundler

#### `npm run dev:all`
Runs both frontend and backend servers concurrently.
- **Usage**: `npm run dev:all`
- **Requirements**: Backend must be properly configured
- **Features**: Starts Django backend on port 8000 and Next.js frontend on port 3000

#### `npm run dev-tools`
Runs the development tools utility for rapid development and code generation.
- **Usage**: `npm run dev-tools <command> [args]`
- **Location**: `scripts/dev-tools.js`

##### Dev Tools Commands:

###### Component Generation
```bash
npm run dev-tools component <name> [location]
```
- Creates a new React component with TypeScript interface
- Default location: `src/components`
- Example: `npm run dev-tools component Button` creates `src/components/Button/Button.tsx`

###### Hook Generation
```bash
npm run dev-tools hook <name>
```
- Creates a new custom React hook
- Location: `src/hooks`
- Example: `npm run dev-tools hook useAuth` creates `src/hooks/useAuth.ts`

###### API Module Generation
```bash
npm run dev-tools api <name>
```
- Creates a new API module with CRUD operations
- Location: `src/api`
- Example: `npm run dev-tools api User` creates `src/api/UserAPI.ts`

###### Page Generation
```bash
npm run dev-tools page <name> [route]
```
- Creates a new Next.js page component
- Location: `src/app/[route]/page.tsx`
- Example: `npm run dev-tools page Dashboard` creates `src/app/dashboard/page.tsx`

###### Addon Module Generation
```bash
npm run dev-tools addon <name>
```
- Creates a complete addon module structure
- Creates folders: `api`, `components`, `hooks`, `types`
- Example: `npm run dev-tools addon vocabulary`

###### Bundle Analysis
```bash
npm run dev-tools analyze
```
- Analyzes bundle size with webpack-bundle-analyzer
- Equivalent to `npm run analyze`

###### Performance Testing
```bash
npm run dev-tools perf
```
- Runs performance tests after building
- Starts production server for testing

###### Help
```bash
npm run dev-tools help
```
- Shows all available dev-tools commands

### Build Commands

#### `npm run build`
Creates an optimized production build.
- **Usage**: `npm run build`
- **Output**: `.next/` directory with production-ready files

#### `npm run analyze`
Builds the application with bundle analysis.
- **Usage**: `npm run analyze`
- **Features**: Opens bundle analyzer to visualize bundle sizes

### Production Commands

#### `npm run start`
Starts the production server after building.
- **Usage**: `npm run start`
- **Requirements**: Must run `npm run build` first
- **Port**: 3000 (by default)

### Code Quality Commands

#### `npm run lint`
Runs ESLint to check code quality and style.
- **Usage**: `npm run lint`
- **Config**: Uses Next.js lint configuration

#### `npm run type-check`
Runs TypeScript compiler to check types without emitting files.
- **Usage**: `npm run type-check`
- **Features**: Validates TypeScript types across the project

### Performance Commands

#### `npm run perf:check`
Runs Lighthouse to check performance metrics.
- **Usage**: `npm run perf:check`
- **Requirements**: Development server must be running
- **Features**: Opens Lighthouse report in browser

### Maintenance Commands

#### `npm run clean`
Removes build artifacts and dependencies.
- **Usage**: `npm run clean`
- **Removes**: `.next/` directory and `node_modules/`

#### `npm run debug:webpack`
Runs webpack debugging script.
- **Usage**: `npm run debug:webpack`
- **Location**: `scripts/debug-webpack.js`

#### `npm run fix:webpack`
Attempts to fix webpack issues by clearing cache.
- **Usage**: `npm run fix:webpack`
- **Actions**: Removes `.next/` directory and restarts development server

## Configuration Details

The minimal configuration (`next.config.minimal.ts`) includes:

1. **CORS Headers**: Configured for authentication API routes
   - Allows credentials
   - Accepts all origins (*)
   - Supports various HTTP methods

2. **API Rewrites**: Proxies API calls to the backend
   - Routes `/api/*` to `http://localhost:8000/api/*`

## Best Practices

1. **Development**: Use `npm run dev:all` for full-stack development
2. **Production Build**: Always run `npm run build` before `npm run start`
3. **Type Safety**: Run `npm run type-check` before commits
4. **Code Quality**: Use `npm run lint` to maintain code standards
5. **Performance**: Periodically run `npm run perf:check` to monitor performance

## Quick Reference Table

| Command | Description | Example |
|---------|-------------|---------|
| `npm run dev` | Start development server | `npm run dev` |
| `npm run dev:turbo` | Start with Turbo mode | `npm run dev:turbo` |
| `npm run dev:all` | Start frontend + backend | `npm run dev:all` |
| `npm run build` | Build for production | `npm run build` |
| `npm run start` | Start production server | `npm run start` |
| `npm run lint` | Run ESLint | `npm run lint` |
| `npm run type-check` | Check TypeScript types | `npm run type-check` |
| `npm run analyze` | Analyze bundle size | `npm run analyze` |
| `npm run clean` | Clean build & deps | `npm run clean` |
| `npm run perf:check` | Monitor performance | `npm run perf:check` |
| **Dev Tools** | | |
| `npm run dev-tools component` | Create component | `npm run dev-tools component Button` |
| `npm run dev-tools hook` | Create hook | `npm run dev-tools hook useAuth` |
| `npm run dev-tools api` | Create API module | `npm run dev-tools api User` |
| `npm run dev-tools page` | Create page | `npm run dev-tools page Dashboard` |
| `npm run dev-tools addon` | Create addon | `npm run dev-tools addon vocabulary` |

## Troubleshooting

- If webpack issues occur, try `npm run fix:webpack`
- For bundle size issues, use `npm run analyze`
- For clean installation, use `npm run clean` followed by `npm install`