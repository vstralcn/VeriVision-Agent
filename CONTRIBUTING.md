# Contributing to Deepfake Detection Platform

Thank you for your interest in contributing to the Deepfake Detection Platform! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Git
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+
- Basic knowledge of FastAPI and Vue.js

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/deepfake-detection-platform.git
cd deepfake-detection-platform
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/deepfake-detection-platform.git
```

## 💻 Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run database
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Using Development Scripts

```bash
# Start all services
./dev.sh start

# View logs
./dev.sh logs

# Open backend shell
./dev.sh shell

# Run tests
./dev.sh test-backend
```

## 🎯 How to Contribute

### Types of Contributions

1. **Bug Reports**
   - Use GitHub Issues
   - Include detailed description
   - Provide steps to reproduce
   - Include screenshots if applicable

2. **Feature Requests**
   - Use GitHub Issues
   - Describe the feature clearly
   - Explain the use case
   - Discuss potential implementation

3. **Code Contributions**
   - Bug fixes
   - New features
   - Performance improvements
   - Documentation updates

4. **Documentation**
   - Fix typos
   - Improve clarity
   - Add examples
   - Translate documentation

### Finding Issues to Work On

- Look for issues labeled `good first issue`
- Check issues labeled `help wanted`
- Review the project roadmap

## 📝 Coding Standards

### Python (Backend)

#### Style Guide

Follow PEP 8 style guide:

```python
# Good
def detect_image(image_path: str, user_id: int) -> Detection:
    """
    Perform deepfake detection on an image.
    
    Args:
        image_path: Path to the image file
        user_id: ID of the user performing detection
        
    Returns:
        Detection object with results
    """
    pass

# Bad
def detectImage(imagePath,userId):
    pass
```

#### Type Hints

Always use type hints:

```python
from typing import List, Optional

def get_users(skip: int = 0, limit: int = 10) -> List[User]:
    pass

def find_user(user_id: int) -> Optional[User]:
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int) -> dict:
    """
    Brief description of the function.
    
    Longer description if needed, explaining the purpose
    and behavior of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Dictionary containing the results
        
    Raises:
        ValueError: If param2 is negative
    """
    pass
```

#### Code Organization

```python
# Imports order:
# 1. Standard library
# 2. Third-party packages
# 3. Local application imports

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.models import User
from app.core.database import get_db
```

### JavaScript/Vue (Frontend)

#### Style Guide

Follow Vue.js style guide:

```vue
<!-- Good -->
<template>
  <div class="component-name">
    <h1>{{ title }}</h1>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const title = ref('Hello')
const uppercaseTitle = computed(() => title.value.toUpperCase())
</script>

<style scoped>
.component-name {
  padding: 20px;
}
</style>
```

#### Naming Conventions

```javascript
// Components: PascalCase
import UserProfile from '@/components/UserProfile.vue'

// Variables and functions: camelCase
const userName = ref('')
const fetchUserData = async () => {}

// Constants: UPPER_SNAKE_CASE
const API_BASE_URL = 'http://localhost:8000'

// Files: kebab-case
// user-profile.vue
// detection-service.js
```

#### Composition API

Prefer Composition API over Options API:

```vue
<script setup>
import { ref, onMounted } from 'vue'

// Good
const count = ref(0)
const increment = () => count.value++

onMounted(() => {
  console.log('Component mounted')
})
</script>
```

### Database

#### Migrations

Always create migrations for schema changes:

```bash
# Create migration
alembic revision --autogenerate -m "Add user avatar field"

# Review the generated migration
# Edit if necessary

# Apply migration
alembic upgrade head
```

#### Model Naming

```python
# Table names: plural, snake_case
class User(Base):
    __tablename__ = "users"

# Column names: snake_case
class Detection(Base):
    __tablename__ = "detections"
    
    created_at = Column(DateTime)
    is_fake = Column(Boolean)
    fake_probability = Column(Float)
```

## 🧪 Testing Guidelines

### Backend Tests

Create tests in `backend/tests/`:

```python
# tests/test_detection.py
import pytest
from fastapi.testclient import TestClient

def test_upload_image(client: TestClient, auth_headers: dict):
    """Test image upload and detection."""
    with open("test_image.jpg", "rb") as f:
        response = client.post(
            "/api/detection/upload",
            headers=auth_headers,
            files={"file": f}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "is_fake" in data
    assert "confidence" in data
```

### Frontend Tests

Create tests in `frontend/tests/`:

```javascript
// tests/components/Detection.spec.js
import { mount } from '@vue/test-utils'
import Detection from '@/views/user/Detection.vue'

describe('Detection Component', () => {
  it('renders upload area', () => {
    const wrapper = mount(Detection)
    expect(wrapper.find('.upload-demo').exists()).toBe(true)
  })
})
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test

# All tests
./dev.sh test-backend
```

## 📝 Commit Guidelines

### Commit Message Format

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Examples

```bash
# Feature
git commit -m "feat(detection): add batch processing support"

# Bug fix
git commit -m "fix(auth): resolve token expiration issue"

# Documentation
git commit -m "docs(api): update authentication examples"

# Breaking change
git commit -m "feat(api): change detection response format

BREAKING CHANGE: Detection response now includes additional metadata field"
```

### Commit Best Practices

- Write clear, concise commit messages
- Keep commits focused and atomic
- Reference issues when applicable: `fixes #123`
- Don't commit sensitive data
- Test before committing

## 🔄 Pull Request Process

### Before Submitting

1. **Update your fork**
```bash
git fetch upstream
git checkout main
git merge upstream/main
```

2. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes**
   - Follow coding standards
   - Add tests
   - Update documentation

4. **Test your changes**
```bash
./dev.sh test-backend
cd frontend && npm run test
```

5. **Commit your changes**
```bash
git add .
git commit -m "feat: add your feature"
```

6. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

### Submitting Pull Request

1. Go to GitHub and create a Pull Request
2. Fill out the PR template completely
3. Link related issues
4. Request review from maintainers

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added
- [ ] All tests pass

## Screenshots (if applicable)

## Related Issues
Fixes #123
```

### Review Process

1. Maintainers will review your PR
2. Address any feedback
3. Make requested changes
4. Push updates to your branch
5. PR will be merged when approved

### After Merge

1. Delete your feature branch
2. Update your local main branch
3. Celebrate! 🎉

## 🐛 Bug Report Template

```markdown
**Describe the bug**
A clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable

**Environment:**
- OS: [e.g., Ubuntu 20.04]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Additional context**
Any other relevant information
```

## 💡 Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem

**Describe the solution you'd like**
A clear description of what you want to happen

**Describe alternatives you've considered**
Alternative solutions or features

**Additional context**
Any other context or screenshots
```

## 📚 Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [Element Plus Documentation](https://element-plus.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Learning Resources
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Vue Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

## 📞 Getting Help

- GitHub Issues: For bugs and features
- GitHub Discussions: For questions and ideas
- Email: [project-email@example.com]

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to the Deepfake Detection Platform!** 🚀
