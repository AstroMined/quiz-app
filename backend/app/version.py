"""Version information for the Quiz App."""

__version__ = "0.1.1"
__version_info__ = (0, 1, 1)

# Build information
PYTHON_VERSION = "3.12.10"
DEPENDENCY_MANAGER = "UV"

# Application metadata
APP_NAME = "Quiz App"
APP_DESCRIPTION = "A Python-based educational platform for creating, managing, and delivering interactive quizzes"

# Version utilities
def get_version() -> str:
    """Return the current version string."""
    return __version__

def get_version_info() -> tuple:
    """Return the version as a tuple of integers."""
    return __version_info__

def get_full_version() -> str:
    """Return full version information including Python version."""
    return f"{APP_NAME} v{__version__} (Python {PYTHON_VERSION})"