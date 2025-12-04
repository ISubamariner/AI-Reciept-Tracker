# HTML Component Templates Reference

## Overview

This document provides ready-to-use HTML/Vue template patterns for the AI Receipt Tracker application. All templates use the consolidated fintech theme with the Wildflowers color palette (calming greens and purples) and flat design principles.

---

## Table of Contents

1. [Layout Templates](#layout-templates)
2. [Card Components](#card-components)
3. [Form Components](#form-components)
4. [Button Patterns](#button-patterns)
5. [Table Layouts](#table-layouts)
6. [Alert Messages](#alert-messages)
7. [Badge & Status Indicators](#badge--status-indicators)
8. [Grid Layouts](#grid-layouts)
9. [Navigation Patterns](#navigation-patterns)
10. [Complete Page Examples](#complete-page-examples)

---

## Layout Templates

### Basic Page Layout

```vue
<template>
  <div class="content-body">
    <!-- Your page content here -->
  </div>
</template>
```

**Use Case:** Every page/view should wrap content in `.content-body` for proper spacing and max-width.

---

### Page with Header Card

```vue
<template>
  <div class="content-body">
    <!-- Page Header -->
    <div class="card mb-4">
      <div class="card-header">
        <h2 class="card-title">📊 Page Title</h2>
        <p class="card-subtitle">Brief description of the page</p>
      </div>
      <div class="card-body">
        <!-- Optional header content -->
      </div>
    </div>

    <!-- Main content below -->
  </div>
</template>
```

**Use Case:** Standard page layout with descriptive header.

---

### Two-Column Layout

```vue
<template>
  <div class="content-body">
    <div class="d-flex gap-4" style="flex-wrap: wrap;">
      <!-- Left Column -->
      <div style="flex: 1; min-width: 300px;">
        <div class="card">
          <!-- Left content -->
        </div>
      </div>

      <!-- Right Column -->
      <div style="flex: 1; min-width: 300px;">
        <div class="card">
          <!-- Right content -->
        </div>
      </div>
    </div>
  </div>
</template>
```

**Use Case:** Side-by-side content sections that stack on mobile.

---

## Card Components

### Simple Card

```vue
<div class="card">
  <div class="card-body">
    <p>Card content goes here</p>
  </div>
</div>
```

**Properties:**
- White background
- 2px forest green border
- 24px padding
- Automatic bottom margin

---

### Card with Header

```vue
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <p class="card-subtitle">Optional subtitle</p>
  </div>
  <div class="card-body">
    <p>Main card content</p>
  </div>
</div>
```

**Use Case:** Most common card pattern for sections.

---

### Card with Footer

```vue
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Transaction Details</h3>
  </div>
  <div class="card-body">
    <p>Transaction information here</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary btn-block">View Details</button>
  </div>
</div>
```

**Use Case:** Cards with action buttons at the bottom.

---

### Feature Card (Centered)

```vue
<div class="card text-center">
  <div class="card-body">
    <div style="font-size: 3rem; margin-bottom: var(--spacing-md);">⚡</div>
    <h4>Feature Title</h4>
    <p class="text-secondary">Feature description text</p>
  </div>
</div>
```

**Use Case:** Feature highlights, benefits, or icon-based cards.

---

## Form Components

### Complete Form Template

```vue
<div class="card" style="max-width: 450px; margin: 0 auto;">
  <div class="card-header">
    <h2 class="card-title text-center">Form Title</h2>
    <p class="card-subtitle text-center">Form description</p>
  </div>
  
  <div class="card-body">
    <form @submit.prevent="handleSubmit">
      <!-- Text Input -->
      <div class="form-group">
        <label for="field1" class="form-label">Field Label</label>
        <input 
          type="text" 
          id="field1" 
          v-model="field1" 
          class="form-input" 
          placeholder="Enter value"
          required
        >
        <span class="form-hint">Helper text goes here</span>
      </div>

      <!-- Select Dropdown -->
      <div class="form-group">
        <label for="field2" class="form-label">Select Option</label>
        <select id="field2" v-model="field2" class="form-select">
          <option value="option1">Option 1</option>
          <option value="option2">Option 2</option>
        </select>
      </div>

      <!-- Textarea -->
      <div class="form-group">
        <label for="field3" class="form-label">Description</label>
        <textarea 
          id="field3" 
          v-model="field3" 
          class="form-textarea" 
          rows="4"
          placeholder="Enter description"
        ></textarea>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="alert alert-error">
        {{ error }}
      </div>

      <!-- Success Alert -->
      <div v-if="success" class="alert alert-success">
        ✓ {{ success }}
      </div>

      <!-- Submit Button -->
      <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="loading">
        {{ loading ? '🔄 Processing...' : '✓ Submit' }}
      </button>
    </form>
  </div>

  <div class="card-footer text-center">
    <p class="text-secondary">
      Additional info or link
    </p>
  </div>
</div>
```

**Use Case:** Login, registration, or any data entry form.

---

### Inline Form Fields

```vue
<div class="d-flex gap-3" style="flex-wrap: wrap;">
  <div class="form-group" style="flex: 1; min-width: 200px;">
    <label class="form-label">First Name</label>
    <input type="text" class="form-input">
  </div>
  <div class="form-group" style="flex: 1; min-width: 200px;">
    <label class="form-label">Last Name</label>
    <input type="text" class="form-input">
  </div>
</div>
```

**Use Case:** Side-by-side form fields that stack on mobile.

---

### Form with Validation

```vue
<div class="form-group">
  <label for="email" class="form-label">Email Address</label>
  <input 
    type="email" 
    id="email" 
    v-model="email" 
    class="form-input"
    :class="{ 'border-error': emailError }"
  >
  <span v-if="emailError" class="form-error">{{ emailError }}</span>
  <span v-else class="form-hint">We'll never share your email</span>
</div>
```

**Additional CSS needed:**
```css
.form-input.border-error {
  border-color: var(--color-error);
}
```

---

## Button Patterns

### Button Variations

```vue
<!-- Primary (Forest Green) -->
<button class="btn btn-primary">Primary</button>

<!-- Secondary (Celadon Green) -->
<button class="btn btn-secondary">Secondary</button>

<!-- Accent (Dusty Rose) -->
<button class="btn btn-accent">Accent Action</button>

<!-- Outline -->
<button class="btn btn-outline">Outline Button</button>

<!-- Small -->
<button class="btn btn-primary btn-sm">Small</button>

<!-- Large -->
<button class="btn btn-primary btn-lg">Large</button>

<!-- Full Width -->
<button class="btn btn-primary btn-block">Full Width</button>

<!-- Disabled -->
<button class="btn btn-primary" disabled>Disabled</button>
```

---

### Button Groups

```vue
<!-- Horizontal Group -->
<div class="d-flex gap-2">
  <button class="btn btn-primary">Save</button>
  <button class="btn btn-outline">Cancel</button>
</div>

<!-- Vertical Group -->
<div class="d-flex flex-column gap-2">
  <button class="btn btn-primary btn-block">Option 1</button>
  <button class="btn btn-secondary btn-block">Option 2</button>
  <button class="btn btn-outline btn-block">Option 3</button>
</div>
```

---

### Icon Buttons

```vue
<button class="btn btn-primary">
  📤 Upload
</button>

<button class="btn btn-secondary">
  📊 View Reports
</button>

<button class="btn btn-accent">
  ⚙️ Settings
</button>
```

**Use Case:** Buttons with emoji or icon indicators.

---

## Table Layouts

### Basic Data Table

```vue
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>Column 1</th>
        <th>Column 2</th>
        <th>Column 3</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in items" :key="item.id">
        <td>{{ item.field1 }}</td>
        <td>{{ item.field2 }}</td>
        <td>{{ item.field3 }}</td>
      </tr>
    </tbody>
  </table>
</div>
```

**Features:**
- Bordered container
- Hover effects on rows
- Responsive horizontal scroll

---

### Table with Actions

```vue
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Status</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in items" :key="item.id">
        <td>{{ item.name }}</td>
        <td>
          <span class="badge badge-success">Active</span>
        </td>
        <td>
          <div class="d-flex gap-2">
            <button class="btn btn-primary btn-sm">Edit</button>
            <button class="btn btn-outline btn-sm">Delete</button>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

---

### Key-Value Table (Details View)

```vue
<div class="table-container">
  <table class="table">
    <tbody>
      <tr>
        <td style="font-weight: var(--font-weight-semibold); width: 200px;">
          Vendor Name
        </td>
        <td>Coffee Shop</td>
      </tr>
      <tr>
        <td style="font-weight: var(--font-weight-semibold);">
          Transaction Date
        </td>
        <td>December 4, 2025</td>
      </tr>
      <tr>
        <td style="font-weight: var(--font-weight-semibold);">
          Amount
        </td>
        <td style="color: var(--color-primary); font-weight: var(--font-weight-bold);">
          $24.50
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

**Use Case:** Displaying object properties in a structured format.

---

## Alert Messages

### Alert Variations

```vue
<!-- Success -->
<div class="alert alert-success">
  ✓ Operation completed successfully!
</div>

<!-- Warning -->
<div class="alert alert-warning">
  ⚠️ Please review your information before proceeding.
</div>

<!-- Error -->
<div class="alert alert-error">
  ✕ An error occurred. Please try again.
</div>

<!-- Info -->
<div class="alert alert-info">
  ℹ️ Here's some helpful information.
</div>
```

---

### Dismissible Alert

```vue
<div v-if="showAlert" class="alert alert-success">
  <div class="d-flex justify-between align-center">
    <span>✓ Changes saved successfully!</span>
    <button @click="showAlert = false" class="btn btn-sm" style="border: none; background: transparent; cursor: pointer;">
      ✕
    </button>
  </div>
</div>
```

---

## Badge & Status Indicators

### Badge Variations

```vue
<!-- Success Badge -->
<span class="badge badge-success">Processed</span>

<!-- Warning Badge -->
<span class="badge badge-warning">Pending</span>

<!-- Error Badge -->
<span class="badge badge-error">Failed</span>

<!-- Info Badge -->
<span class="badge badge-info">New</span>
```

---

### Status with Icon

```vue
<span class="badge badge-success">
  ✓ Approved
</span>

<span class="badge badge-warning">
  ⏳ In Progress
</span>

<span class="badge badge-error">
  ✕ Rejected
</span>
```

---

### Badge in Context

```vue
<div class="d-flex justify-between align-center">
  <h3>Transaction #12345</h3>
  <span class="badge badge-success">Completed</span>
</div>
```

---

## Grid Layouts

### Responsive Card Grid

```vue
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--spacing-lg);">
  <div class="card">
    <div class="card-body">Card 1</div>
  </div>
  <div class="card">
    <div class="card-body">Card 2</div>
  </div>
  <div class="card">
    <div class="card-body">Card 3</div>
  </div>
</div>
```

**Properties:**
- Automatically adjusts columns based on available space
- Minimum card width: 280px
- Gap between cards: 24px (--spacing-lg)

---

### Fixed Column Grid

```vue
<!-- 2 Columns -->
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-lg);">
  <div class="card">Left</div>
  <div class="card">Right</div>
</div>

<!-- 3 Columns -->
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--spacing-lg);">
  <div class="card">Column 1</div>
  <div class="card">Column 2</div>
  <div class="card">Column 3</div>
</div>

<!-- 4 Columns -->
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--spacing-lg);">
  <div class="card">Item 1</div>
  <div class="card">Item 2</div>
  <div class="card">Item 3</div>
  <div class="card">Item 4</div>
</div>
```

---

### Dashboard Stats Grid

```vue
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-md);">
  <div class="card text-center">
    <div class="card-body">
      <h2 style="color: var(--color-primary); margin-bottom: var(--spacing-sm);">$1,234</h2>
      <p class="text-secondary">Total Revenue</p>
    </div>
  </div>
  <div class="card text-center">
    <div class="card-body">
      <h2 style="color: var(--color-primary); margin-bottom: var(--spacing-sm);">42</h2>
      <p class="text-secondary">Transactions</p>
    </div>
  </div>
  <div class="card text-center">
    <div class="card-body">
      <h2 style="color: var(--color-primary); margin-bottom: var(--spacing-sm);">98%</h2>
      <p class="text-secondary">Success Rate</p>
    </div>
  </div>
</div>
```

**Use Case:** Dashboard metric cards.

---

## Navigation Patterns

### Breadcrumb Navigation

```vue
<nav class="mb-4" style="font-size: var(--font-size-sm);">
  <router-link to="/" style="color: var(--color-primary);">Home</router-link>
  <span class="text-muted"> / </span>
  <router-link to="/transactions" style="color: var(--color-primary);">Transactions</router-link>
  <span class="text-muted"> / </span>
  <span class="text-secondary">Details</span>
</nav>
```

---

### Tab Navigation (Card Header)

```vue
<div class="card">
  <div class="card-header">
    <div class="d-flex gap-3 border-bottom">
      <a 
        href="#" 
        class="tab-link" 
        :class="{ active: activeTab === 'overview' }"
        @click.prevent="activeTab = 'overview'"
      >
        Overview
      </a>
      <a 
        href="#" 
        class="tab-link"
        :class="{ active: activeTab === 'details' }"
        @click.prevent="activeTab = 'details'"
      >
        Details
      </a>
    </div>
  </div>
  <div class="card-body">
    <div v-if="activeTab === 'overview'">Overview content</div>
    <div v-if="activeTab === 'details'">Details content</div>
  </div>
</div>
```

**Additional CSS:**
```css
.tab-link {
  padding: var(--spacing-sm) var(--spacing-md);
  text-decoration: none;
  color: var(--color-text-secondary);
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
}

.tab-link:hover {
  color: var(--color-primary);
}

.tab-link.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}
```

---

## Complete Page Examples

### Dashboard Page

```vue
<template>
  <div class="content-body">
    <!-- Hero Card -->
    <div class="card mb-4">
      <div class="card-header">
        <h1 class="card-title">📊 Dashboard</h1>
        <p class="card-subtitle">Welcome back, User!</p>
      </div>
    </div>

    <!-- Stats Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--spacing-lg); margin-bottom: var(--spacing-xl);">
      <div class="card">
        <div class="card-body text-center">
          <h2 style="color: var(--color-primary);">$5,432</h2>
          <p class="text-secondary">Total Spent</p>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <h2 style="color: var(--color-primary);">127</h2>
          <p class="text-secondary">Receipts</p>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <h2 style="color: var(--color-primary);">15</h2>
          <p class="text-secondary">This Month</p>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Recent Activity</h3>
      </div>
      <div class="card-body">
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Vendor</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Dec 4, 2025</td>
                <td>Coffee Shop</td>
                <td>$4.50</td>
                <td><span class="badge badge-success">Processed</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
```

---

### Detail View Page

```vue
<template>
  <div class="content-body">
    <!-- Back Navigation -->
    <nav class="mb-3">
      <router-link to="/transactions" style="color: var(--color-primary);">
        ← Back to Transactions
      </router-link>
    </nav>

    <!-- Header Card -->
    <div class="card mb-4">
      <div class="card-header">
        <div class="d-flex justify-between align-center">
          <div>
            <h2 class="card-title">Transaction #12345</h2>
            <p class="card-subtitle">Coffee Shop</p>
          </div>
          <span class="badge badge-success">Processed</span>
        </div>
      </div>
    </div>

    <!-- Details Grid -->
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: var(--spacing-lg);">
      <!-- Main Details -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Transaction Details</h3>
        </div>
        <div class="card-body">
          <div class="table-container">
            <table class="table">
              <tbody>
                <tr>
                  <td style="font-weight: var(--font-weight-semibold);">Date</td>
                  <td>December 4, 2025</td>
                </tr>
                <tr>
                  <td style="font-weight: var(--font-weight-semibold);">Amount</td>
                  <td style="color: var(--color-primary); font-weight: var(--font-weight-bold);">$4.50</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Actions Sidebar -->
      <div>
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Actions</h3>
          </div>
          <div class="card-body">
            <div class="d-flex flex-column gap-2">
              <button class="btn btn-primary btn-block">Edit</button>
              <button class="btn btn-outline btn-block">Download</button>
              <button class="btn btn-outline btn-block">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
```

---

### Empty State Page

```vue
<template>
  <div class="content-body">
    <div class="card text-center" style="max-width: 500px; margin: 0 auto;">
      <div class="card-body">
        <div style="font-size: 5rem; margin-bottom: var(--spacing-lg);">📭</div>
        <h2 class="mb-3">No Items Found</h2>
        <p class="text-secondary mb-4">
          You haven't created any items yet. Get started by clicking the button below.
        </p>
        <button class="btn btn-primary btn-lg">
          ➕ Create First Item
        </button>
      </div>
    </div>
  </div>
</template>
```

---

### Loading State

```vue
<template>
  <div class="content-body">
    <div class="card text-center">
      <div class="card-body">
        <div style="font-size: 3rem; margin-bottom: var(--spacing-md);">🔄</div>
        <p class="text-secondary">Loading data...</p>
      </div>
    </div>
  </div>
</template>
```

---

### Error State

```vue
<template>
  <div class="content-body">
    <div class="card">
      <div class="card-body">
        <div class="alert alert-error mb-3">
          ✕ Failed to load data. Please try again.
        </div>
        <button @click="retry" class="btn btn-primary">
          🔄 Retry
        </button>
      </div>
    </div>
  </div>
</template>
```

---

## Best Practices

### 1. Consistent Spacing
Always use CSS variables for spacing:
```vue
<div class="mb-4">  <!-- Use utility classes -->
<div style="margin-bottom: var(--spacing-lg);">  <!-- Or CSS variables -->
```

### 2. Responsive Design
Use flex and grid with wrapping:
```vue
<div class="d-flex gap-3" style="flex-wrap: wrap;">
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
```

### 3. Color Usage
Reference theme colors via CSS variables:
```vue
<span style="color: var(--color-primary);">
<div style="background-color: var(--color-background-alt);">
```

### 4. Icon Integration
Use emojis or icon fonts consistently:
```vue
<button class="btn btn-primary">📤 Upload</button>
<h2>💰 Receipt Tracker</h2>
```

### 5. Accessibility
- Use semantic HTML
- Include proper labels
- Maintain keyboard navigation
- Use ARIA attributes when needed

---

## Quick Reference

### Common Utility Classes
- **Spacing**: `mb-3`, `mt-4`, `p-3`, `gap-3`
- **Display**: `d-flex`, `d-block`, `d-none`
- **Flex**: `justify-between`, `align-center`, `flex-column`
- **Text**: `text-center`, `text-secondary`, `text-muted`
- **Border**: `border`, `border-radius`
- **Background**: `bg-white`, `bg-primary`

### CSS Variable Quick List
- Colors: `--color-primary`, `--color-secondary`, `--color-accent`
- Spacing: `--spacing-sm`, `--spacing-md`, `--spacing-lg`
- Fonts: `--font-size-base`, `--font-weight-bold`
- Layout: `--sidebar-width`, `--border-width`

---

## Notes

- All templates are designed for Vue 3 with Composition API
- Templates assume fintech-theme.css is imported
- Adjust inline styles as needed for specific use cases
- Always test responsive behavior on mobile devices
- Keep component templates modular and reusable

---

**Last Updated:** December 2025  
**Version:** 1.0.0
