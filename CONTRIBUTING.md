# Contributing to CareerOS

Thank you for your interest in contributing to CareerOS! This document provides guidelines for contributions.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/career-os.git
   cd career-os
   ```
3. **Set up development environment** (see GETTING_STARTED.md)

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test additions

### 2. Make Changes

- Write clean, documented code
- Follow existing code style
- Add tests for new features
- Update documentation

### 3. Test Your Changes

**Backend:**
```bash
cd backend
pytest tests/ -v
black --check .
flake8 .
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run build
```

### 4. Commit Changes

Use conventional commits:

```bash
git commit -m "feat: add new outreach template"
git commit -m "fix: resolve rate limiting bug"
git commit -m "docs: update API documentation"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python (Backend)

- Use Black for formatting
- Follow PEP 8
- Type hints encouraged
- Docstrings for all functions

```python
def calculate_score(message: str, contact: Dict) -> int:
    """
    Calculate personalization score.
    
    Args:
        message: The message text
        contact: Contact information
    
    Returns:
        Score from 0-100
    """
    pass
```

### TypeScript (Frontend)

- Use ESLint
- Functional components with hooks
- Type everything
- Document complex logic

```typescript
interface Contact {
  id: string;
  name: string;
  company?: string;
}

function ContactCard({ contact }: { contact: Contact }) {
  // Component logic
}
```

## Testing

### Backend Tests

```python
# tests/test_feature.py
import pytest

def test_feature():
    result = my_function()
    assert result == expected
```

Run tests:
```bash
pytest tests/ -v --cov
```

### Frontend Tests

```typescript
// __tests__/component.test.tsx
import { render, screen } from '@testing/library/react';

test('renders component', () => {
  render(<Component />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

## Documentation

- Update README.md if adding features
- Document API changes in docs/API.md
- Add JSDoc/docstrings
- Update GETTING_STARTED.md if setup changes

## Pull Request Guidelines

### PR Title

Use conventional commit format:
```
feat: Add dark mode support
fix: Resolve authentication bug
docs: Update deployment guide
```

### PR Description

Include:
- **What** - What changes were made
- **Why** - Why these changes are needed
- **How** - How the changes work
- **Testing** - How you tested
- **Screenshots** - For UI changes

Template:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Manual testing completed

## Screenshots (if applicable)
```

### Review Process

1. Automated tests must pass
2. Code review by maintainer
3. Address feedback
4. Approval and merge

## Areas for Contribution

### High Priority
- [ ] Additional agent tools (Twitter, HackerNews)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboards
- [ ] More outreach templates
- [ ] Integration tests

### Medium Priority
- [ ] UI/UX improvements
- [ ] Performance optimizations
- [ ] Documentation improvements
- [ ] Example use cases
- [ ] Video tutorials

### Good First Issues

Look for issues tagged `good-first-issue`:
- Documentation updates
- Simple bug fixes
- Test additions
- UI polish

## Development Tips

### Hot Reload

**Backend:**
```bash
uvicorn api.main:app --reload
```

**Frontend:**
```bash
npm run dev
```

### Debugging

**Backend:**
```python
import pdb; pdb.set_trace()
```

**Frontend:**
```typescript
console.log('Debug:', variable);
debugger;
```

### Database Changes

1. Update models in `backend/models/`
2. Create migration SQL
3. Test locally
4. Document in PR

## Getting Help

- **Questions:** GitHub Discussions
- **Bugs:** GitHub Issues
- **Chat:** Discord (link in README)
- **Email:** dev@careeros.dev

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Every contribution helps make CareerOS better for everyone. Thank you for your time and effort! 🎉
