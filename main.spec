# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\wdc\\Documents\\wdc\\TSAnalyzer'],
             binaries=[],
             datas=[('TSAnalyzer\\resources\\style.qss', 'TSAnalyzer\\resources'),
             ('TSAnalyzer\\resources\\images\\*', 'TSAnalyzer\\resources\\images'),
             ('TSAnalyzer\\resources\\ui\\*.ui', 'TSAnalyzer\\resources\\ui')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True)
