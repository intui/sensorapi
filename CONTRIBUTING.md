# Contributing to SensorAPI

Thank you for your interest in contributing to SensorAPI! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment (see below)
4. Create a branch for your changes
5. Make your changes and test them
6. Submit a pull request

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps which reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain which behavior you expected to see instead
- Explain why this enhancement would be useful

### Your First Code Contribution

Unsure where to begin contributing? You can start by looking through `beginner` and `help-wanted` issues:

- **Beginner issues** - issues which should only require a few lines of code, and a test or two
- **Help wanted issues** - issues which should be a bit more involved than beginner issues

## Development Setup

### Prerequisites

- Python 3.9+ 
- Node.js 16+ (for frontend)
- PostgreSQL 12+
- Git

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/sensorapi.git
cd sensorapi

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your database configuration

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Database Setup

1. Create a PostgreSQL database
2. Update your `.env` file with the database connection details
3. Run migrations: `alembic upgrade head`

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_sensors.py

# Run integration tests
python run_tests.py
```

### Writing Tests

- Write tests for any new functionality
- Ensure all existing tests pass
- Aim for good test coverage
- Use descriptive test names
- Follow the existing test patterns

## Coding Standards

### Python Code Style

- Follow PEP 8
- Use Black for code formatting: `black .`
- Use isort for import sorting: `isort .`
- Use type hints where appropriate
- Write docstrings for functions and classes

### GraphQL Schema

- Use clear, descriptive names for types and fields
- Include descriptions for types and fields
- Follow GraphQL best practices for schema design

### Frontend Code Style

- Follow TypeScript/React best practices
- Use ESLint and Prettier for code formatting
- Write component tests using React Testing Library

### Documentation

- Keep the README up to date
- Document new features and API changes
- Use clear, concise language
- Include code examples where helpful

## Pull Request Process

1. **Create a branch**: Create a new branch from `main` for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**: Implement your changes following the coding standards

3. **Test your changes**: Ensure all tests pass and add new tests if needed

4. **Update documentation**: Update relevant documentation

5. **Commit your changes**: Use clear commit messages
   ```bash
   git commit -m "feat: add new sensor type validation"
   ```

6. **Push to your fork**: 
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Submit a pull request**: Create a pull request from your fork

### Pull Request Guidelines

- Use a clear title that describes the change
- Fill out the pull request template completely
- Link to any relevant issues
- Ensure all CI checks pass
- Keep changes focused and atomic
- Be responsive to feedback

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, a maintainer will merge your PR

## Questions?

If you have questions, feel free to:

- Open an issue with the `question` label
- Join our community discussions
- Reach out to maintainers

Thank you for contributing to SensorAPI! 🚀