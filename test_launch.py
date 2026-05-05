from Jarvis.features import app_finder

for name in ['telegram','spotify']:
    info = app_finder.find_appx_package(name)
    print('INFO', info)
    if info:
        ok = app_finder.launch_appx_package(info)
        print(name, 'launched?', ok)
    else:
        print(name, 'not found')
