"""Diagnóstico de instalação VS Code sem abrir a janela gráfica."""
import sys
import importlib

print('Python executado:', sys.executable)
print('Versão do Python:', sys.version.split()[0])
errors = []
for module, package in [('pygame', 'pygame'), ('OpenGL', 'PyOpenGL')]:
    try:
        imported = importlib.import_module(module)
        print(f'{package}: OK, versão {getattr(imported,"__version__", "instalado")}')
    except ImportError as exc:
        errors.append(package)
        print(f'{package}: NÃO INSTALADO ({exc})')
if errors:
    print('\nInstale no ambiente usado: python -m pip install -r requirements.txt')
    sys.exit(1)
print('\nDependências encontradas. Execute: python main.py')
print('Observação: este diagnóstico não testa o driver nem o contexto OpenGL.')
