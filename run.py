import sys
import os

from core import APP_NAME, APP_VERSION

'''
This script is the entry point for the Sitewave application. It initializes the PyQt6 application, 
displays the project launcher (if no project is opened automatically), and starts the main application window.

It also includes workarounds for known Linux rendering issues with GBM/NVIDIA and ensures that modules can be imported correctly, 
regardless of whether the application is run as a script or as a PyInstaller bundle.

The main logic for project selection, initialization of translations and the logger, 
as well as handling of Windows taskbar icons, is organized in the main() function, 
which is called when the application starts.

'''

# Workaround for Linux rendering issues (GBM/NVIDIA errors)
# Disables GPU acceleration for the web preview to avoid errors.
if sys.platform.startswith('linux'):
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox --disable-features=Vulkan"
    # Fix for "QRhiGles2: Failed to create temporary context" error
    os.environ["QT_X11_NO_MITSHM"] = "1"

# Ensure that we can import modules from the current directory
project_root = os.path.dirname(os.path.abspath(__file__))

def get_project_root():
    """Determines the root path, works for development and PyInstaller bundle."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle (as .exe)
        return sys._MEIPASS
    else:
        # Running in a normal development environment
        return os.path.dirname(os.path.abspath(__file__))

project_root = get_project_root()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from PyQt6.QtWidgets import QApplication, QDialog
    from PyQt6.QtGui import QIcon
    from PyQt6.QtCore import Qt, QSettings
except ImportError:
    print("Error: PyQt6 is not installed.")
    print("Please install it with: pip install PyQt6 PyQt6-WebEngine")
    sys.exit(1)

try:
    from gui.main_window import MainWindow
    from gui.dialogs.project_launcher import ProjectLauncher
    from core.config_manager import ConfigManager
except ImportError as e:
    print(f"Error loading app modules: {e}")
    print("Ensure that the 'gui' folder and the 'gui/__init__.py' file exist.")
    sys.exit(1)

from core.i18n import init as i18n_init
from workers.logger_config import configure_logger

def main():
    """
    Initializes the application, handles project selection, and starts the main window.
    """
    
    # Windows Taskbar Icon Fix: To ensure the icon is displayed separately and correctly in the taskbar
    if os.name == 'nt':
        import ctypes
        myappid = "Siteweave.App.1" # Any unique ID
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Initialize QApplication
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Set App Icon (Global)
    icon_path = os.path.join(project_root, "assets/logo", "app_logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # --- Project Selection Logic ---
    app_config_file = os.path.join(project_root, "app_config.yaml")
    recent_projects = []
    auto_open = True
    
    config_manager = ConfigManager(app_config_file)
    app_config = config_manager.load()
    recent_projects = app_config.get("recent_projects", [])
    auto_open = app_config.get("auto_open_last_project", True)

    # Initialize translations and app logger
    try:
        i18n_init(app_root=project_root, locale=app_config.get('language'))
    except Exception:
        pass

    try:
        configure_logger('tci-app', project_root)
    except Exception:
        pass
    
    # Check if Shift is pressed (to force launcher)
    modifiers = app.queryKeyboardModifiers()
    force_launcher = (modifiers & Qt.KeyboardModifier.ShiftModifier)
    
    selected_project = None

    # Try to open the last project if Shift is not pressed
    if recent_projects and isinstance(recent_projects, list) and not force_launcher and auto_open:
        last_project = recent_projects[0]
        if os.path.exists(last_project) and os.path.isdir(last_project):
            selected_project = last_project

    # If no project was chosen automatically, show launcher
    if not selected_project:
        launcher = ProjectLauncher(project_root)
        if launcher.exec() == QDialog.DialogCode.Accepted:
            selected_project = launcher.selected_project
        else:
            sys.exit(0)

    if selected_project:
        # Prepare project environment: set path for imports and CWD
        if selected_project not in sys.path:
            sys.path.insert(0, selected_project)
        
        # Change working directory so plugins can find relative paths
        if os.path.isdir(selected_project):
            os.chdir(selected_project)

        # Create and show the main window
        window = MainWindow(selected_project)
        window.show()

        # Start the event loop
        sys.exit(app.exec())

if __name__ == "__main__":
    main()