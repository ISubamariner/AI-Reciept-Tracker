# Quick Reference Card - Wildflowers Fintech Theme

## 🎨 Colors (CSS Variables)

```css
/* Primary Colors */
--color-primary: #519755;        /* Forest green - buttons, borders */
--color-secondary: #A8DCAB;      /* Celadon - backgrounds, highlights */
--color-accent: #DBAAA7;         /* Dusty rose - accents, warnings */
--color-tertiary: #BE91BE;       /* Orchid purple - info, tertiary */
--color-background: #F5FAF6;     /* Light mint - main background */

/* Text Colors */
--color-text-primary: #2D3E2F;   /* Dark forest - body text */
--color-text-secondary: #5A6B5C; /* Green-gray - labels */
--color-text-muted: #8A9B8C;     /* Light green-gray - hints */

/* State Colors */
--color-success: #519755;        /* Forest green */
--color-warning: #DBAAA7;        /* Dusty rose */
--color-error: #C98E8B;          /* Darker rose */
--color-info: #BE91BE;           /* Orchid purple */
```

## 📏 Spacing Scale

```css
--spacing-xs: 4px;    /* Extra small */
--spacing-sm: 8px;    /* Small */
--spacing-md: 16px;   /* Medium (base) */
--spacing-lg: 24px;   /* Large */
--spacing-xl: 32px;   /* Extra large */
--spacing-xxl: 48px;  /* Double extra large */
```

**Utility Classes:**
- Margin: `mt-1` to `mt-5`, `mb-1` to `mb-5`
- Padding: `p-1` to `p-5`
- Gap: `gap-1` to `gap-4`

## 🎯 Layout Classes

```vue
<!-- Page wrapper -->
<div class="content-body">
  <!-- Your content -->
</div>

<!-- Cards -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
    <p class="card-subtitle">Subtitle</p>
  </div>
  <div class="card-body">Content</div>
  <div class="card-footer">Actions</div>
</div>
```

## 🔘 Buttons

```vue
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-accent">Accent</button>
<button class="btn btn-outline">Outline</button>

<!-- Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary btn-lg">Large</button>
<button class="btn btn-primary btn-block">Full Width</button>
```

## 📝 Forms

```vue
<div class="form-group">
  <label class="form-label">Label</label>
  <input type="text" class="form-input" placeholder="Placeholder">
  <span class="form-hint">Helper text</span>
  <span class="form-error">Error message</span>
</div>

<!-- Select -->
<select class="form-select">
  <option>Option 1</option>
</select>

<!-- Textarea -->
<textarea class="form-textarea" rows="4"></textarea>
```

## 🏷️ Badges

```vue
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-error">Error</span>
<span class="badge badge-info">Info</span>
```

## 💬 Alerts

```vue
<div class="alert alert-success">Success message</div>
<div class="alert alert-warning">Warning message</div>
<div class="alert alert-error">Error message</div>
<div class="alert alert-info">Info message</div>
```

## 📊 Tables

```vue
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

## 📐 Flexbox Utilities

```vue
<!-- Display -->
<div class="d-flex">Flex container</div>
<div class="d-inline-flex">Inline flex</div>

<!-- Direction -->
<div class="d-flex flex-column">Column</div>
<div class="d-flex flex-row">Row</div>

<!-- Justify -->
<div class="d-flex justify-start">Start</div>
<div class="d-flex justify-center">Center</div>
<div class="d-flex justify-end">End</div>
<div class="d-flex justify-between">Space between</div>

<!-- Align -->
<div class="d-flex align-start">Align start</div>
<div class="d-flex align-center">Align center</div>
<div class="d-flex align-end">Align end</div>

<!-- Gap -->
<div class="d-flex gap-2">Gap 8px</div>
<div class="d-flex gap-3">Gap 16px</div>
```

## 📱 Mobile Utilities

```vue
<!-- Visibility -->
<div class="hide-mobile">Desktop only</div>
<div class="show-mobile">Mobile only</div>
<div class="hide-desktop">Mobile only</div>

<!-- Layout -->
<div class="mobile-flex-column">Stacks on mobile</div>
<div class="mobile-full-width">Full width mobile</div>
<div class="mobile-text-center">Center on mobile</div>

