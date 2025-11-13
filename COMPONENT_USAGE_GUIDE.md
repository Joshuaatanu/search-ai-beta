# Component Usage Guide - Sentino AI

Quick reference for using the unified design system components.

---

## 🎨 Getting Started

### Import Order (Required in all pages)
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/academic.css') }}">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
```

### Include Header (Required in all pages)
```html
<body>
  {% include 'components/header.html' %}
  
  <!-- Your page content here -->
</body>
```

---

## 🔘 Buttons

### Primary Button (Main Actions)
```html
<button class="btn btn-primary">
  <i class="fas fa-check"></i> Save Changes
</button>
```

### Secondary Button
```html
<button class="btn btn-secondary">
  <i class="fas fa-times"></i> Cancel
</button>
```

### Outline Button
```html
<button class="btn btn-outline">
  <i class="fas fa-download"></i> Download
</button>
```

### Success Button
```html
<button class="btn btn-success">
  <i class="fas fa-check-circle"></i> Confirm
</button>
```

### Danger Button
```html
<button class="btn btn-danger">
  <i class="fas fa-trash"></i> Delete
</button>
```

### Icon-Only Button
```html
<button class="btn btn-icon btn-primary">
  <i class="fas fa-search"></i>
</button>
```

### Button Sizes
```html
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>
<button class="btn btn-primary btn-xl">Extra Large</button>
```

### Button Group
```html
<div class="btn-group">
  <button class="btn btn-outline">Option 1</button>
  <button class="btn btn-outline">Option 2</button>
  <button class="btn btn-primary">Option 3</button>
</div>
```

---

## 🃏 Cards

### Standard Card
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <button class="btn btn-sm btn-outline">Action</button>
  </div>
  <div class="card-body">
    <p>Card content goes here...</p>
  </div>
  <div class="card-footer">
    <span>Footer text</span>
    <button class="btn btn-primary btn-sm">Button</button>
  </div>
</div>
```

### Flat Card (with border, no shadow)
```html
<div class="card card-flat">
  <p>Content</p>
</div>
```

### Bordered Card (accent border)
```html
<div class="card card-bordered">
  <p>Important content</p>
</div>
```

### Gradient Card
```html
<div class="card card-gradient">
  <h3>Featured Item</h3>
  <p>This card has a gradient background</p>
</div>
```

---

## 📝 Forms

### Complete Form Example
```html
<form>
  <!-- Text Input -->
  <div class="form-group">
    <label class="form-label" for="username">Username</label>
    <input type="text" id="username" class="form-input" placeholder="Enter username" required>
    <small class="form-help">Choose a unique username</small>
  </div>
  
  <!-- Text Input with Error -->
  <div class="form-group">
    <label class="form-label" for="email">Email</label>
    <input type="email" id="email" class="form-input error" value="invalid">
    <span class="form-error">Please enter a valid email address</span>
  </div>
  
  <!-- Textarea -->
  <div class="form-group">
    <label class="form-label" for="bio">Bio</label>
    <textarea id="bio" class="form-textarea" placeholder="Tell us about yourself"></textarea>
  </div>
  
  <!-- Select -->
  <div class="form-group">
    <label class="form-label" for="role">Role</label>
    <select id="role" class="form-select">
      <option>Student</option>
      <option>Researcher</option>
      <option>Professor</option>
    </select>
  </div>
  
  <!-- Checkbox -->
  <div class="form-checkbox">
    <input type="checkbox" id="terms">
    <label for="terms">I agree to the terms</label>
  </div>
  
  <!-- Submit Button -->
  <button type="submit" class="btn btn-primary">
    <i class="fas fa-save"></i> Submit
  </button>
</form>
```

---

## 🪟 Modals

### Basic Modal
```html
<!-- Trigger -->
<button class="btn btn-primary" onclick="showModal('myModal')">
  Open Modal
</button>

<!-- Modal -->
<div class="modal" id="myModal">
  <div class="modal-content">
    <div class="modal-header">
      <h3>
        <i class="fas fa-info-circle"></i>
        Modal Title
      </h3>
      <button class="modal-close" onclick="closeModal('myModal')">
        <i class="fas fa-times"></i>
      </button>
    </div>
    <div class="modal-body">
      <p>Modal content goes here...</p>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal('myModal')">
        Cancel
      </button>
      <button class="btn btn-primary">
        Confirm
      </button>
    </div>
  </div>
</div>

<!-- JavaScript -->
<script>
function showModal(id) {
  document.getElementById(id).classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}
</script>
```

### Large Modal
```html
<div class="modal" id="largeModal">
  <div class="modal-content large-modal">
    <!-- ... -->
  </div>
</div>
```

### Extra Large Modal
```html
<div class="modal" id="xlModal">
  <div class="modal-content extra-large-modal">
    <!-- ... -->
  </div>
</div>
```

---

## 🔔 Notifications

