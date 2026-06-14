"""
PyInstaller configuration for creating standalone EchoType executable
"""

# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/python', 'src/python'),
    ],
    hiddenimports=[
        'PyQt6',
        'pyttsx3',
        'whisper',
        'sounddevice',
        'soundfile',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EchoType',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if 'assets/icon.ico' else None,
)

app = BUNDLE(
    exe,
    name='EchoType.app',
    icon='assets/icon.icns' if 'assets/icon.icns' else None,
    bundle_identifier='com.echotype.app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
    },
)
