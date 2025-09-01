# Contributing to FluteN

Thank you for your interest in contributing to FluteN! We appreciate your time and effort in making this project better.

## How to Contribute

1. **Fork** the repository on GitHub
2. **Clone** the project to your own machine
3. **Commit** changes to your own branch
4. **Push** your work back up to your fork
5. Submit a **Pull Request** so we can review your changes

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use 4 spaces for indentation
- Keep lines under 100 characters
- Write docstrings for all public functions and classes
- Add comments to explain complex logic

## Reporting Issues

When reporting issues, please include:
- A clear title and description
- Steps to reproduce the issue
- Expected vs actual behavior
- Any relevant error messages or screenshots
- Your system information (OS, Python version, etc.)

## Development Setup

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Run tests:
   ```bash
   python -m pytest
   ```

## Pull Request Guidelines

- Keep PRs focused on a single feature or bug fix
- Update the documentation as needed
- Add tests for new features
- Ensure all tests pass before submitting
- Write a clear PR description

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
