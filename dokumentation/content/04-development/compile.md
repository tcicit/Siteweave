---
author: TCI
breadcrumbs: true
date: '2025-01-01'
draft: false
featured_image: ''
layout: doc
release_date: '2026-01-15'
tags:
- Entwicklung
- Dokumentation
title: Compile
weight: 60
---

Compiling a Python application into a standalone application (also known as “freezing”) bundles your scripts, the Python interpreter, and all dependencies into a single executable package. The most common and robust tool for this is PyInstaller.

Here is a step-by-step guide on how to proceed:

### Step 1: Install PyInstaller

If you haven't already done so, install PyInstaller with pip:

```bash
pip install pyinstaller
```

### Step 2: Preparations

1. Icon format: PyInstaller requires a specific format for the application icon:

- Windows: .ico
- macOS: .icns
 
You will need to convert your assets/logo/app_logo.png to the appropriate format. There are free online tools available for this.

2. Important note about manage_translations.py: This script calls the command line tool pybabel with subprocess.check_call. This will fail in the compiled application because pybabel does not exist there as a standalone program.

You have two options for the compiled app:

Recommendation: Consider this script a pure developer tool and remove it from the build process (by removing it from the hiddenimports in the configuration file below).

Alternative (more complex): Rewrite the script so that it imports the babel library directly and uses its Python functions instead of calling an external command.

### Step 3: Create the build.spec file
The best way to compile a complex project like yours is to use a .spec file. This is the central “assembly instructions” for PyInstaller.

Create a new file called build.spec in the root directory of your project (/home/xyz/Documents/Development/Python/apps/tci-static-site/).

New file: **build.spec**


```
# -*- mode: python ; coding: utf-8 -*-

import os

# FIX: __file__ is not available in PyInstaller spec files.
# We use the current working directory instead.
project_root = os.path.abspath(os.getcwd())

block_cipher = None

a = Analysis(
    [‘run_editor.py’],
    pathex=[project_root],
    binaries=[],
    # All non-code files and directories required for the application are listed here.
    # Format: (‘source path’, ‘target folder in build’)
    # Format: (‘source path’, ‘target folder in build’)
    datas=[
        (‘assets’, ‘assets’),
        (‘locales’, ‘locales’),
        (‘workers’, ‘workers’),
        (‘plugins’, ‘plugins’),
        (‘project_templates’, ‘project_templates’),
        (‘app_config.yaml’, ‘.’),
        (‘babel.cfg’, ‘.’)
    ],
    hiddenimports=[
        ‘babel.localedata’,
        ‘pkg_resources.py2_warn’,
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [], # IMPORTANT: Empty list for binaries here
          exclude_binaries=True, # IMPORTANT: Prevents binaries from being packed into the EXE (for folder mode)
          name=‘tci-static-site-editor’,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False, # Important for GUI applications
          icon=os.path.join(project_root, ‘assets’, ‘logo’, ‘app_logo.png’) )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name=‘tci-static-site-editor’)
```

### Step 4: Start compilation
Open a terminal in the root directory of your project.

Execute the following commands:

```bash
# 1. Delete old build artifacts (important!)
rm -rf build dist

# 2. Recompile
pyinstaller build.spec
```

PyInstaller will now create two folders: build (for temporary files) and dist (for the result).

In the dist folder, you will find a subfolder named after your app (e.g., TCI-Static-Site-Editor). This folder contains the executable file and all necessary dependencies. You can share this entire folder.

### Step 5: Folder vs. single file mode
A folder (default): By default, the .spec file creates a folder with many files. This is the most robust and fastest to start.
A single file: If you prefer a single .exe file, you can easily customize the command:

```bash
pyinstaller --onefile build.spec
```

Note that this will cause the application to take a little longer to start, as all files must be unpacked into a temporary directory each time it is launched.
That's the whole process! The .spec file is the key to success, as it gives you full control over what is included in your final application.

## Basic structure of a .spec file
The file is divided into three main blocks, which are executed sequentially:

- Analysis: The “detective.” This block analyzes your scripts, finds all imports and dependencies, and decides which files need to be packaged.
- EXE: The “builder.” This block takes the results of the analysis and creates the actual executable file (.exe on Windows).
- COLLECT: The “packager.” This block collects the .exe file and all other necessary resources (images, DLLs, etc.) and places them in a final output folder.

### 1. The Analysis Block in Detail

This is the most important and complex part. Here you define everything that goes into your app.

```python
a = Analysis(
    [app_entry_point],  # -> [‘run_editor.py’]
    pathex=[‘.’],
    datas=[
        (‘assets’, ‘assets’),
        (‘locales’, ‘locales’),
        (‘project_templates’, ‘project_templates’),
    ],
    hiddenimports=[
        ‘PyQt6.sip’,
        ‘compress_images’,
        # ...
    ],
    # ...
)
```

- The [app_entry_point]: This is the list of main entry points for your application. PyInstaller starts its analysis here. For your app, this is run_editor.py, which starts QApplication.  
- pathex=[‘.’]: Tells PyInstaller which directories to search for modules in. [‘.’] means “Search in the current directory as well.” This is important so that your local imports such as from core.i18n import ... are found.
- datas=[ ... ]: One of the most important options for any app with resources. It copies non-code files or entire folders into the final application.
- Format: (‘source on your hard drive’, ‘target folder in the app’)
- Example: (‘assets’, ‘assets’) means: “Take the entire assets folder from my project and place it as a folder named assets in the main directory of the compiled app.”

