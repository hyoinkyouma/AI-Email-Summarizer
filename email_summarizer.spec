# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Define all required hidden imports
hidden_imports = [
    'streamlit',
    'fastapi',
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.websockets',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'bark',
    'soundfile',
    'numpy',
    'torch',
    'google.auth',
    'google.oauth2',
    'google_auth_oauthlib',
    'googleapiclient',
    'pydantic'
]

# Define the data files that need to be included
datas = [
    ('backend/credentials.json', 'backend'),
    ('backend/token.pickle', 'backend'),
    ('backend/*.py', 'backend'),  # Include all Python files from backend
]

# Try to include Bark model files if they exist
import os
from pathlib import Path
home = str(Path.home())
bark_path = os.path.join(home, '.cache', 'bark')
if os.path.exists(bark_path):
    for root, dirs, files in os.walk(bark_path):
        for file in files:
            if file.endswith('.pt') or file.endswith('.json'):  # Only include model files
                src = os.path.join(root, file)
                dst = os.path.join('bark_models', os.path.relpath(root, bark_path))
                datas.append((src, dst))

a = Analysis(
    ['app.py'],  # Main script
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EmailSummarizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # You can add an icon file path here if you want
)