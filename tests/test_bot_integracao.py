"""
Teste de Integração End-to-End para bot.py e pai.bot.py.
"""

import importlib.util
from pathlib import Path
import pytest
from bot import executar_pipeline_completa

RAIZ_PROJETO = Path(__file__).resolve().parent.parent


def test_executar_pipeline_bot():
    res_p5 = executar_pipeline_completa()
    assert res_p5["sucesso"] is True
    assert res_p5["status"] == "PROCESSO_CONCLUIDO"
    assert res_p5["metricas"]["total_atendimentos"] >= 1


def test_pai_bot_wrapper_import():
    # Importa dinamica e com seguranca pai.bot.py (arquivo com ponto no nome)
    caminho_pai = RAIZ_PROJETO / "pai.bot.py"
    spec = importlib.util.spec_from_file_location("pai_bot_module", str(caminho_pai))
    assert spec is not None
    assert spec.loader is not None
    pai_bot_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pai_bot_module)
    assert hasattr(pai_bot_module, "main")
