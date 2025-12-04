# Fintech Theme Documentation

## Overview

This document provides comprehensive documentation for the AI Receipt Tracker's consolidated CSS theme system. The theme implements a calming, nature-inspired aesthetic using the Wildflowers color scheme with flat design principles and clear borderlines. The soft green and purple tones reduce eye strain while maintaining professional appeal.

## File Structure

```
src/assets/
├── fintech-theme.css    # Main consolidated theme file
├── main.css            # Entry point that imports theme
└── THEME_DOCUMENTATION.md  # This file
```

## Color Palette

### Primary Colors

| Color Name | Hex Code | Usage | Example |
|------------|----------|-------|---------|
| **Forest Green** | `#519755` | Primary actions, borders, headers | Buttons, borders, nav items, headers |
| **Celadon Green** | `#A8DCAB` | Soft backgrounds, highlights, hover | Backgrounds, active nav, hover states |
| **Dusty Rose** | `#DBAAA7` | Secondary elements, accents | Secondary buttons, accents, warnings |
| **Orchid Purple** | `#BE91BE` | Tertiary actions, info elements | Info badges, tertiary buttons |

### Supporting Colors

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Dark Forest | `#3D7A42` | Hover state for forest green |
| Dark Celadon | `#8BC690` | Darker celadon for emphasis |
| Dark Rose | `#C98E8B` | Hover/error state for dusty rose |
| Dark Purple | `#A677A6` | Hover state for orchid purple |
| Background Alt | `#E8F4EA` | Slightly darker mint for contrast |

### Text Colors

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Text Primary | `#2D3E2F` | Main body text, headings (dark forest) |
| Text Secondary | `#5A6B5C` | Supporting text, labels (medium green-gray) |
| Text Muted | `#8A9B8C` | Disabled text, hints (light green-gray) |
| White | `#FFFFFF` | Text on dark backgrounds |

### State Colors

| State | Hex Code | Usage |
|-------|----------|-------|
| Success | `#519755` | Successful operations, processed status (forest green) |
| Warning | `#DBAAA7` | Warnings, pending status (dusty rose) |
| Error | `#C98E8B` | Errors, failed operations (darker rose) |
| Info | `#BE91BE` | Informational messages (orchid purple) |

### Navigation Colors

| Element | Hex Code | Usage |
|---------|----------|-------|
| Nav Background | `#2D3E2F` | Sidebar background (dark forest) |
| Nav Text | `#F5FAF6` | Navigation item text (light mint) |
| Nav Hover | `#A8DCAB` | Navigation hover state (celadon) |
| Nav Border | `#519755` | Navigation borders (forest green) |
| Nav Active | `#A8DCAB` | Active navigation item (celadon) |

## Layout System

### Sidebar Navigation

The application uses a fixed left sidebar navigation system:

- **Width**: 240px (desktop), full width when open (mobile)
- **Position**: Fixed left
- **Background**: Dark forest green (`#2D3E2F`)
- **Border**: 2px solid forest green

#### Sidebar Structure

```html
<div class="sidebar">
  <div class="sidebar-header">
    <a href="/" class="sidebar-logo">App Name</a>
  </div>
  <nav class="sidebar-nav">
    <div class="nav-section">
      <div class="nav-section-title">Section Title</div>
      <a href="/page" class="nav-item">
        <span class="nav-item-icon">🏠</span>
        Page Name
      </a>
    </div>
  </nav>
</div>
```

### Main Content Area

Content is offset by the sidebar width and contains:

- **Content Header**: Sticky header with page title
- **Content Body**: Main content area with max-width constraint (1200px)

```html
<div class="main-content">
  <div class="content-header">
    <h1>Page Title</h1>
  </div>
  <div class="content-body">
    <!-- Your content here -->
  </div>
</div>
```

## Component Usage Guide

### Cards

Cards are the primary content containers with clear borders:

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <p class="card-subtitle">Optional subtitle</p>
  </div>
  <div class="card-body">
    <!-- Card content -->
  </div>
  <div class="card-footer">
    <!-- Optional footer -->
  </div>
