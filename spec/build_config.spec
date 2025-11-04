# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Get project root directory (parent of spec folder)
# SPECPATH is automatically provided by PyInstaller
spec_root = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    [os.path.join(spec_root, 'main.py')],
    pathex=[spec_root],
    binaries=[],
    datas=[
        (os.path.join(spec_root, 'ui'), 'ui'),
        (os.path.join(spec_root, 'utils'), 'utils'),
        (os.path.join(spec_root, 'assets', 'icon.ico'), '.')
    ],
    hiddenimports=[
        # Rembg and its dependencies
        'rembg',
        'rembg.bg',
        'rembg.session_factory',
        'rembg.sessions',
        'rembg.sessions.base',
        'rembg.sessions.u2net',
        'pymatting',
        'pymatting.util',
        'pymatting.alpha',
        'pymatting.foreground',
        'scipy',
        'scipy.sparse',
        'scipy.sparse.linalg',
        'scipy.ndimage',
        'skimage',
        'skimage.transform',
        'skimage.color',
        'skimage.util',
        'pooch',
        # OpenCV
        'cv2',
        # PIL
        'PIL',
        'PIL.Image',
        'PIL.ImageFilter',
        'PIL.ImageEnhance',
        # Numpy
        'numpy',
        # PyQt5
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        # ONNX Runtime
        'onnxruntime',
        'onnxruntime.capi',
        'onnxruntime.capi.onnxruntime_pybind11_state'
    ],
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
        'sklearn',  # scikit-learn (berbeda dengan skimage)
        'torch',  # PyTorch tidak dipakai, rembg pakai onnxruntime
        'torchvision'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Primadona_Background_Remover',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabled untuk startup lebih cepat
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Diubah ke True untuk debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_root, "assets", "icon.ico")
)