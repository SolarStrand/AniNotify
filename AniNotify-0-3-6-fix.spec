# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\5atan\\Documents\\python\\notify_if_new_voice\\notifier.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\5atan\\Documents\\python\\notify_if_new_voice\\bin\\aninotify_icon.ico', 'bin')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AniNotify-0-3-6-fix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\5atan\\Documents\\python\\notify_if_new_voice\\bin\\aninotify_icon.ico'],
)
