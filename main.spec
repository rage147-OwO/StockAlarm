# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['FearGreed.py'],
    pathex=[],
    binaries=[('C:/Users/lim/miniconda3/envs/builder/Library/bin/libcrypto-1_1-x64.dll', '.'), ('C:/Users/lim/miniconda3/envs/builder/Library/bin/libssl-1_1-x64.dll', '.')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
)