</div>
```

**Properties:**
- Background: White
- Border: 2px solid forest green (#519755)
- Padding: 24px
- Border radius: 4px

### Forms

Form components with consistent styling:

```html
<div class="form-group">
  <label class="form-label" for="input-id">Label</label>
  <input type="text" id="input-id" class="form-input" placeholder="Placeholder">
  <span class="form-hint">Helper text</span>
  <span class="form-error">Error message (if needed)</span>
</div>
```

**Available Form Classes:**
- `.form-group` - Container for form field
- `.form-label` - Label styling
- `.form-input` - Text input
- `.form-select` - Select dropdown
- `.form-textarea` - Textarea
- `.form-hint` - Helper text
- `.form-error` - Error message

### Buttons

Six button variants with consistent styling:

```html
<!-- Primary (Forest Green) -->
<button class="btn btn-primary">Primary Action</button>

<!-- Secondary (Celadon Green) -->
<button class="btn btn-secondary">Secondary Action</button>

<!-- Accent (Dusty Rose) -->
<button class="btn btn-accent">Accent Action</button>

<!-- Outline -->
<button class="btn btn-outline">Outline Button</button>

<!-- Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary btn-lg">Large</button>

<!-- Full width -->
<button class="btn btn-primary btn-block">Full Width</button>
```

**Properties:**
- Border: 2px solid
- Padding: 16px 24px
- Font weight: Semibold (600)
- Transition: 0.15s ease

### Tables

Data tables with alternating row hover effects:

```html
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>Column 1</th>
        <th>Column 2</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Data 1</td>
        <td>Data 2</td>
      </tr>
    </tbody>
  </table>
</div>
```

### Badges

Status indicators with four states:

```html
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-error">Error</span>
<span class="badge badge-info">Info</span>
```

### Alerts

Notification messages:

```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-warning">Warning message</div>
<div class="alert alert-error">Error message</div>
<div class="alert alert-info">Info message</div>
```

## CSS Custom Properties (Variables)

All theme values are defined as CSS custom properties for easy maintenance:

```css
/* Example usage in components */
.my-component {
  background-color: var(--color-primary);
  padding: var(--spacing-lg);
  border: var(--border-width) solid var(--color-border);
  font-size: var(--font-size-base);
}
```

### Variable Categories

1. **Colors**: `--color-*`
2. **Spacing**: `--spacing-*`
3. **Typography**: `--font-*`
4. **Layout**: `--sidebar-width`, `--header-height`
5. **Transitions**: `--transition-*`

## Spacing System

Uses an 8px base scale:

| Class | Value | Pixels |
|-------|-------|--------|
| `xs` | `--spacing-xs` | 4px |
| `sm` | `--spacing-sm` | 8px |
| `md` | `--spacing-md` | 16px |
| `lg` | `--spacing-lg` | 24px |
| `xl` | `--spacing-xl` | 32px |
| `xxl` | `--spacing-xxl` | 48px |

## Utility Classes

### Spacing Utilities

```html
<!-- Margin -->
<div class="mt-3">Margin top (16px)</div>
<div class="mb-4">Margin bottom (24px)</div>

<!-- Padding -->
<div class="p-3">Padding (16px)</div>
```

Available: `m-0`, `mt-1` through `mt-5`, `mb-1` through `mb-5`, `p-0` through `p-5`

### Display Utilities

```html
<div class="d-flex justify-between align-center gap-3">
  <span>Item 1</span>
  <span>Item 2</span>
