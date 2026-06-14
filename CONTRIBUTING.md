# Contributing to Data Quality Platform

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## 🎯 How to Contribute

### 1. Report Issues
- Check existing issues before creating a new one
- Provide clear, descriptive titles
- Include steps to reproduce the issue
- Attach relevant logs or screenshots

### 2. Submit Pull Requests

#### Prerequisites
- Fork the repository
- Clone your fork locally
- Create a feature branch: `git checkout -b feature/your-feature-name`

#### Commit Message Format
```
feat: add new feature
fix: resolve issue
docs: update documentation
refactor: improve code structure
test: add/update tests
chore: maintenance tasks
```

#### Code Quality Standards
- Follow PEP 8 style guidelines (Python)
- Follow standard JavaScript/React conventions (Frontend)
- Add type hints where applicable
- Include docstrings for functions and classes
- Write tests for new functionality
- Ensure all tests pass

#### Pull Request Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary dependencies added

### 3. Development Setup

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest black flake8

# Frontend setup
cd frontend
npm install

# Run tests
pytest
```

## 📋 Code Style

### Python
- 4 spaces for indentation
- Maximum line length: 88 characters
- Use type hints
- Google-style docstrings

### JavaScript/React
- Use ESLint configuration from project
- Prettier formatting (2 spaces)
- Follow React best practices
- Functional components preferred

## 🚀 Development Workflow

1. Create feature branch from `main`
2. Make focused, atomic commits
3. Write tests for new features
4. Update documentation
5. Submit pull request with clear description
6. Address review feedback
7. Merge upon approval

---

**Thank you for contributing! 🙌**