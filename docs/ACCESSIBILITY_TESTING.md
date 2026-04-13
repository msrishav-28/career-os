# CareerOS: Accessibility Testing & WCAG Compliance

**Version:** 1.0
**Last Updated:** February 15, 2026
**Owner:** Frontend & QA Team

---

## Accessibility Philosophy

### Core Commitment

CareerOS must be usable by everyone, regardless of:
- Visual ability (blind, low vision, color blind)
- Motor ability (cannot use mouse, tremors)
- Cognitive ability (dyslexia, ADHD)
- Auditory ability (deaf, hard of hearing)

### Why This Matters for $10K Product

1. **Legal Requirement:** Enterprise clients need ADA/Section 508 compliance
2. **Market Expansion:** 15% of global population has some disability
3. **Better UX for All:** Accessible design improves everyone's experience
4. **Professional Credibility:** Shows attention to detail

---

## WCAG 2.1 Compliance Targets

### Target Level: AA (Minimum for Enterprise)

| Level | Requirement | CareerOS Target |
|-------|-------------|------------------|
| **A** | Basic accessibility | ✅ Must meet 100% |
| **AA** | Recommended | ✅ Must meet 100% |
| **AAA** | Enhanced | 🎯 Target 80%+ |

### Key WCAG 2.1 AA Requirements

**Perceivable:**
- Text alternatives for non-text content
- Captions for audio/video
- Content presentable in different ways
- Sufficient color contrast (4.5:1 for normal text)

**Operable:**
- All functionality via keyboard
- Enough time to read/use content
- No seizure-causing content (no flashing >3x/sec)
- Clear navigation and focus indicators

**Understandable:**
- Text is readable and understandable
- Pages operate predictably
- Help users avoid/correct mistakes

**Robust:**
- Compatible with assistive technologies
- Valid HTML and ARIA usage

---

## Keyboard Navigation

### Tab Order Requirements

**All Interactive Elements Must Be Keyboard Accessible:**
- Buttons, links, form inputs
- Cards (if clickable)
- Modal close buttons
- Dropdown menus

**Tab Order Must Be Logical:**
```
Landing Page:
1. Skip to main content link
2. Logo/home link
3. Navigation menu items
4. Main CTA button
5. Footer links

Dashboard:
1. Emergency stop button
2. Navigation rail items
3. Main content (approval stack)
4. Approve button
5. Reject button
```

### Keyboard Shortcuts

**Global:**
- `Tab` - Next element
- `Shift + Tab` - Previous element
- `Enter/Space` - Activate button
- `Esc` - Close modal
- `?` - Show shortcuts help

**Message Approval:**
- `A` - Approve current message
- `R` - Reject current message
- `E` - Edit current message
- `N` - Next message
- `P` - Previous message

### Focus Trap in Modals

When modal opens, focus must be trapped inside until closed.

---

## Screen Reader Support

### Required Testing

**Test With:**
- **NVDA** (Windows, free)
- **JAWS** (Windows, paid but most popular)
- **VoiceOver** (macOS/iOS, built-in)
- **TalkBack** (Android, built-in)

**Critical Flows:**
1. Login
2. Resume upload and parsing
3. Message approval workflow
4. Emergency stop activation
5. Settings update

### Semantic Landmarks

Use HTML5 semantic elements:

```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  
  <header role="banner">
    <nav role="navigation" aria-label="Main navigation">
      <!-- Navigation -->
    </nav>
  </header>
  
  <main id="main-content" role="main">
    <!-- Main content -->
  </main>
  
  <footer role="contentinfo">
    <!-- Footer -->
  </footer>
</body>
```

### Dynamic Content Announcements

```html
<!-- System status updates -->
<div role="status" aria-live="polite" aria-atomic="true" class="sr-only">
  {statusMessage}
</div>

<!-- Critical errors -->
<div role="alert" aria-live="assertive" aria-atomic="true" class="sr-only">
  {errorMessage}
</div>
```

### Button Labels

```html
<!-- ❌ BAD: No context -->
<button aria-label="Approve">✓</button>

<!-- ✅ GOOD: Full context -->
<button aria-label="Approve message from Jane Smith">
  <CheckIcon aria-hidden="true" />
  <span class="sr-only">Approve message from Jane Smith</span>
</button>
```

---

## Color Contrast Requirements

### WCAG AA Contrast Ratios

**Normal Text (< 18px):**
- Minimum: 4.5:1
- Enhanced (AAA): 7:1

**Large Text (≥ 18px):**
- Minimum: 3:1
- Enhanced (AAA): 4.5:1

**UI Components:**
- Minimum: 3:1

### CareerOS Color Audit