</div>
```

Classes:
- Display: `d-block`, `d-inline`, `d-inline-block`, `d-flex`, `d-none`
- Flex: `flex-row`, `flex-column`
- Justify: `justify-start`, `justify-center`, `justify-end`, `justify-between`
- Align: `align-start`, `align-center`, `align-end`
- Gap: `gap-1` through `gap-4`

### Border Utilities

```html
<div class="border border-radius">Bordered element</div>
```

Classes: `border`, `border-top`, `border-bottom`, `border-radius`

### Background Utilities

```html
<div class="bg-primary">Primary background</div>
```

Classes: `bg-white`, `bg-primary`, `bg-secondary`, `bg-accent`

## Responsive Design

### Breakpoints

- **Desktop**: > 768px (full sidebar)
- **Mobile**: ≤ 768px (hidden sidebar)

### Mobile Behavior

On mobile devices:
- Sidebar is hidden by default
- Main content takes full width
- Reduced padding in content areas
- Mobile menu toggle can be implemented with `.sidebar.mobile-open`

```css
@media (max-width: 768px) {
  /* Sidebar hidden by default */
  .sidebar {
    transform: translateX(-100%);
  }
  
  /* Show sidebar when toggled */
  .sidebar.mobile-open {
    transform: translateX(0);
  }
}
```

## Accessibility

### Focus States

All interactive elements have visible focus indicators:

```css
*:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

### Screen Reader Support

Use the `.sr-only` class for screen-reader-only text:

```html
<button>
  <span class="sr-only">Close dialog</span>
  <span aria-hidden="true">×</span>
</button>
```

## Best Practices

### 1. Use CSS Variables

Always use CSS custom properties instead of hardcoded values:

```css
/* ✅ Good */
.component {
  color: var(--color-primary);
  padding: var(--spacing-md);
}

/* ❌ Bad */
.component {
  color: #519755;
  padding: 16px;
}
```

### 2. Use Utility Classes

Prefer utility classes for common patterns:

```html
<!-- ✅ Good -->
<div class="d-flex justify-between mb-3">

<!-- ❌ Bad (custom styles) -->
<div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
```

### 3. Component Composition

Build complex components by combining theme classes:

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Transaction Details</h3>
  </div>
  <div class="card-body">
    <div class="d-flex justify-between align-center mb-3">
      <span class="text-secondary">Vendor:</span>
      <span class="text-bold">Coffee Shop</span>
    </div>
    <div class="d-flex justify-between align-center">
      <span class="text-secondary">Amount:</span>
      <span class="text-bold">$4.50</span>
    </div>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary btn-block">View Details</button>
  </div>
</div>
```

### 4. Consistent Borders

All borders use the same width (2px) for consistency:

```css
/* Border width is standardized */
border: var(--border-width) solid var(--color-border);
```

### 5. Flat Design Principles

- No gradients or shadows (minimal shadows only where needed)
- Clear, solid borders
- Flat colors
- High contrast

## Migration Guide

To migrate existing components to the new theme:

1. **Remove inline styles**: Convert to utility classes
2. **Replace hardcoded colors**: Use CSS variables
3. **Apply component classes**: Use `.card`, `.btn`, etc.
4. **Update layouts**: Wrap content in `.main-content` and `.content-body`
5. **Test responsiveness**: Ensure mobile behavior is correct

### Example Migration

**Before:**
```vue
<style scoped>
.container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
}
</style>
```

**After:**
```vue
<template>
  <div class="content-body">
    <div class="card" style="max-width: 400px; margin: 0 auto;">
      <!-- Content -->
    </div>
  </div>
</template>
```

## Customization

To customize the theme, modify variables in `fintech-theme.css`:

```css
:root {
  /* Change primary color */
  --color-primary: #519755; /* Your custom forest green */
  
  /* Change spacing scale */
  --spacing-base: 16px;
  
  /* Change sidebar width */
  --sidebar-width: 280px;
}
```

## Support

For questions or issues with the theme system:
1. Check this documentation
2. Review `fintech-theme.css` for implementation details
3. Ensure you're importing the theme in `main.css`
4. Test in browser DevTools to debug CSS variable values

## Version History

- **v1.0.0** (December 2025): Initial release with Wildflowers theme (calming greens & purples)
  - Side navigation layout
  - Comprehensive component library
  - Flat design with clear borders
  - Full responsive support
  - Accessibility features
