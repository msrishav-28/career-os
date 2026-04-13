# Contributing to CareerOS

![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)

Thank you for your interest in contributing to CareerOS. This document provides guidelines for contributions to ensure quality and consistency.

## Code of Conduct

All contributors are expected to adhere to professional standards. Be respectful, inclusive, and constructive in all interactions.

## Getting Started

1.  **Fork the repository**
2.  **Clone your fork**
    ```bash
    git clone https://github.com/YOUR_USERNAME/career-os.git
    cd career-os
    ```
3.  **Set up development environment** (see [GETTING_STARTED.md](../GETTING_STARTED.md))

## Development Workflow

### 1. Create a Branch

Create a new branch for your feature or fix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch Naming Convention:**
*   `feature/`: New features
*   `fix/`: Bug fixes
*   `docs/`: Documentation updates
*   `refactor/`: Code restructuring
*   `test/`: Adding missing tests

### 2. Make Changes

*   Write clean, documented code.
*   Follow the existing code style (Black for Python, Prettier/ESLint for TypeScript).
*   Add unit tests for any new logic.
*   Update documentation if parameters or behavior changes.

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

**Types:**
*   `feat`: New feature
*   `fix`: Bug fix
*   `docs`: Documentation
*   `style`: Formatting
*   `refactor`: Code restructuring
*   `test`: Tests
*   `chore`: Maintenance

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Open a Pull Request on GitHub targeting the `main` branch.

## Code Style

### Python (Backend)

*   **Formatter**: Black
*   **Linter**: Flake8
*   **Style**: PEP 8
*   **Typing**: Strict type hints required for all function signatures.
*   **Docstrings**: All public functions and classes must have docstrings.

```python
def calculate_score(message: str, contact: Dict[str, Any]) -> int:
    """
    Calculate personalization score derived from message content.

    Args:
        message: The message text.
        contact: Contact information dictionary.

    Returns:
        Integer score from 0 to 100.
    """
    pass
```

### TypeScript (Frontend)

*   **Linter**: ESLint
*   **Style**: Functional components with hooks.
*   **Typing**: Strict interfaces for all props and state.

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

## Pull Request Guidelines

### PR Title

Use the conventional commit format:
`type: Description of change` (e.g., `feat: Add dark mode support`)

### PR Description

Please include:
*   **Summary**: What changes were made.
*   **Motivation**: Why these changes are necessary.
*   **Implementation**: How the changes work.
*   **Testing**: Verification steps performed.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
