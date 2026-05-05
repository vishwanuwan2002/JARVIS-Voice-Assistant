"""
Search for installed applications on Windows and launch them.
Falls back to browser if not found.
"""

import os
import subprocess
import webbrowser
import json
import difflib
# pathlib.Path was unused; removed


# Common app installation paths on Windows
APP_PATHS = {
    'youtube': [
        'C:/Program Files/YouTube/YouTube.exe',
        'C:/Program Files (x86)/YouTube/YouTube.exe',
        os.path.expandvars('%APPDATA%/YouTube/YouTube.exe'),
    ],
    'spotify': [
        os.path.expandvars('%APPDATA%/Spotify/Spotify.exe'),
        'C:/Users/*/AppData/Roaming/Spotify/Spotify.exe',
    ],
    'discord': [
        os.path.expandvars('%LOCALAPPDATA%/Discord/app-*/Discord.exe'),
        'C:/Program Files/Discord/Discord.exe',
        'C:/Program Files (x86)/Discord/Discord.exe',
    ],
    'telegram': [
        'C:/Users/*/AppData/Roaming/Telegram Desktop/Telegram.exe',
        os.path.expandvars('%APPDATA%/Telegram Desktop/Telegram.exe'),
        'C:/Program Files/Telegram/Telegram.exe',
    ],
    'whatsapp': [
        os.path.expandvars('%LOCALAPPDATA%/WhatsApp/WhatsApp.exe'),
        'C:/Program Files/WhatsApp/WhatsApp.exe',
        'C:/Program Files (x86)/WhatsApp/WhatsApp.exe',
    ],
    'chrome': [
        'C:/Program Files/Google/Chrome/Application/chrome.exe',
        'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    ],
    'firefox': [
        'C:/Program Files/Mozilla Firefox/firefox.exe',
        'C:/Program Files (x86)/Mozilla Firefox/firefox.exe',
    ],
    'edge': [
        'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
        'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    ],
    'excel': [
        'C:/Program Files/Microsoft Office/root/Office*/EXCEL.EXE',
        'C:/Program Files (x86)/Microsoft Office/root/Office*/EXCEL.EXE',
    ],
    'word': [
        'C:/Program Files/Microsoft Office/root/Office*/WINWORD.EXE',
        'C:/Program Files (x86)/Microsoft Office/root/Office*/WINWORD.EXE',
    ],
    'powerpoint': [
        'C:/Program Files/Microsoft Office/root/Office*/POWERPNT.EXE',
        'C:/Program Files (x86)/Microsoft Office/root/Office*/POWERPNT.EXE',
    ],
    'notepad': [
        'C:/Windows/System32/notepad.exe',
    ],
    'calculator': [
        'C:/Windows/System32/calc.exe',
    ],
    'file explorer': [
        'C:/Windows/explorer.exe',
    ],
    'vscode': [
        os.path.expandvars('%LOCALAPPDATA%/Programs/Microsoft VS Code/Code.exe'),
        'C:/Program Files/Microsoft VS Code/Code.exe',
    ],
    'visual studio': [
        'C:/Program Files/Microsoft Visual Studio/*/Enterprise/Common7/IDE/devenv.exe',
    ],
    'vlc': [
        'C:/Program Files/VideoLAN/VLC/vlc.exe',
        'C:/Program Files (x86)/VideoLAN/VLC/vlc.exe',
    ],
    'paint': [
        'C:/Windows/System32/mspaint.exe',
    ],
    'settings': [
        'C:/Windows/System32/ms-settings:',
    ],
}

# Mapping of app names to their most common browser equivalents
BROWSER_FALLBACKS = {
    'youtube': 'youtube.com',
    'spotify': 'spotify.com',
    'discord': 'discord.com',
    'telegram': 'telegram.org',
    'whatsapp': 'whatsapp.com',
    'twitter': 'twitter.com',
    'facebook': 'facebook.com',
    'instagram': 'instagram.com',
    'gmail': 'gmail.com',
    'google': 'google.com',
    'amazon': 'amazon.com',
}

# Path to optional user overrides (maps app name -> path or special directive)
OVERRIDES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'app_overrides.json')

# Simple synonyms to map common phrases to canonical names
SYNONYMS = {
    'explorer': 'file explorer',
    'filemanager': 'file explorer',
    'file-manager': 'file explorer',
    'vs code': 'vscode',
    'visual studio code': 'vscode',
    'code': 'vscode',
    'visual studio': 'visual studio',
    'telegram desktop': 'telegram',
    'telegramapp': 'telegram',
    'youtube app': 'youtube',
    'whatsapp desktop': 'whatsapp',
    'edge browser': 'edge',
    'internet explorer': 'edge',
}


def load_app_overrides():
    try:
        if os.path.exists(OVERRIDES_PATH):
            with open(OVERRIDES_PATH, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                # Normalize keys to lowercase
                return {k.lower(): v for k, v in data.items()}
    except Exception as e:
        print(f"Failed to load app_overrides.json: {e}")
    return {}


def canonicalize_app_name(name):
    """Return a canonical app key for matching (uses overrides, synonyms, fuzzy matching)."""
    if not name:
        return name
    name_l = name.strip().lower()
    overrides = load_app_overrides()
    if name_l in overrides:
        return name_l
    if name_l in APP_PATHS:
        return name_l
    if name_l in BROWSER_FALLBACKS:
        return name_l
    if name_l in SYNONYMS:
        return SYNONYMS[name_l]
    # Try partial matches in synonyms keys
    for k, v in SYNONYMS.items():
        if k in name_l:
            return v
    # fuzzy match against known keys
    choices = list(set(list(APP_PATHS.keys()) + list(BROWSER_FALLBACKS.keys()) + list(SYNONYMS.values()) + list(overrides.keys())))
    if choices:
        match = difflib.get_close_matches(name_l, choices, n=1, cutoff=0.6)
        if match:
            return match[0]
    return name_l


def find_app_in_registry(app_name):
    """
    Search Windows registry for installed applications.
    This is a fallback method if the predefined paths don't work.
    """
    try:
        import winreg
        
        # Check in HKEY_LOCAL_MACHINE
        reg_paths = [
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
            r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
        ]
        
        for reg_path in reg_paths:
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                for i in range(winreg.QueryInfoKey(reg_key)[0]):
                    try:
                        sub_key_name = winreg.EnumKey(reg_key, i)
                        sub_key = winreg.OpenKey(reg_key, sub_key_name)
                        display_name = winreg.QueryValueEx(sub_key, 'DisplayName')[0].lower()
                        
                        if app_name.lower() in display_name:
                            # Found the app, try to get the install location
                            try:
                                install_loc = winreg.QueryValueEx(sub_key, 'InstallLocation')[0]
                                if install_loc:
                                    return install_loc
                            except Exception:
                                # ignore missing install location for this subkey
                                # print(f"Registry subkey install location error: {e}")
                                pass
                    except Exception:
                        # ignore subkey enumeration errors
                        # print(f"Registry subkey enumeration error: {e}")
                        pass
            except Exception:
                # ignore registry path open errors
                pass
    except Exception as e:
        print(f"Registry search failed: {e}")
    
    return None


def find_appx_package(app_name):
    """
    Use PowerShell Get-AppxPackage to find a UWP/Appx package that matches app_name.
    Returns a dict with keys: Name, PackageFullName, PackageFamilyName, InstallLocation or None.
    """
    try:
        import json
        # Build a PowerShell command that selects useful fields and converts to JSON
        ps_cmd = (
            f"Get-AppxPackage -Name '*{app_name}*' | Select-Object Name,PackageFullName,PackageFamilyName,InstallLocation | ConvertTo-Json -Compress"
        )
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
        out = proc.stdout.strip()
        if not out:
            return None

        # PowerShell returns either an array or an object; parse JSON
        data = json.loads(out)
        # If list, take first
        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        # Normalize keys
        result = {
            'Name': data.get('Name'),
            'PackageFullName': data.get('PackageFullName'),
            'PackageFamilyName': data.get('PackageFamilyName'),
            'InstallLocation': data.get('InstallLocation'),
        }
        return result
    except Exception as e:
        # PowerShell might be restricted or command could fail; just return None
        print(f"Appx package lookup failed: {e}")
        return None


def launch_appx_package(package_info):
    """
    Given package info (dict from find_appx_package), try to locate the app Id in AppxManifest.xml
    and launch via shell:AppsFolder\<PackageFamily>!<AppId>
    Returns True on success, False otherwise.
    """
    try:
        pkg_family = package_info.get('PackageFamilyName')
        install_loc = package_info.get('InstallLocation')
        if not pkg_family or not install_loc:
            return False

        manifest_path = os.path.join(install_loc, 'AppxManifest.xml')
        # Some packages may include multiple manifests or different casing
        if not os.path.exists(manifest_path):
            # try to find any AppxManifest.xml under install_loc
            for root, dirs, files in os.walk(install_loc):
                for f in files:
                    if f.lower() == 'appxmanifest.xml':
                        manifest_path = os.path.join(root, f)
                        break
                if os.path.exists(manifest_path):
                    break

        if not os.path.exists(manifest_path):
            return False

        # Parse manifest to get Application Id
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            # Namespace handling: manifest often has a default namespace
            ns = ''
            if root.tag.startswith('{'):
                ns = root.tag.split('}')[0].strip('{')
            nsmap = {'ns': ns} if ns else {}

            # Find first Application element and get its Id attribute
            app_id = None
            if ns:
                apps = root.findall('.//ns:Applications/ns:Application', nsmap)
            else:
                apps = root.findall('.//Applications/Application')

            if apps:
                app_elem = apps[0]
                app_id = app_elem.get('Id') or app_elem.get('Id'.lower())

            if not app_id:
                # Try a fallback: common Application Id 'App'
                app_id = 'App'

            app_user_model_id = f"{pkg_family}!{app_id}"

            # Launch via explorer shell
            subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_user_model_id}"])
            return True
        except Exception as e:
            print(f"Failed to parse manifest or launch appx package: {e}")
            return False
    except Exception as e:
        print(f"launch_appx_package error: {e}")
        return False


def find_app_executable(app_name):
    """
    Find the executable path for a given app name.
    Returns the path if found, None otherwise.
    """
    app_name_lower = app_name.lower().strip()
    
    # Check predefined paths
    if app_name_lower in APP_PATHS:
        for path_pattern in APP_PATHS[app_name_lower]:
            # Handle user home expansion
            expanded_path = os.path.expandvars(path_pattern)
            
            # Handle wildcards in paths (like */Discord/app-*/Discord.exe)
            if '*' in expanded_path:
                # Use glob to find matching paths
                from glob import glob
                matches = glob(expanded_path, recursive=True)
                if matches:
                    # Return the first matching path
                    if os.path.exists(matches[0]):
                        return matches[0]
            else:
                # Direct path check
                if os.path.exists(expanded_path):
                    return expanded_path
    
    # If not found in predefined paths, search in common app directories
    common_dirs = [
        os.path.expandvars('%APPDATA%'),
        os.path.expandvars('%LOCALAPPDATA%'),
        'C:/Program Files',
        'C:/Program Files (x86)',
    ]
    
    for dir_path in common_dirs:
        if os.path.exists(dir_path):
            # Search for exe files matching the app name
            from glob import glob
            search_pattern = os.path.join(dir_path, f'*{app_name_lower.replace(" ", "*")}*/**/*.exe')
            matches = glob(search_pattern, recursive=True)
            if matches:
                # Return the first matching executable
                return matches[0]
    
    # Try registry search as fallback
    registry_result = find_app_in_registry(app_name)
    if registry_result:
        return registry_result
    
    return None


def open_app_or_browser(app_name):
    """
    Try to open an installed app. If not found, open in browser instead.
    
    :param app_name: Name of the application to open
    :return: Tuple (success: bool, action: str, details: str)
             Example: (True, 'app', 'Opened YouTube from installed app')
             Example: (True, 'browser', 'Opened youtube.com in browser')
             Example: (False, 'error', 'Could not open YouTube')
    """
    try:
        # Use canonical name (fuzzy + synonyms + overrides)
        canonical = canonicalize_app_name(app_name)
        overrides = load_app_overrides()

        # If there's a user override, try it first
        override_val = overrides.get(canonical)
        if override_val:
            try:
                if isinstance(override_val, str) and override_val.lower().startswith('appx:'):
                    pkg_name = override_val.split(':', 1)[1]
                    pkg_info = find_appx_package(pkg_name)
                    if pkg_info and launch_appx_package(pkg_info):
                        return (True, 'app', f'Opened {canonical} using override (UWP)')
                else:
                    path = os.path.expandvars(override_val)
                    if os.path.exists(path):
                        subprocess.Popen(path)
                        return (True, 'app', f'Opened {canonical} using override (exe)')
                    else:
                        # try to launch as command
                        try:
                            subprocess.Popen(override_val)
                            return (True, 'app', f'Opened {canonical} using override (cmd)')
                        except Exception:
                            pass
            except Exception:
                pass

        # First try UWP/Appx packages for the canonical name
        try:
            pkg_info = find_appx_package(canonical)
            if pkg_info:
                launched = launch_appx_package(pkg_info)
                if launched:
                    return (True, 'app', f'Opened {canonical} from installed app (UWP)')
        except Exception:
            pass

        # Next, try to find and launch a traditional executable
        app_path = find_app_executable(canonical)
        if app_path:
            # Found the app - launch it
            try:
                if canonical == 'settings':
                    os.startfile(app_path)
                else:
                    subprocess.Popen(app_path)
                return (True, 'app', f'Opened {canonical} from installed app')
            except Exception as e:
                print(f"Failed to launch app from path {app_path}: {e}")
                # Fall through to browser fallback

        # App not found installed - try browser fallback
        if canonical in BROWSER_FALLBACKS:
            domain = BROWSER_FALLBACKS[canonical]
            url = f'https://www.{domain}'
            webbrowser.open(url)
            return (True, 'browser', f'Opened {canonical} from browser')
        else:
            # No predefined path and no browser fallback - try to open as URL anyway
            domain = canonical.replace(' ', '')
            url = f'https://www.{domain}.com'
            webbrowser.open(url)
            return (True, 'browser', f'Opened {canonical} from browser')
            
    except Exception as e:
        print(f"Error in open_app_or_browser: {e}")
        return (False, 'error', f'Could not open {app_name}: {str(e)}')
