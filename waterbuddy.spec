# -*- mode: python ; coding: utf-8 -*-
import platform
import sys

block_cipher = None
is_mac = sys.platform == "darwin"
is_win = sys.platform == "win32"

icon_path = None
if is_mac:
    icon_path = "assets/icon.icns"
elif is_win:
    icon_path = "assets/icon.ico"

# On Windows, exclude macOS-only packages so the build doesn't fail
excludes = []
if is_win:
    excludes = ["AppKit", "Foundation", "objc", "Cocoa"]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("assets", "assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
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
    name="WaterBuddy",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # No terminal window on Windows
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
    name="WaterBuddy",
)

if is_mac:
    app = BUNDLE(
        coll,
        name="WaterBuddy.app",
        icon=icon_path,
        bundle_identifier="com.waterbuddy.app",
        info_plist={
            "LSUIElement": True,           # Hide from Dock
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,
        },
    )
