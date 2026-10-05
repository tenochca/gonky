"""App-wide constants: paths, version string, and default values."""

import pathlib

# ------------------------------------------------------------------
# Package identity
# ------------------------------------------------------------------
APP_NAME = "Gonky"
APP_ID = "io.github.gonky"
APP_VERSION = "0.1.0"

# ------------------------------------------------------------------
# Filesystem paths
# ------------------------------------------------------------------
_PACKAGE_DIR = pathlib.Path(__file__).parent
PROJECT_ROOT = _PACKAGE_DIR.parent.parent  # gonky/ workspace root

ASSETS_DIR = PROJECT_ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
STYLES_DIR = ASSETS_DIR / "styles"

APP_CSS_PATH = STYLES_DIR / "gonky.css"
APP_ICON_PATH = ICONS_DIR / "gonky.svg"

# User-facing file extensions
GONKY_PROJECT_EXTENSION = ".gonky"
CONKY_CONFIG_EXTENSION = ".conf"

# ------------------------------------------------------------------
# Default Conky global settings
# ------------------------------------------------------------------
DEFAULT_WINDOW_WIDTH = 200
DEFAULT_WINDOW_HEIGHT = 300
DEFAULT_WINDOW_X = 10
DEFAULT_WINDOW_Y = 10
DEFAULT_UPDATE_INTERVAL = 1.0  # seconds
