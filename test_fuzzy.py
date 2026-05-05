"""
Test fuzzy matching, synonyms, and app_overrides.json functionality
"""

from Jarvis.features import app_finder

print("="*80)
print("TEST 1: Fuzzy Matching & Synonyms")
print("="*80)

test_cases = [
    ('vs code', 'should map to vscode'),
    ('visual studio code', 'should map to vscode'),
    ('code', 'should map to vscode'),
    ('telegram desktop', 'should map to telegram'),
    ('explorer', 'should map to file explorer'),
    ('file-manager', 'should map to file explorer'),
    ('edge browser', 'should map to edge'),
]

for app_name, description in test_cases:
    canonical = app_finder.canonicalize_app_name(app_name)
    print(f"  {app_name:25} -> {canonical:20} ({description})")

print("\n" + "="*80)
print("TEST 2: App Overrides Loading")
print("="*80)
overrides = app_finder.load_app_overrides()
print(f"Loaded {len(overrides)} overrides from app_overrides.json")
if overrides:
    for k, v in overrides.items():
        print(f"  {k} -> {v}")
else:
    print("  (empty - you can add custom mappings)")

print("\n" + "="*80)
print("TEST 3: Actual App Detection & Launching (simulator)")
print("="*80)

test_apps = ['notepad', 'telegram', 'youtube', 'vs code', 'file explorer']
for app in test_apps:
    canonical = app_finder.canonicalize_app_name(app)
    print(f"\n  Command: open {app}")
    print(f"    -> Canonical name: {canonical}")
    
    # Don't actually launch, just show what would happen
    if canonical in app_finder.APP_PATHS:
        print(f"    -> Found in APP_PATHS (exe-based)")
    
    try:
        pkg = app_finder.find_appx_package(canonical)
        if pkg:
            print(f"    -> Found in AppxPackages (UWP): {pkg['Name']}")
    except Exception:
        pass
    
    if canonical in app_finder.BROWSER_FALLBACKS:
        print(f"    -> Will fallback to: {app_finder.BROWSER_FALLBACKS[canonical]}")

print("\n" + "="*80)
print("All tests completed successfully!")
print("="*80)