### Success Notification
```html
<div class="notification notification-success">
  <div class="notification-icon">
    <i class="fas fa-check-circle"></i>
  </div>
  <div class="notification-content">
    <div class="notification-title">Success!</div>
    <div class="notification-message">Your changes have been saved.</div>
  </div>
  <button class="notification-close">
    <i class="fas fa-times"></i>
  </button>
</div>
```

### Error Notification
```html
<div class="notification notification-error">
  <div class="notification-icon">
    <i class="fas fa-exclamation-circle"></i>
  </div>
  <div class="notification-content">
    <div class="notification-title">Error!</div>
    <div class="notification-message">Something went wrong.</div>
  </div>
  <button class="notification-close">
    <i class="fas fa-times"></i>
  </button>
</div>
```

### Warning Notification
```html
<div class="notification notification-warning">
  <div class="notification-icon">
    <i class="fas fa-exclamation-triangle"></i>
  </div>
  <div class="notification-content">
    <div class="notification-title">Warning!</div>
    <div class="notification-message">Please review your input.</div>
  </div>
  <button class="notification-close">
    <i class="fas fa-times"></i>
  </button>
</div>
```

### Info Notification
```html
<div class="notification notification-info">
  <div class="notification-icon">
    <i class="fas fa-info-circle"></i>
  </div>
  <div class="notification-content">
    <div class="notification-title">Info</div>
    <div class="notification-message">New features available!</div>
  </div>
  <button class="notification-close">
    <i class="fas fa-times"></i>
  </button>
</div>
```

### JavaScript Helper
```javascript
function showNotification(type, title, message) {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <div class="notification-icon">
      <i class="fas fa-${type === 'success' ? 'check-circle' : 
                         type === 'error' ? 'exclamation-circle' :
                         type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
    </div>
    <div class="notification-content">
      <div class="notification-title">${title}</div>
      <div class="notification-message">${message}</div>
    </div>
    <button class="notification-close" onclick="this.parentElement.remove()">
      <i class="fas fa-times"></i>
    </button>
  `;
  document.body.appendChild(notification);
  
  // Auto-remove after 5 seconds
  setTimeout(() => notification.remove(), 5000);
}

// Usage:
showNotification('success', 'Saved!', 'Your changes have been saved.');
```

---

## ⏳ Loading States

### Inline Spinner
```html
<span class="loading-spinner"></span>
```

### Button with Spinner
```html
<button class="btn btn-primary" disabled>
  <span class="loading-spinner"></span>
  Loading...
</button>
```

### Full Page Overlay
```html
<div class="loading-overlay">
  <div class="loading-content">
    <div class="loading-spinner"></div>
    <p>Loading...</p>
  </div>
</div>
```

---

## 📐 Layout

### Container
```html
<div class="container">
  <!-- Max-width: 1400px, centered -->
</div>

<div class="container container-sm">
  <!-- Max-width: 800px, centered -->
</div>

<div class="container container-lg">
  <!-- Max-width: 1600px, centered -->
</div>
```

### Grid
```html
<!-- 2 Columns -->
<div class="grid grid-2">
  <div>Column 1</div>
  <div>Column 2</div>
</div>

<!-- 3 Columns -->
<div class="grid grid-3">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>

<!-- 4 Columns -->
<div class="grid grid-4">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
  <div>Column 4</div>
</div>
```

### Flexbox
```html
<div class="flex items-center justify-between gap-4">
  <div>Left content</div>
  <div>Right content</div>
</div>

<div class="flex flex-col gap-6">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

---

## 🎨 Utility Classes

### Text Alignment
```html
<p class="text-center">Centered text</p>
```

### Text Colors
```html
<p class="text-primary">Primary color text</p>
<p class="text-gray">Gray text</p>
<p class="text-success">Success color text</p>
<p class="text-error">Error color text</p>
```

### Spacing
```html
<div class="mt-4">Margin top</div>
<div class="mb-4">Margin bottom</div>
<div class="p-4">Padding all sides</div>
<div class="p-6">Larger padding</div>
```

### Display
```html
<div class="hidden">Hidden element</div>
<div class="block">Block element</div>
<div class="inline-block">Inline-block element</div>
```

### Responsive Display
```html
<div class="mobile-hidden">Hidden on mobile</div>
<div class="desktop-hidden">Hidden on desktop</div>
```

---

## 🎯 Common Patterns

### Hero Section
```html
<section style="background: var(--gradient-primary); color: white; padding: 4rem 2rem; text-align: center;">
  <div class="container">
    <h1 style="font-size: var(--text-5xl); margin-bottom: 1rem;">Welcome to Sentino AI</h1>
    <p style="font-size: var(--text-xl); margin-bottom: 2rem;">Your academic research companion</p>
    <button class="btn btn-primary btn-lg">Get Started</button>
  </div>
</section>
```

