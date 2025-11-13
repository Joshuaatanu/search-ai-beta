# Sentino AI - Unified UI/UX Design System

## 🎯 Design Philosophy

**Core Principles:**
1. **Consistency** - Same patterns across all pages
2. **Clarity** - Clear visual hierarchy
3. **Efficiency** - Minimal clicks to accomplish tasks
4. **Accessibility** - WCAG 2.1 AA compliance
5. **Responsiveness** - Mobile-first approach

---

## 🎨 Visual Design System

### Color Palette

```css
/* Primary Colors */
--primary-blue: #2563eb;      /* Main actions, links */
--primary-dark: #1d4ed8;      /* Hover states */
--primary-light: #3b82f6;     /* Backgrounds */

/* Secondary Colors */
--secondary-gray: #64748b;    /* Secondary actions */
--accent-green: #10b981;      /* Success states */
--accent-purple: #8b5cf6;     /* Special features */

/* Semantic Colors */
--success: #10b981;
--warning: #f59e0b;
--error: #ef4444;
--info: #3b82f6;

/* Neutrals */
--gray-50: #f8fafc;
--gray-100: #f1f5f9;
--gray-200: #e2e8f0;
--gray-300: #cbd5e1;
--gray-400: #94a3b8;
--gray-500: #64748b;
--gray-600: #475569;
--gray-700: #334155;
--gray-800: #1e293b;
--gray-900: #0f172a;

/* Gradients */
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-accent: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
--gradient-success: linear-gradient(135deg, #10b981 0%, #059669 100%);
```

### Typography

```css
/* Font Families */
--font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
--font-mono: 'JetBrains Mono', 'Courier New', monospace;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
--text-5xl: 3rem;      /* 48px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

### Spacing Scale

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### Border Radius

```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-2xl: 24px;
--radius-full: 9999px;
```

### Shadows

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

---

## 📐 Layout Structure

### Page Template (All Pages)

```
┌─────────────────────────────────────────────┐
│  HEADER (Sticky)                            │
│  [Logo] [Navigation] [Search] [User Menu]  │
├─────────────────────────────────────────────┤
│                                             │
│  MAIN CONTENT                               │
│  Max-width: 1400px                          │
│  Padding: 2rem                              │
│                                             │
│  [Page specific content]                    │
│                                             │
├─────────────────────────────────────────────┤
│  FOOTER (Optional)                          │
│  Copyright, Links, etc.                     │
└─────────────────────────────────────────────┘
```

### Grid System

```css
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.container-sm {
  max-width: 800px;
}

.container-lg {
  max-width: 1600px;
}

.grid {
  display: grid;
  gap: 1.5rem;
}

.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

