# -*- mode: python ; coding: utf-8 -*-
import platform
import os

block_cipher = None
os_name = platform.system()
is_mac = os_name == 'Darwin'
is_win = os_name == 'Windows'

icon_path = 'assets/icon.icns' if is_mac else 'assets/icon.ico' if is_win else None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WaterBuddy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WaterBuddy',
)

if is_mac:
    app = BUNDLE(
        coll,
        name='WaterBuddy.app',
        icon=icon_path,
        bundle_identifier='com.waterbuddy.app',
        info_plist={
            'LSUIElement': True,
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
        }
    )
