# CONTRIBUTING

Thank you for your interest in contributing to urban-garbanzo!

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/urban-garbanzo.git
   cd urban-garbanzo
   ```

3. **Set up your development environment**:
   ```bash
   make install-dev
   make env
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Before you code

- **Check existing issues** to avoid duplicate work
- **Discuss major features** by opening an issue first

### While you code

1. **Write tests** for your changes
2. **Keep commits atomic** - one logical change per commit
3. **Follow the code style** - we use black, ruff, and mypy

### Code Quality Checks

```bash
# Run all checks
make lint
make typecheck
make test

# Auto-format code
make format

# Run pre-commit hooks
make precommit
```

## Before You Submit

1. **Update tests** - add tests for new functionality
2. **Run the full test suite**:
   ```bash
   make test
   ```

3. **Check coverage** - aim for >80% coverage for new code

4. **Update documentation** if needed (README, docstrings)

5. **Commit with clear messages**:
   ```
   Add feature: brief description

   - More detailed explanation if needed
   - Mention any related issues (#123)
   ```

## Submitting a Pull Request

1. Push your branch to your fork
2. Open a Pull Request to the `main` branch
3. Provide a clear description of the changes
4. Link any related issues using `#issue_number`
5. Be responsive to review feedback

## Code Style Guidelines

### Python Style

- **Line length**: 100 characters (enforced by black)
- **Imports**: Organized and sorted (enforced by ruff)
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

### Example

```python
def evaluate_prompt(prompt: str, criteria: list[str]) -> dict[str, float]:
    """Evaluate a prompt across multiple dimensions.

    Args:
        prompt: The prompt text to evaluate
        criteria: List of evaluation criteria

    Returns:
        Dictionary mapping criteria to scores (0-1)
    """
    # implementation
    pass
```

## Testing

- Write tests for all new features
- Use pytest fixtures for setup/teardown
- Use `pytest-asyncio` for async code
- Aim for >80% code coverage

```python
@pytest.mark.asyncio
async def test_evaluate_prompt():
    """Test prompt evaluation."""
    result = await evaluate_prompt("test prompt", ["clarity"])
    assert "clarity" in result
    assert 0 <= result["clarity"] <= 1
```

## Questions?

- Open an issue for questions or discussions
- Check the README and existing documentation
- Join our community discussions

Thank you for contributing! 🎉
