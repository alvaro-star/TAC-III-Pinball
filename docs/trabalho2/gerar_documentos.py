"""Gera os PDFs do Trabalho 2 (GDD e relatório) no formato ABNT simplificado a partir dos HTML.

Uso (na raiz do projeto): python docs/trabalho2/gerar_documentos.py
Requer: Graphviz (dot) e Google Chrome ou Chromium.
1. Renderiza os diagramas .dot em PNG.
2. Imprime cada HTML em PDF (formatação em abnt.css).
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = {
    'gdd.html': 'UNI - TAC III - GDD Pinball Trabalho 2.pdf',
    'relatorio.html': 'UNI - TAC III - Relatorio Tecnico Trabalho 2.pdf',
}


def find_chrome():
    for name in ('google-chrome', 'chromium', 'chromium-browser', 'chrome', 'msedge'):
        path = shutil.which(name)
        if path:
            return path
    sys.exit('Chrome/Chromium não encontrado.')


def render_diagrams():
    for dot in sorted((HERE / 'diagramas').glob('*.dot')):
        subprocess.run(['dot', '-Tpng', '-Gdpi=160', str(dot), '-o', str(dot.with_suffix('.png'))],
                       check=True)


def print_pdf(chrome, source, target):
    subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={target}', source.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    chrome = find_chrome()
    render_diagrams()
    for name, output in DOCS.items():
        print_pdf(chrome, HERE / name, HERE / output)
        print('gerado:', output)