<!-- Spacing -->
<div class="mobile-p-2">Padding 8px mobile</div>
<div class="mobile-mt-2">Margin-top 8px mobile</div>

<!-- Touch targets -->
<button class="touch-target">44x44px min</button>
```

## 🎨 Responsive Grid

```vue
<!-- Auto-adjusting columns -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--spacing-lg);">
  <div class="card">Item 1</div>
  <div class="card">Item 2</div>
  <div class="card">Item 3</div>
</div>
```

## 📱 Breakpoints

```css
/* Mobile Portrait */
@media (max-width: 480px) { }

/* Mobile & Tablet */
@media (max-width: 768px) { }

/* Tablet Only */
@media (min-width: 769px) and (max-width: 1024px) { }

/* Desktop */
@media (min-width: 1025px) { }
```

## 🔤 Typography

```vue
<h1>Page Title (32px)</h1>
<h2>Section Header (24px)</h2>
<h3>Card Title (20px)</h3>
<h4>Subheading (18px)</h4>
<h5>Small Heading (16px)</h5>
<h6>Tiny Heading (14px)</h6>

<!-- Utility classes -->
<p class="text-center">Centered text</p>
<p class="text-secondary">Secondary color</p>
<p class="text-muted">Muted color</p>
<p class="text-bold">Bold text</p>
```

## 🎯 Common Patterns

### Page with Header
```vue
<div class="content-body">
  <div class="card mb-4">
    <div class="card-header">
      <h2 class="card-title">📊 Page Title</h2>
      <p class="card-subtitle">Description</p>
    </div>
  </div>
  <!-- Main content -->
</div>
```

### Form Card
```vue
<div class="card" style="max-width: 450px; margin: 0 auto;">
  <div class="card-header">
    <h2 class="card-title text-center">Form Title</h2>
  </div>
  <div class="card-body">
    <form @submit.prevent="handleSubmit">
      <!-- Form fields -->
      <button class="btn btn-primary btn-lg btn-block">
        Submit
      </button>
    </form>
  </div>
</div>
```

### Stats Grid
```vue
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-lg);">
  <div class="card text-center">
    <div class="card-body">
      <h2 style="color: var(--color-primary);">$1,234</h2>
      <p class="text-secondary">Revenue</p>
    </div>
  </div>
  <!-- More stat cards -->
</div>
```

### Action Buttons
```vue
<div class="d-flex justify-between align-center mobile-flex-column gap-3">
  <h2>Page Title</h2>
  <div class="d-flex gap-2 mobile-full-width">
    <button class="btn btn-primary mobile-full-width">Action 1</button>
    <button class="btn btn-outline mobile-full-width">Action 2</button>
  </div>
</div>
```

## 🔗 Navigation

```vue
<!-- Sidebar navigation (in App.vue) -->
<aside class="sidebar">
  <div class="sidebar-header">
    <a href="/" class="sidebar-logo">💰 App Name</a>
  </div>
  <nav class="sidebar-nav">
    <div class="nav-section">
      <div class="nav-section-title">Section</div>
      <a href="/page" class="nav-item">
        <span class="nav-item-icon">🏠</span>
        Page Name
      </a>
    </div>
  </nav>
</aside>
```

## ⚡ Quick Tips

1. **Always use CSS variables** for colors and spacing
2. **Wrap pages in `.content-body`** for proper layout
3. **Use utility classes** instead of custom CSS
4. **Test on mobile** - design is mobile-first
5. **44px minimum tap targets** for touch devices
6. **Use `.card` components** for content sections
7. **Apply `.btn-block`** for full-width buttons
8. **Use grid with `auto-fit`** for responsive layouts

## 📚 Documentation

- **THEME_DOCUMENTATION.md** - Complete reference
- **HTML_COMPONENT_TEMPLATES.md** - Copy-paste templates
- **MOBILE_OPTIMIZATION_GUIDE.md** - Mobile guidelines
- **VISUAL_DESIGN_GUIDE.md** - Visual reference
- **fintech-theme.css** - CSS source code

---

**Print this card or keep it handy while developing!** 🚀