### Stats Grid
```html
<div class="grid grid-3 gap-6">
  <div class="card text-center">
    <div style="font-size: 3rem; color: var(--primary-blue); margin-bottom: 1rem;">
      <i class="fas fa-search"></i>
    </div>
    <h3 style="font-size: var(--text-3xl); font-weight: bold; margin-bottom: 0.5rem;">1,234</h3>
    <p style="color: var(--gray-600);">Searches</p>
  </div>
  <div class="card text-center">
    <div style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;">
      <i class="fas fa-file-pdf"></i>
    </div>
    <h3 style="font-size: var(--text-3xl); font-weight: bold; margin-bottom: 0.5rem;">567</h3>
    <p style="color: var(--gray-600);">Documents</p>
  </div>
  <div class="card text-center">
    <div style="font-size: 3rem; color: var(--accent-purple); margin-bottom: 1rem;">
      <i class="fas fa-brain"></i>
    </div>
    <h3 style="font-size: var(--text-3xl); font-weight: bold; margin-bottom: 0.5rem;">89</h3>
    <p style="color: var(--gray-600);">Analyses</p>
  </div>
</div>
```

### Feature Cards
```html
<div class="grid grid-3 gap-6">
  <div class="card">
    <div style="width: 48px; height: 48px; background: var(--primary-blue); color: white; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 1rem;">
      <i class="fas fa-bolt"></i>
    </div>
    <h3 style="font-size: var(--text-xl); font-weight: bold; margin-bottom: 0.5rem;">Quick Search</h3>
    <p style="color: var(--gray-600);">Get instant answers to your questions</p>
    <button class="btn btn-outline btn-sm" style="margin-top: 1rem;">Learn More</button>
  </div>
  <!-- More feature cards... -->
</div>
```

### Empty State
```html
<div class="card text-center" style="padding: 4rem 2rem;">
  <div style="font-size: 4rem; color: var(--gray-400); margin-bottom: 1rem;">
    <i class="fas fa-inbox"></i>
  </div>
  <h3 style="font-size: var(--text-2xl); font-weight: bold; margin-bottom: 0.5rem;">No Items Yet</h3>
  <p style="color: var(--gray-600); margin-bottom: 2rem;">Get started by adding your first item</p>
  <button class="btn btn-primary">
    <i class="fas fa-plus"></i> Add Item
  </button>
</div>
```

---

## 🎨 Color Usage Guide

### When to Use Each Color

**Primary Blue** (`--primary-blue`)
- Main CTAs
- Primary navigation
- Links
- Active states

**Success Green** (`--success`)
- Success messages
- Positive actions
- Completion states
- Checkmarks

**Error Red** (`--error`)
- Error messages
- Destructive actions
- Validation errors
- Warnings about loss

**Warning Orange** (`--warning`)
- Caution messages
- Important notices
- Temporary states

**Info Blue** (`--info`)
- Informational messages
- Helpful tips
- Neutral notifications

**Gray** (`--gray-X00`)
- Text hierarchy
- Borders
- Backgrounds
- Disabled states

---

## 📱 Responsive Best Practices

### Mobile-First Approach
```css
/* Base styles for mobile */
.element {
  font-size: 1rem;
  padding: 1rem;
}

/* Tablet and up */
@media (min-width: 768px) {
  .element {
    font-size: 1.125rem;
    padding: 1.5rem;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .element {
    font-size: 1.25rem;
    padding: 2rem;
  }
}
```

### Touch Targets
- Minimum 44px × 44px for touch targets
- Use `btn-lg` on mobile for important actions
- Add padding around clickable elements

### Content Priority
- Show most important content first on mobile
- Use `mobile-hidden` for secondary content
- Stack vertically on small screens

---

## ✅ Checklist for New Pages

When creating a new page:

- [ ] Import `components.css` before `academic.css`
- [ ] Include Font Awesome icons
- [ ] Add `{% include 'components/header.html' %}`
- [ ] Use standard button classes (`.btn-primary`, etc.)
- [ ] Use `.card` for content sections
- [ ] Use `.form-input`, `.form-label` for forms
- [ ] Use `.container` for page width
- [ ] Use `.grid` for layouts
- [ ] Add loading states for async actions
- [ ] Add error states for failures
- [ ] Add empty states when no content
- [ ] Test on mobile (< 768px)
- [ ] Test on tablet (768px - 1024px)
- [ ] Test on desktop (> 1024px)
- [ ] Test keyboard navigation
- [ ] Check color contrast
- [ ] Verify all links work

---

## 🚀 Quick Start Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title - Sentino AI</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/academic.css') }}">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
  <!-- Unified Header -->
  {% include 'components/header.html' %}
  
  <!-- Page Content -->
  <main>
    <div class="container" style="padding: 2rem 0;">
      <h1>Page Title</h1>
      
      <div class="grid grid-2 gap-6" style="margin-top: 2rem;">
        <div class="card">
          <h2 class="card-title">Section 1</h2>
          <p>Content goes here...</p>
        </div>
        
        <div class="card">
          <h2 class="card-title">Section 2</h2>
          <p>Content goes here...</p>
        </div>
      </div>
    </div>
  </main>
</body>
</html>
```

---

**Happy Coding! 🎉**

For questions or issues, refer to `UI_DESIGN_SYSTEM.md` or `UI_IMPLEMENTATION_SUMMARY.md`.







