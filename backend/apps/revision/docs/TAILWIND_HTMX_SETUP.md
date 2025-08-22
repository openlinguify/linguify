# Tailwind CSS + HTMX Integration for Django Flashcard App

This document describes the complete setup and integration of Tailwind CSS and HTMX for the Linguify revision app, providing modern, interactive flashcard components.

## Overview

The integration includes:
- **Tailwind CSS** for utility-first styling with custom components
- **HTMX** for dynamic interactions without complex JavaScript
- **Custom flashcard components** optimized for educational apps
- **Responsive design** that works on mobile and desktop
- **Spaced repetition UI patterns** for effective learning

## Files Added/Modified

### Configuration Files
- `/tailwind.config.js` - Tailwind configuration with custom theme
- `/package.json` - NPM dependencies and build scripts
- `/build-tailwind.js` - Custom build script for compilation

### Templates
- `/backend/apps/revision/templates/revision/base.html` - Updated base template with HTMX and Tailwind
- `/backend/apps/revision/templates/revision/flashcard_examples.html` - Demo page showcasing all components

### Styles
- `/backend/apps/revision/static/revision/css/tailwind-components.css` - Custom component styles
- `/backend/apps/revision/static/revision/css/tailwind.css` - Tailwind input file (for future compilation)

### Python Views
- `/backend/apps/revision/views/htmx_views.py` - HTMX endpoint handlers for demo functionality
- `/backend/apps/revision/urls_htmx.py` - URL configuration for HTMX endpoints

## Features Implemented

### 1. Flashcard Components

#### Basic Flip Card
```html
<div class="flashcard" onclick="this.classList.toggle('flipped')">
    <div class="flashcard-inner">
        <div class="flashcard-front">
            <h3>Question content</h3>
        </div>
        <div class="flashcard-back">
            <h3>Answer content</h3>
        </div>
    </div>
</div>
```

#### Interactive Deck Cards
```html
<div class="deck-card" 
     hx-get="/revision/htmx/api/cards/sample/1/" 
     hx-target="#detail-modal" 
     hx-trigger="click">
    <h3>Deck Title</h3>
    <p>Progress indicators and metadata</p>
</div>
```

### 2. Study Mode Selection
Dynamic loading of different study interfaces:
- Flashcards (traditional spaced repetition)
- Quiz mode (multiple choice)
- Matching game (drag & drop associations)
- Writing practice (type-to-answer)

### 3. Interactive Forms
Real-time form validation and preview:
```html
<form hx-post="/revision/htmx/api/cards/create/" 
      hx-target="#feedback" 
      hx-swap="innerHTML">
    <textarea hx-get="/revision/htmx/api/cards/preview/" 
              hx-target="#preview" 
              hx-trigger="keyup changed delay:500ms"></textarea>
</form>
```

### 4. Search and Filtering
Instant search results with HTMX:
```html
<input type="text" 
       hx-get="/revision/htmx/api/cards/search/"
       hx-target="#results"
       hx-trigger="keyup changed delay:300ms">
```

## Custom Tailwind Classes

### Layout Classes
- `.flashcard` - 3D flippable card container
- `.flashcard-inner` - Inner transform container
- `.flashcard-front` / `.flashcard-back` - Card faces
- `.study-mode-card` - Study mode selection cards
- `.deck-card` - Deck preview cards

### Interactive Classes
- `.btn-linguify` - Primary button style
- `.btn-linguify-outline` - Outlined button style
- `.btn-linguify-accent` - Accent color button
- `.form-input` / `.form-textarea` - Form elements
- `.tag-primary` / `.tag-accent` - Tag components

### Progress Indicators
- `.progress-ring` - Circular progress indicator
- `.loading-spinner` - Loading animation
- `.skeleton` - Skeleton loading state

## HTMX Integration

### Configuration
HTMX is configured in the base template with:
- Global view transitions enabled
- CSRF token automatic inclusion
- Error handling and loading states
- Custom event listeners for better UX

### Patterns Used

#### 1. Dynamic Content Loading
```html
<div hx-get="/api/endpoint/" 
     hx-target="#container" 
     hx-trigger="click">
```

#### 2. Form Submissions
```html
<form hx-post="/api/submit/" 
      hx-target="#feedback" 
      hx-swap="innerHTML">
```

