from os import path, pathsep # ';' for Windows, ':' for Unix
from sys import platform
from importlib import util
import PyInstaller.__main__

ctk_path = path.dirname(util.find_spec("customtkinter").origin)

args = [
    'RavenFormatsUI_CTKI.pyw',
    '--noconfirm',
    '--windowed',
    '--specpath', 'dist',
    '--additional-hooks-dir', '.',
    '--add-data', f'../xmlb_fake.py{pathsep}.',
    '--add-data', f'{ctk_path}{pathsep}customtkinter/'
]

if platform in ['win64', 'win32']:
    args.extend([
        '--onefile',
        '--version-file', '../RavenFormatsUI_CTKI.txt',
        '--icon', '../MM.ico',
        '--add-data', f'../MM.ico{pathsep}.'
    ])
elif platform == 'darwin':
    args.extend([
        '--icon', '../MM.icns',
        '--add-data', f'../MM.icns{pathsep}.'
    ])
else: # Linux
    args.extend([
        '--onefile',
        '--icon', '../MM.png', #.png preferred
        '--add-data', f'../MM.png{pathsep}.'
    ])

PyInstaller.__main__.run(args)