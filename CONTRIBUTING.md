# Contributing to Smart City AI Assistant

Thank you for considering contributing to this project! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs
- Use the GitHub Issues page
- Follow the bug report template
- Include detailed steps to reproduce
- Provide environment information

### Suggesting Features
- Use the GitHub Issues page
- Follow the feature request template
- Explain the use case and benefit
- Consider implementation complexity

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/AI-Agent.git
   cd AI-Agent
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Python tests
   cd python-agent
   pytest tests/
   
   # Frontend tests
   cd frontend
   npm test
   
   # Integration tests
   docker-compose -f infra/docker-compose.yml up
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   
   Use conventional commits:
   - `feat:` New features
   - `fix:` Bug fixes
   - `docs:` Documentation
   - `test:` Tests
   - `chore:` Maintenance

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a Pull Request on GitHub

## Development Setup

### Prerequisites
- Node.js 18+
- Python 3.9+
- Docker (optional)

### Local Development
```bash
# Install dependencies
npm install
cd frontend && npm install && cd ..
cd python-agent && pip install -r requirements.txt && cd ..

# Copy environment
cp .env.example .env

# Start services
npm run dev
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Add docstrings for public functions
- Maximum line length: 100 characters

### TypeScript
- Follow Next.js conventions
- Use functional components with hooks
- Add JSDoc comments for complex functions
- Use Prettier for formatting

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## Testing Guidelines

### Python Tests
- Write unit tests for all new functions
- Use pytest fixtures for common setup
- Mock external API calls
- Aim for >80% code coverage

### Frontend Tests
- Test components with React Testing Library
- Test API routes
- Test user interactions
- Test error states

## Documentation

- Update README.md for major changes
- Add JSDoc/docstrings for new functions
- Update API documentation
- Include examples where helpful

## Review Process

1. Automated tests must pass
2. Code review by maintainers
3. Address review feedback
4. Squash commits if requested
5. Merge after approval

## Questions?

- Open a GitHub Discussion
- Join our community chat
- Email maintainers

Thank you for contributing! 🎉
