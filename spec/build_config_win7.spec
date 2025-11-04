# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

# WINDOWS 7 64-BIT COMPATIBLE BUILD
# IMPORTANT: Build this on Python 3.8.x for Windows 7 compatibility!

block_cipher = None

# Get project root directory (parent of spec folder)
# SPECPATH is automatically provided by PyInstaller
spec_root = os.path.abspath(os.path.join(SPECPATH, '..'))

# Collect ALL from rembg (aggressive approach)
rembg_datas, rembg_binaries, rembg_hiddenimports = collect_all('rembg')

# Also collect from dependencies
pymatting_datas, pymatting_binaries, pymatting_hiddenimports = collect_all('pymatting')
pooch_datas, pooch_binaries, pooch_hiddenimports = collect_all('pooch')

# Get site-packages path
site_packages = next(p for p in sys.path if 'site-packages' in p)
rembg_path = os.path.join(site_packages, 'rembg')

# Manual add rembg package as data
manual_rembg_datas = [(rembg_path, 'rembg')]

a = Analysis(
    [os.path.join(spec_root, 'main.py')],
    pathex=[spec_root],
    binaries=rembg_binaries + pymatting_binaries + pooch_binaries,
    datas=[
        (os.path.join(spec_root, 'ui'), 'ui'),
        (os.path.join(spec_root, 'utils'), 'utils'),
        (os.path.join(spec_root, 'assets', 'icon.ico'), '.'),
        (os.path.join(spec_root, 'assets', 'splash.png'), '.')
    ] + rembg_datas + pymatting_datas + pooch_datas + manual_rembg_datas,
    hiddenimports=[
        # Rembg 2.0.30 and ALL its dependencies
        'rembg',
        'rembg.bg',
        'rembg.session_factory',
        'rembg.session_base',
        'rembg.session_cloth',
        'rembg.session_simple',
        'rembg.cli',
        'rembg._version',
        # PyMatting
        'pymatting',
        'pymatting.util',
        'pymatting.util.util',
        'pymatting.alpha',
        'pymatting.alpha.estimate_alpha_cf',
        'pymatting.alpha.estimate_alpha_knn',
        'pymatting.alpha.estimate_alpha_lbdm',
        'pymatting.alpha.estimate_alpha_lkm',
        'pymatting.alpha.estimate_alpha_rw',
        'pymatting.foreground',
        'pymatting.foreground.estimate_foreground_ml',
        # Scipy
        'scipy',
        'scipy.sparse',
        'scipy.sparse.linalg',
        'scipy.sparse.linalg._dsolve',
        'scipy.sparse.linalg._eigen',
        'scipy.sparse.linalg._isolve',
        'scipy.sparse.csgraph',
        'scipy.sparse.csgraph._validation',
        'scipy.ndimage',
        'scipy.ndimage._ni_support',
        'scipy.ndimage._nd_image',
        'scipy.special',
        'scipy.special._ufuncs',
        # Scikit-image
        'skimage',
        'skimage.transform',
        'skimage.transform._geometric',
        'skimage.transform._warps',
        'skimage.color',
        'skimage.color.colorconv',
        'skimage.util',
        'skimage.util.dtype',
        # Pooch for model downloading
        'pooch',
        'pooch.core',
        # OpenCV
        'cv2',
        # PIL
        'PIL',
        'PIL.Image',
        'PIL.ImageFilter',
        'PIL.ImageEnhance',
        # Numpy
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        # PyQt5
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        # ONNX Runtime
        'onnxruntime',
        'onnxruntime.capi',
        'onnxruntime.capi.onnxruntime_pybind11_state',
        'onnxruntime.capi._pybind_state'
    ] + rembg_hiddenimports + pymatting_hiddenimports + pooch_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'test',
        'tests',
        'sklearn',
        'torch',
        'torchvision'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Splash screen configuration
splash = Splash(
    os.path.join(spec_root, 'assets', 'splash.png'),
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    minify_script=True,
    always_on_top=True,
)

# ONEDIR MODE: Best compatibility for Windows 7
exe = EXE(
    pyz,
    a.scripts,
    splash,
    splash.binaries,
    [],
    exclude_binaries=True,
    name='Primadona_Background_Remover',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabled untuk kompatibilitas Windows 7
    console=False,
    disable_windowed_traceback=False,
    target_arch='x64',  # IMPORTANT: 64-bit untuk Windows 7 64-bit
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_root, "assets", "icon.ico"),
    uac_admin=False,  # Tidak perlu admin rights
    uac_uiaccess=False,
)

# COLLECT: Kumpulkan semua file dalam folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Primadona_Background_Remover_Win7'
)
