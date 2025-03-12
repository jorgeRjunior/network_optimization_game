"""
Script para criar um executável do Otimizador de Rede para Jogos
Requer: PyInstaller instalado (pip install pyinstaller)
"""

import os
import sys
import shutil
from subprocess import run, PIPE

def create_executable():
    print("Iniciando criação do executável...")
    
    # Nome do arquivo principal
    main_file = "network_optimizer.py"
    
    # Verificar se o arquivo principal existe
    if not os.path.exists(main_file):
        print(f"ERRO: Arquivo {main_file} não encontrado.")
        print(f"Renomeie seu arquivo principal para {main_file} ou modifique este script.")
        return False
    
    # Verificar se o PyInstaller está instalado
    try:
        import PyInstaller
        print("PyInstaller encontrado:", PyInstaller.__version__)
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        result = run([sys.executable, "-m", "pip", "install", "pyinstaller"], stdout=PIPE, stderr=PIPE, text=True)
        if result.returncode != 0:
            print("ERRO ao instalar PyInstaller:")
            print(result.stderr)
            return False
        print("PyInstaller instalado com sucesso.")
    
    # Criar diretório para o ícone se não existir
    if not os.path.exists("resources"):
        os.makedirs("resources")
    
    # Verificar se há um ícone, caso contrário criar um arquivo .ico genérico
    icon_path = "resources/icon.ico"
    if not os.path.exists(icon_path):
        print("Ícone não encontrado. Usando ícone padrão do PyInstaller.")
        icon_option = []
    else:
        icon_option = ["--icon", icon_path]
    
    # Criar o arquivo .spec para PyInstaller
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_file}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Otimizador de Rede para Jogos',
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
    {'icon="' + icon_path + '",' if os.path.exists(icon_path) else ''}
    uac_admin=True,
)
"""
    
    # Salvar o arquivo .spec
    spec_file = "network_optimizer.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Configuração do PyInstaller criada.")
    print("Iniciando compilação do executável...")
    
    # Executar o PyInstaller com o arquivo .spec
    pyinstaller_cmd = ["pyinstaller", "--clean", spec_file]
    result = run(pyinstaller_cmd, stdout=PIPE, stderr=PIPE, text=True)
    
    if result.returncode != 0:
        print("ERRO ao criar o executável:")
        print(result.stderr)
        return False
    
    print("\nExecutável criado com sucesso!")
    print("\nVocê pode encontrar o executável em: dist/Otimizador de Rede para Jogos.exe")
    return True

if __name__ == "__main__":
    create_executable()