#### 3. Live Search
```html
<input hx-get="/api/search/" 
       hx-target="#results" 
       hx-trigger="keyup changed delay:300ms">
```

#### 4. Indicators and Loading States
```html
<div class="htmx-indicator loading-spinner"></div>
```

## Responsive Design

The components are built mobile-first with breakpoints:
- Mobile: Single column, touch-optimized
- Tablet: 2-column grids, medium spacing
- Desktop: 3-4 column grids, hover effects
- Large screens: Optimized layouts with more content

## Color Scheme

The design uses the existing Linguify color palette:
- **Primary**: `#2D5BBA` (Linguify blue)
- **Primary Dark**: `#1E3A8A` (Darker blue for hovers)
- **Secondary**: `#8B5CF6` (Purple accent)
- **Accent**: `#00D4AA` (Teal/green accent)
- **Success**: `#10b981` (Green for positive actions)
- **Warning**: `#f59e0b` (Orange for warnings)
- **Danger**: `#ef4444` (Red for errors)

## Usage Examples

### 1. Accessing the Demo Page
Visit: `/revision/htmx/examples/` to see all components in action.

### 2. Adding New Flashcard Components
1. Add HTML structure with Tailwind classes
2. Include HTMX attributes for interactivity
3. Create corresponding Django view for dynamic content
4. Add URL pattern to `urls_htmx.py`

### 3. Customizing Styles
Edit `/backend/apps/revision/static/revision/css/tailwind-components.css` to modify component styles while maintaining consistency with the design system.

## Development Workflow

### 1. Starting Development
```bash
# Watch for Tailwind changes (when using compiled version)
npm run watch:tailwind

# Or start development server normally (using CDN version)
python manage.py runserver
```

### 2. Building for Production
```bash
# Build optimized Tailwind CSS
npm run build:tailwind:prod

# Update template to use compiled CSS instead of CDN
```

### 3. Adding New Components
1. Design component with Tailwind utilities
2. Add custom CSS to `tailwind-components.css` if needed
3. Create HTMX interactions in templates
4. Add Django views for dynamic behavior
5. Test responsiveness and accessibility

## Best Practices

### 1. Performance
- Use CSS components for repeated patterns
- Minimize HTMX requests with proper debouncing
- Implement loading states for better UX
- Optimize images and icons

### 2. Accessibility
- Include proper ARIA labels
- Ensure keyboard navigation works
- Use semantic HTML elements
- Test with screen readers

### 3. Mobile Optimization
- Touch targets are at least 44px
- Swipe gestures for card interactions
- Optimized layouts for small screens
- Fast loading on mobile networks

### 4. Code Organization
- Keep HTMX logic in templates
- Use Django views for data processing
- Organize CSS components logically
- Document complex interactions

## Future Enhancements

### 1. Advanced Animations
- Smooth transitions between study modes
- Card shuffle animations
- Progress celebrations
- Gesture-based interactions

### 2. Progressive Web App Features
- Offline flashcard study
- Push notifications for study reminders
- Background sync for progress
- App-like installation

### 3. Advanced HTMX Patterns
- WebSocket integration for real-time features
- Advanced form validation
- Drag and drop interfaces
- Multi-step wizards

## Troubleshooting

### Common Issues

1. **Tailwind styles not applying**
   - Check CDN is loaded
   - Verify custom component CSS is included
   - Clear browser cache

2. **HTMX requests failing**
   - Check CSRF token configuration
   - Verify URL patterns match
   - Check Django logs for errors

3. **Mobile layout issues**
   - Test on actual devices
   - Use browser dev tools mobile simulation
   - Check viewport meta tag

### Debug Tools
- Browser developer tools for CSS debugging
- HTMX debugging extension for Chrome/Firefox
- Django debug toolbar for backend issues

## Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [HTMX Documentation](https://htmx.org/docs/)
- [Django Static Files](https://docs.djangoproject.com/en/stable/howto/static-files/)
- [Educational UI Patterns](https://ui-patterns.com/patterns/category/education)

---

This integration provides a solid foundation for building modern, interactive educational applications with Django, combining the power of utility-first CSS with seamless HTMX interactions.