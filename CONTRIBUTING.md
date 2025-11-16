# 🤝 Contributing to Dark War Survival Bot

Thank you for your interest in contributing to the Dark War Survival Bot project! This guide will help you get started with contributing to this automation solution.

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Contributing Guidelines](#contributing-guidelines)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Pull Request Process](#pull-request-process)
7. [Issue Reporting](#issue-reporting)

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Git
- Dark War Survival (Phone or BlueStacks)
- Understanding of automation concepts

### Areas for Contribution
- 🐛 **Bug Fixes**: Resolve issues and improve stability
- ✨ **New Features**: Add automation capabilities
- 📚 **Documentation**: Improve guides and help content
- ⚡ **Performance**: Optimize speed and efficiency
- 🎨 **UI/UX**: Enhance the control center interface
- 🧪 **Testing**: Add test coverage and validation

## 💻 Development Setup

### 1. Fork and Clone
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/yourusername/dark-war-automation-bot.git
cd dark-war-automation-bot
```

### 2. Set Up Environment
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run installation script
python install.py
```

### 3. Test Your Setup
```bash
# Test the control center
python bot_control_center.py

# Test window detection
python find_phone_window.py  # For phone mode
python main.py --detect-window  # For BlueStacks mode
```

## 📝 Contributing Guidelines

### Types of Contributions

#### 🐛 Bug Fixes
- Fix automation issues
- Resolve performance problems
- Handle error conditions
- Improve stability

#### ✨ New Features
- Add new automation tasks
- Implement new game modes
- Create additional tools
- Enhance existing functionality

#### 📚 Documentation
- Update setup guides
- Add troubleshooting content
- Create video tutorials
- Improve code comments

#### ⚡ Performance
- Optimize click speeds
- Reduce resource usage
- Improve template matching
- Enhance system integration

### Contribution Workflow

1. **Check Existing Issues**: Look for related issues or discussions
2. **Create Issue**: For new features or major changes
3. **Fork Repository**: Create your own copy
4. **Create Branch**: Use descriptive branch names
5. **Make Changes**: Follow code standards
6. **Test Thoroughly**: Verify on both phone and BlueStacks
7. **Submit Pull Request**: With detailed description

## 🎯 Code Standards

### Python Code Style
- Follow **PEP 8** formatting guidelines
- Use **meaningful variable names**
- Add **docstrings** to functions and classes
- Include **type hints** where appropriate
- Keep functions **focused and small**

#### Example:
```python
def find_window(window_title: str) -> Optional[gw.Win32Window]:
    """
    Find a window by title.

    Args:
        window_title: The title of the window to find

    Returns:
        Window object if found, None otherwise
    """
    try:
        windows = gw.getWindowsWithTitle(window_title)
        return windows[0] if windows else None
    except Exception as e:
        logger.error(f"Error finding window: {e}")
        return None
```

### File Organization
- **Single Responsibility**: One class/function per purpose
- **Clear Naming**: Descriptive file and variable names
- **Logical Structure**: Group related functionality
- **Import Organization**: Standard library, third-party, local imports

### Configuration
- **Centralized Config**: Use `config.py` and JSON files
- **Default Values**: Always provide sensible defaults
- **Validation**: Check configuration validity
- **Documentation**: Document all config options

### Error Handling
- **Graceful Failures**: Handle errors without crashing
- **Informative Messages**: Clear error descriptions
- **Logging**: Use proper logging levels
- **Recovery**: Attempt to recover from errors

### GUI Development
- **Consistent Design**: Follow established UI patterns
- **Responsive Layout**: Handle window resizing
- **User Feedback**: Clear status messages
- **Accessibility**: Consider ease of use

## 🧪 Testing

### Test Categories

#### Unit Tests
- Individual function testing
- Configuration validation
- Error handling verification
- Edge case coverage

#### Integration Tests
- Full automation workflows
- Window detection accuracy
- Template matching reliability
- Performance benchmarks

#### User Acceptance Tests
- End-to-end automation
- GUI functionality
- Setup process validation
- Documentation accuracy

### Test Requirements
- **Both Modes**: Test phone and BlueStacks modes
- **Error Scenarios**: Test failure conditions
- **Performance**: Verify speed improvements
- **Safety**: Confirm emergency stops work

### Running Tests
```bash
# Run unit tests
python -m pytest tests/

# Test specific components
python test_window_manager.py
python test_template_matcher.py

# Performance testing
python performance_optimizer.py --test
```

## 📬 Pull Request Process

### Before Submitting
1. **Update Documentation**: Modify README.md if needed
2. **Test Thoroughly**: Ensure all functionality works
3. **Check Code Style**: Follow formatting guidelines
4. **Update Dependencies**: Add any new requirements
5. **Write Tests**: Include test coverage for new features

### Pull Request Template
```markdown
## Description
Brief description of changes and motivation

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix/feature causing existing functionality to not work)
- [ ] Documentation update

## Testing
- [ ] Tested on phone mode
- [ ] Tested on BlueStacks mode
- [ ] Added/updated unit tests
- [ ] Performance impact assessed

## Screenshots
Include screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

### Review Process
1. **Automated Checks**: CI/CD pipeline validation
2. **Peer Review**: Code review by maintainers
3. **Testing**: Functionality verification
4. **Documentation**: Guide accuracy check
5. **Approval**: Final approval and merge

## 🐛 Issue Reporting

### Bug Reports
When reporting bugs, include:
- **Environment**: OS, Python version, game mode
- **Steps to Reproduce**: Detailed reproduction steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots**: Visual evidence if applicable
- **Logs**: Relevant log file contents

#### Bug Report Template
```markdown
**Environment**
- OS: [e.g., Windows 10]
- Python Version: [e.g., 3.9.0]
- Game Mode: [Phone/BlueStacks]
- Bot Version: [e.g., v1.2.0]

**Steps to Reproduce**
1. Launch bot control center
2. Select phone mode
3. Click start bot
4. Error occurs

**Expected Behavior**
Bot should start automation

**Actual Behavior**
Error message: "Window not found"

**Screenshots**
[Attach screenshots]

**Additional Context**
[Any other relevant information]
```

### Feature Requests
For feature requests, provide:
- **Feature Description**: Clear explanation of desired functionality
- **Use Case**: Why this feature would be useful
- **Implementation Ideas**: Suggested approach (optional)
- **Alternative Solutions**: Other approaches considered

## 🏆 Recognition

### Contributors
All contributors will be recognized in:
- **README.md**: Contributors section
- **Release Notes**: Major contribution acknowledgments
- **GitHub**: Contributor graphs and statistics

### Types of Contributions Recognized
- Code contributions
- Documentation improvements
- Bug reports and testing
- Feature suggestions
- Community support

## 📞 Getting Help

### Channels for Support
- **GitHub Issues**: Technical problems and bugs
- **GitHub Discussions**: Feature ideas and questions
- **Documentation**: Comprehensive guides and tutorials
- **Code Comments**: Inline documentation and examples

### Response Times
- **Bug Reports**: 1-3 days
- **Feature Requests**: 3-7 days
- **Pull Reviews**: 2-5 days
- **Documentation Updates**: 1-2 days

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

**🤖 Thank you for contributing to the Dark War Survival Bot project! Together, we're building the ultimate automation solution!**