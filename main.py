import sys
import os
import logging

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
    from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
    from PyQt6.QtGui import QIcon
    from PyQt6.QtCore import Qt, QSettings, QtMsgType, qInstallMessageHandler
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

def qt_message_handler(mode, context, message):
    """Leitet interne Qt-Fehlermeldungen an das Python-Logging-System weiter."""
    logger = logging.getLogger("qt")
    if mode == QtMsgType.QtDebugMsg:
        logger.debug(message)
    elif mode == QtMsgType.QtInfoMsg:
        logger.info(message)
    elif mode == QtMsgType.QtWarningMsg:
        logger.warning(message)
    elif mode == QtMsgType.QtCriticalMsg:
        logger.error(message)
    elif mode == QtMsgType.QtFatalMsg:
        logger.critical(message)

def show_i18n_warning(locale, error):
    """Displays a warning dialog if the translation system fails to load a language."""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Translation Error")
    msg.setText(f"Could not load translations for language: '{locale}'")
    msg.setInformativeText(f"The application will continue using default English strings.\n\nDetails: {error}")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    # Using exec() to block until user acknowledges, ensuring they see the error during startup.
    msg.exec()

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
    
    # Installiere den Handler für Qt-interne Meldungen (wie libpng Warnungen)
    qInstallMessageHandler(qt_message_handler)

    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Set App Icon (Global)
    icon_path = os.path.join(project_root, "assets/logo", "app_logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # --- Project Selection Logic ---
    # Initialize translations with a default locale first.
    # This ensures the _() function is available for any components (like ConfigManager
    # or ProjectLauncher) that might use it during their initialization.
    try:
        # A default language (e.g., 'en') is used initially.
        # The actual configured language will be set after loading app_config.
        i18n_init(app_root=project_root, locale='en')
    except Exception as e:
        # Fallback: Ensure _() exists globally even if init fails to prevent crashes
        import builtins
        builtins._ = lambda s: s
        show_i18n_warning('en', e)

    app_config_file = os.path.join(project_root, "app_config.yaml")
    recent_projects = []
    auto_open = True
    
    config_manager = ConfigManager(app_config_file)
    app_config = config_manager.load()
    recent_projects = app_config.get("recent_projects", [])
    auto_open = app_config.get("auto_open_last_project", True)
    locales_path = app_config.get("paths", {}).get("locales", "locales")

    # Check if Shift is pressed (to force launcher)
    # Re-initialize translations with the configured language if it's different from the initial default.
    configured_language = app_config.get('language')
    if configured_language and configured_language != 'en': # 'en' was our initial default
        # Pfad auflösen (relativ zu project_root/app_root)
        abs_locales = locales_path if os.path.isabs(locales_path) else os.path.join(project_root, locales_path)
        try:
            i18n_init(app_root=project_root, locale=configured_language, locales_dir=abs_locales)
        except Exception as e:
            show_i18n_warning(configured_language, e)
    modifiers = app.queryKeyboardModifiers()
    force_launcher = (modifiers & Qt.KeyboardModifier.ShiftModifier)
    
    selected_project = None

    # Try to open the last project if Shift is not pressed
    if recent_projects and isinstance(recent_projects, list) and not force_launcher and auto_open:
        path = recent_projects[0]
        # Portabler Check: Pfad relativ auflösen, falls er nicht absolut ist
        abs_path = path if os.path.isabs(path) else os.path.join(project_root, path)
        if os.path.exists(abs_path) and os.path.isdir(abs_path):
            selected_project = abs_path

    # If no project was chosen automatically, show launcher
    if not selected_project:
        launcher = ProjectLauncher(project_root)
        if launcher.exec() == QDialog.DialogCode.Accepted:
            selected_project = launcher.selected_project
        else:
            sys.exit(0)

    if selected_project:
        # Prepare project environment: set path for imports and CWD
        from core.logging import configure_logger
        # Jetzt, wo das Projekt bekannt ist, Log-Ausgabe für Qt-Meldungen in worker.log aktivieren
        configure_logger("qt", selected_project)
        
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