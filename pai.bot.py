"""
HyperAutomation — Ponto de Entrada de Compatibilidade (pai.bot.py)

Arquivo wrapper de compatibilidade que delega a execução para bot.py.
Garante que comandos invocando tanto 'python bot.py' quanto 'python pai.bot.py'
funcionem com 100% de paridade.
"""

from bot import main

if __name__ == "__main__":
    main()
