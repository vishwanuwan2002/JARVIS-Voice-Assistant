from Jarvis.features import app_finder

for name in ['telegram', 'spotify', 'youtube', 'chrome']:
    info = app_finder.find_appx_package(name)
    print(f"--- {name} ---")
    print(info)