/* Responsive */
@media (max-width: 1024px) {
  .grid-3, .grid-4 { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
}
```

---

## 🧩 Component Library

### 1. Header/Navigation

**Structure:**
- Sticky header with blur backdrop
- Logo (left) + Navigation (center) + User Menu (right)
- Mobile: Hamburger menu

**Components:**
- Logo with click-to-home
- 5-7 main navigation items
- Search bar (optional)
- User dropdown menu
- Mobile menu toggle

### 2. Buttons

**Primary Button:**
```css
.btn-primary {
  background: var(--primary-blue);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
```

**Secondary Button:**
```css
.btn-secondary {
  background: var(--gray-100);
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
}
```

**Icon Button:**
```css
.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### 3. Cards

**Standard Card:**
```css
.card {
  background: white;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-md);
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}
```

### 4. Forms

**Input Fields:**
```css
.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
```

### 5. Modals

**Modal Structure:**
```css
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: var(--radius-xl);
  max-width: 800px;
  margin: 2rem auto;
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
}
```

### 6. Notifications/Alerts

**Toast Notifications:**
```css
.notification {
  position: fixed;
  top: 1rem;
  right: 1rem;
  max-width: 400px;
  padding: 1rem 1.5rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  animation: slideInRight 0.3s;
}

.notification-success {
  background: var(--success);
  color: white;
}

.notification-error {
  background: var(--error);
  color: white;
}
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First Approach */

/* Small devices (phones) */
@media (min-width: 640px) { }

/* Medium devices (tablets) */
@media (min-width: 768px) { }

/* Large devices (desktops) */
@media (min-width: 1024px) { }

/* Extra large devices */
@media (min-width: 1280px) { }

/* 2K screens */
@media (min-width: 1536px) { }
```

---

## 🎬 Animations & Transitions

### Standard Transitions

```css
--transition-fast: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
--transition-normal: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
```

### Common Animations

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

---

## 🔧 Implementation Plan

### Phase 1: Core Components (Week 1)
1. Create unified header component
2. Standardize button styles
3. Create card component library
4. Implement form styling
5. Create modal component

### Phase 2: Page Updates (Week 2)
1. Update `academic_research.html` (main page)
2. Update `profile.html`
3. Update `settings.html`
4. Update `pdf_analysis.html`
5. Update auth pages (`login.html`, `signup.html`)

### Phase 3: Polish (Week 3)
1. Add loading states
2. Implement error states
3. Add empty states
4. Polish animations
5. Test responsiveness

### Phase 4: Testing & QA (Week 4)
1. Cross-browser testing
2. Mobile device testing
3. Accessibility audit
4. Performance optimization
5. User feedback collection

---

## 📋 Page Inventory & Redesign Status

### Current Pages:

| Page | Status | Priority | Redesign Needed |
|------|--------|----------|-----------------|
| academic_research.html | ⚠️ Partial | HIGH | Header, Navigation |
| profile.html | ✅ Good | MEDIUM | Minor tweaks |
| account_settings.html | ✅ Good | MEDIUM | Minor tweaks |
| pdf_analysis.html | ✅ Good | MEDIUM | Minor tweaks |
| login.html | ✅ Good | LOW | Consistent with signup |
| signup.html | ✅ Good | LOW | Consistent with login |
| index.html | ❌ Outdated | HIGH | Full redesign |
| chat.html | ❌ Outdated | MEDIUM | Full redesign |
| base.html | ❌ Not Used | LOW | Remove or update |
| demo.html | ❌ Unknown | LOW | Review |
| feature_disabled.html | ❌ Unknown | LOW | Review |

### Consistency Issues Identified:

1. **Navigation:**
   - `academic_research.html` - Modern nav with modals
   - `profile.html` - Simple nav links
   - `pdf_analysis.html` - Similar to profile
   - `index.html` - Different nav structure

2. **Headers:**
   - Gradient header (profile, settings, pdf)
   - Sticky white header (academic_research)
   - Different header (index, chat)

3. **Buttons:**
   - Mix of `.btn-primary`, `.feature-button`, custom styles
   - Inconsistent hover states

4. **Forms:**
   - Different input styles across pages
   - Inconsistent validation display

5. **Modals:**
   - Used only in academic_research.html
   - Should be standardized

---

## 🎯 Unified Navigation Structure

### Standard Navigation (All Pages):

```html
<header class="app-header">
  <div class="header-container">
    <!-- Logo -->
    <a href="/" class="logo">
      <i class="fas fa-graduation-cap"></i>
      <span>Sentino AI</span>
    </a>
    
    <!-- Main Navigation -->
    <nav class="main-nav">
      <a href="/" class="nav-link">
        <i class="fas fa-home"></i>
        <span>Home</span>
      </a>
      <a href="/#papers" class="nav-link">
        <i class="fas fa-graduation-cap"></i>
        <span>Papers</span>
      </a>
      <a href="/#quick" class="nav-link">
        <i class="fas fa-bolt"></i>
        <span>Quick</span>
      </a>
      <a href="/#deep" class="nav-link">
        <i class="fas fa-brain"></i>
        <span>Deep</span>
      </a>
      <a href="/pdf-analysis" class="nav-link">
        <i class="fas fa-file-pdf"></i>
        <span>PDF</span>
      </a>
    </nav>
    
    <!-- User Menu -->
    <div class="header-actions">
      <button class="search-trigger">
        <i class="fas fa-search"></i>
      </button>
      
      <!-- If Logged In -->
      <div class="user-menu">
        <button class="user-trigger">
          <img src="avatar.jpg" alt="User" class="avatar">
          <span class="username">John Doe</span>
          <i class="fas fa-chevron-down"></i>
        </button>
        <div class="user-dropdown">
          <a href="/profile"><i class="fas fa-user"></i> Profile</a>
          <a href="/settings"><i class="fas fa-cog"></i> Settings</a>
          <a href="/history"><i class="fas fa-history"></i> History</a>
          <hr>
          <a href="/logout"><i class="fas fa-sign-out-alt"></i> Logout</a>
        </div>
      </div>
      
      <!-- If Not Logged In -->
      <a href="/login" class="btn-primary">Login</a>
      
      <!-- Mobile Toggle -->
      <button class="mobile-toggle">
        <i class="fas fa-bars"></i>
      </button>
    </div>
  </div>
</header>
```

---

## 🎨 Recommended Changes

### Immediate Priorities:

1. **Create Unified Header Component** ✅
   - Use same header across all pages
   - Implement in new `components/header.html`
   - Include in all page templates

2. **Standardize Buttons** ✅
   - Replace all button classes with standard ones
   - `.btn-primary`, `.btn-secondary`, `.btn-outline`
   - Consistent hover/active states

3. **Unified Card Design** ✅
   - Same card style everywhere
   - Standard padding, shadows, radius

4. **Consistent Form Styling** ✅
   - Same input/textarea/select styles
   - Unified validation display
   - Consistent error messages

5. **Modal System** ✅
   - Use modals for all interactions
   - Standard modal sizes (sm, md, lg, xl)
   - Consistent close buttons

### Long-term Improvements:

1. **Component Library**
   - Create reusable components
   - Document each component
   - Create style guide page

2. **Dark Mode**
   - Add theme switcher
   - Create dark theme variables
   - Save user preference

3. **Loading States**
   - Skeleton screens
   - Progress indicators
   - Loading animations

4. **Empty States**
   - No results found
   - No history yet
   - No documents uploaded

5. **Error States**
   - 404 page
   - 500 error page
   - Network error handling

---

## 📊 Success Metrics

- **Consistency Score**: 95%+ (same patterns used across pages)
- **Accessibility Score**: 90%+ (Lighthouse audit)
- **Performance Score**: 90%+ (Lighthouse audit)
- **Mobile Usability**: 100% (Google Mobile-Friendly Test)
- **User Task Success**: 95%+ (Can complete tasks without help)

---

## 🚀 Next Steps

1. Review and approve this design system
2. Create shared CSS component file
3. Update all pages systematically
4. Test on all devices/browsers
5. Gather user feedback
6. Iterate and improve

---

This design system will ensure a professional, consistent, and user-friendly experience across all pages of Sentino AI!