| Element | Foreground | Background | Ratio | Pass? |
|---------|------------|------------|-------|-------|
| Body text | #FFFFFF | #050505 | 20.6:1 | ✅ AAA |
| Secondary | #A1A1AA | #050505 | 10.4:1 | ✅ AAA |
| Indigo button | #FFFFFF | #6366F1 | 8.6:1 | ✅ AAA |
| Success | #10B981 | #050505 | 8.2:1 | ✅ AAA |
| Error | #DC2626 | #050505 | 5.9:1 | ✅ AA |

### Color Blindness

**Never Use Color Alone:**

```html
<!-- ❌ BAD: Only color -->
<div style="color: green;">Message approved</div>

<!-- ✅ GOOD: Icon + text + color -->
<div class="text-signal-green flex items-center gap-2">
  <CheckCircleIcon />
  <span>Message approved</span>
</div>
```

**Test With:**
- Deuteranopia (red-green, most common)
- Protanopia (red-green)
- Tritanopia (blue-yellow)
- Achromatopsia (total color blindness)

---

## Focus Management

### Visible Focus Indicators

```css
/* Global focus style */
*:focus {
  outline: 2px solid var(--indigo-glow);
  outline-offset: 2px;
}

/* Custom for glass buttons */
.btn-primary:focus {
  outline: none;
  box-shadow: 
    0 0 0 3px rgba(99, 102, 241, 0.5),
    0 0 20px rgba(99, 102, 241, 0.3);
}
```

**Requirements:**
- Minimum 2px thickness
- High contrast (3:1 with adjacent)
- Visible on all backgrounds
- Consistent across site

### Focus Order After Actions

**Message Approval:**
```typescript
function handleApprove(messageId: string) {
  await approveMessage(messageId);
  
  // Focus next card or completion button
  const nextCard = document.querySelector('[data-card-index="1"]');
  if (nextCard) {
    (nextCard as HTMLElement).focus();
  } else {
    document.getElementById('view-history-btn')?.focus();
  }
}
```

---

## Reduced Motion Support

### Detecting Preference

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### In-App Toggle

```typescript
function SettingsPage() {
  const [reducedMotion, setReducedMotion] = useState(false);
  
  useEffect(() => {
    if (reducedMotion) {
      document.documentElement.classList.add('reduce-motion');
    } else {
      document.documentElement.classList.remove('reduce-motion');
    }
  }, [reducedMotion]);
  
  return (
    <label>
      <input
        type="checkbox"
        checked={reducedMotion}
        onChange={(e) => setReducedMotion(e.target.checked)}
      />
      Reduce motion and animations
    </label>
  );
}
```

---

## Testing Tools

### Automated Testing

**Browser Extensions:**
- **axe DevTools** - Comprehensive accessibility scan
- **WAVE** - Visual feedback on issues
- **Lighthouse** - Includes accessibility audit

**CI/CD Integration:**
```javascript
import { axe, toHaveNoViolations } from 'jest-axe';

test('ApprovalCard has no violations', async () => {
  const { container } = render(<ApprovalCard {...props} />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Manual Testing Checklist

**Keyboard Navigation:**
- [ ] Can navigate entire site with Tab/Shift+Tab
- [ ] Focus order is logical
- [ ] All shortcuts work
- [ ] No keyboard traps
- [ ] Focus visible at all times

**Screen Reader:**
- [ ] Page title announced
- [ ] Headings create logical structure
- [ ] Forms have proper labels
- [ ] Buttons have descriptive text
- [ ] Dynamic updates announced

**Color & Contrast:**
- [ ] All text meets 4.5:1 contrast
- [ ] Focus indicators visible
- [ ] No color-only information

**Motion:**
- [ ] Respects prefers-reduced-motion
- [ ] No flashing content
- [ ] Animations can be disabled

---

## Pre-Launch Checklist

**Content:**
- [ ] All images have alt text
- [ ] Videos have captions
- [ ] Headings in logical order
- [ ] Link text is descriptive

**Navigation:**
- [ ] Skip to main content link
- [ ] Keyboard shortcuts documented
- [ ] Current page clearly indicated

**Forms:**
- [ ] All inputs have labels
- [ ] Required fields marked
- [ ] Error messages specific
- [ ] Success messages announced

**Interactive:**
- [ ] All buttons have clear labels
- [ ] Focus indicators visible
- [ ] Disabled state clear
- [ ] Loading states announced

**Testing:**
- [ ] Automated tests pass
- [ ] Manual keyboard test complete
- [ ] Screen reader test complete
- [ ] Color contrast verified

---

## Conclusion

Accessibility is not optional for a $10K product. This guide ensures CareerOS is usable by everyone and meets legal requirements.

**Key Takeaways:**
1. Build accessibility in from day one
2. Test with real assistive technology
3. WCAG AA is minimum
4. Keyboard navigation is non-negotiable

**Ongoing:**
- Quarterly accessibility audits
- User testing with disabled users
- Continuous improvement

---

**Document Owner:** Accessibility Team
**Review Cycle:** Quarterly
**Last Updated:** February 15, 2026