# -*- mode: python -*-

block_cipher = None


a = Analysis(['launcherMac.py'],
             pathex=['/Users/franzz1818/Documents/CSM-project/launcherMac'],
             binaries=[],
             datas=[],
             hiddenimports=['scipy._lib.messagestream', 'h5py.defs', 'h5py.utils'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='launcherMac',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='launcherMac')
