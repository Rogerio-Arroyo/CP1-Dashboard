"""Entrypoint WSGI para deploy no Vercel.
O Vercel Python procura um objeto WSGI chamado 'app' neste arquivo.
Reaproveitamos o servidor Flask que o Dash cria internamente.
"""
import sys
import os

# garante que o diretório raiz do projeto esteja no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import server as app  # 'server' é o Flask WSGI do Dash
