from os import path, pathsep # ';' for Windows, ':' for Unix
from sys import argv, platform
from importlib import util
import PyInstaller.__main__

VERSION = argv[1] if len(argv) > 1 else ''
SCRIPT_NAME = 'RavenFormatsUI_CTKI'
ICON_NAME = 'MM'

args = [
    f'{SCRIPT_NAME}.pyw',
    '--noconfirm',
    '--windowed',
    '--specpath', 'dist',
    '--additional-hooks-dir', '.',
    '--add-data', f'../xmlb_fake.py{pathsep}.',
    '--add-data', f'{path.dirname(util.find_spec("customtkinter").origin)}{pathsep}customtkinter/'
]

if platform in ['win64', 'win32']:
    args.extend([
        '--onefile',
        '--version-file', f'../{SCRIPT_NAME}.txt',
        '--icon', f'../{ICON_NAME}.ico',
        '--add-data', f'../{ICON_NAME}.ico{pathsep}.'
    ])
    if VERSION:
        v = len(VERSION) # must not surpass the version configuration in the text
        with open(f'{SCRIPT_NAME}.txt', 'r+') as f:
            while (line := f.readline()):
                if line[8:14] == 'vers=(':
                    f.seek(pos)
                    f.write(f"{line[:14]}{VERSION[1:].replace('.', ', ')}{line[15 + v // 2 * 3 - 3:]}")
                elif line[29:36] == 'Version':
                    f.seek(pos)
                    f.write(f'{line[:40]}{VERSION[1:]}{line[39 + v:]}')
                pos = f.tell() # Only works if match isn't on first line
elif platform == 'darwin':
    args.extend([
        '--icon', f'../{ICON_NAME}.icns',
        '--add-data', f'../{ICON_NAME}.icns{pathsep}.',
        '--osx-bundle-identifier', f'com.ak2yny.ravenformatsui'
    ])
else: # Linux
    args.extend([
        '--onefile',
        '--icon', f'../{ICON_NAME}.png',
        '--add-data', f'../{ICON_NAME}.png{pathsep}.',
        '--name', f'{SCRIPT_NAME}-Linux' # _{VERSION}
    ])

PyInstaller.__main__.run(args)

if platform == 'darwin' and VERSION:
    spec = f'dist/{SCRIPT_NAME}.spec'
    with open(spec, 'r+') as f:
        size = f.seek(0, 2)
        _ = f.seek(size - 2)
        # Version only sets CFBundleShortVersionString
        #f.write(f"    version='{VERSION[1:]}',\n)\n")
        f.write(f'''info_plist={{
        'CFBundleShortVersionString': '{VERSION[1:]}',
        'CFBundleVersion': '{VERSION[1:]}',
        }},
)
''')
    PyInstaller.__main__.run([spec, '-y'])