Why is this necessary? Your app accesses images, templates, and translation files at runtime (os.path.join(‘assets’, ...)). Without datas, these files would be missing and the app would crash.

- hiddenimports=[ ... ]: The “lifeline” for modules that PyInstaller cannot find automatically.

Why is this necessary? PyInstaller analyzes the code statically. If a module is imported dynamically (e.g., based on a configuration file or, as in your case, by loading “app” scripts from a folder), PyInstaller does not see this import.

Examples in your app:

compress_images, site_renderer, etc.: These scripts are loaded dynamically as “tools.” We need to list them explicitly here.
PyQt6.QtWebEngineCore: Some PyQt modules are loaded internally in a way that PyInstaller may overlook. It is best practice to add them as hiddenimports to avoid runtime errors.

### 2. The EXE block in detail

This block configures the actual executable file.

``` python
exe = EXE(
    pyz,
    a.scripts,
    # ...
    name=app_name,
    console=False,
    icon=icon_path,)

```

- name=app_name: Sets the file name of the executable (e.g., TCI-Static-Site-Editor.exe).
- console=False: A crucial setting for GUI applications!

False (default for GUI): The application starts without an additional black command line window in the background. This is what you want for a professional-looking app.

- True: The application would always start with a console window. This is useful for debugging or for pure command line tools.
- icon=icon_path: Assigns your application icon to the .exe file. This is the icon that will be displayed in Windows Explorer, shortcuts, and the taskbar. It must be in the platform-specific format (.ico for Windows).

### 3. The COLLECT block in detail

This block brings everything together and creates the final folder that you pass on to your users.

```python
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    # ...
    name=app_name,)

```

- exe, a.binaries, a.zipfiles, a.datas: These lines instruct the packer to collect the created .exe file, all binary files found (such as DLLs), the packed Python modules (pyz), and your resource files (datas).
- name=app_name: Sets the name of the output folder that will be created in the dist directory. If app_name is set to TCI-Static-Site-Editor, your entire program will end up in the dist/TCI-Static-Site-Editor folder.

In summary, the .spec file is an explicit build instruction that gives you much more control than simple command line options and is essential for projects that are more complex than a single script.

## Optional single file app

You can achieve this with a single option, but there is an important adjustment in the code that is necessary for this.

Here are the complete instructions.


### Step 1: The command line option
To instruct PyInstaller to create a single .exe file instead of a folder, use the --onefile option.

The command for compiling therefore changes to:

```bash
pyinstaller --onefile build.spec
```

That's all there is to the command. PyInstaller will now pack everything into a single executable file in the dist folder.

### Step 2: The crucial code adjustment (path to resources)
The problem: When your app is launched as a single .exe file, it unpacks all the necessary resources (such as your assets, locales, and project_templates) into a temporary directory (e.g., under C:\Users\<user>\AppData\Local\Temp\_MEIxxxxxx). Your code, which assumes a fixed project_root, would no longer be able to find these files.

The solution: We need to adjust the starting point of your application (run_editor.py) so that it recognizes whether it is running in a compiled app and adjusts the path to the resources accordingly. PyInstaller provides a special variable sys._MEIPASS for this purpose.

Here is the necessary change for your run_editor.py:

**run_editor.py**

```
if sys.platform.startswith(‘linux’):
    os.environ[“QTWEBENGINE_CHROMIUM_FLAGS”] = “--disable-gpu --no-sandbox --disable-features=Vulkan”


# Ensure that we can import modules from the current directory


project_root = os.path.dirname(os.path.abspath(__file__))
def get_project_root():
    “”“Determines the root path, works for development and PyInstaller bundle.”“”
    if getattr(sys, ‘frozen’, False) and hasattr(sys, ‘_MEIPASS’):
        # Running in a PyInstaller bundle (as .exe)
        return sys._MEIPASS
    else:
        # Running in a normal development environment
        return os.path.dirname(os.path.abspath(__file__))

project_root = get_project_root()
if project_root not in sys.path:
    sys.path.insert(0, project_root)
```

What does this code do? The new function get_project_root checks whether the app is “frozen.”

If so, it returns the path to the temporary folder (sys._MEIPASS).
If not (you are running python run_editor.py), it returns the normal project folder.

By setting project_root to the result of this function, all your existing lines of code such as os.path.join(project_root, “assets”, ...) will automatically work both in development and in the compiled .exe file.

Summary of the procedure

- Modify code: Add the get_project_root function to your run_editor.py as shown in the diff above.
- Compile: Run the build command with the --onefile option.

``` bash
pyinstaller --onefile build.spec
```

- Result: In the dist folder, you will now find a single TCI-Static-Site-Editor.exe that you can share.

### Advantages and disadvantages of the single-file method
Advantages:

Easy to share: The user only has to download and run a single file. Very user-friendly.
Tidy: No folder with hundreds of files.

Disadvantages:

Slower startup: Each time it is launched, the application must unpack all its components into the temporary directory. Depending on the size of the app, this can take a few seconds. Launching from a folder is almost instantaneous.

Temporary files: If the app crashes, the temporary folder may not be deleted.

For final distribution to end users, the single-file method is often the best choice, despite the slightly slower startup.




