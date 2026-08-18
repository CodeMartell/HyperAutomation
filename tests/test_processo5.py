"""
Testes unitários para o Processo 5 (Relatórios).
"""

import pytest
from pathlib import Path
from processo5.relatorios import (
    executar_relatorios,
    validar_dados_processo4,
    gerar_metricas,
    fallback_relatorio,
)


def test_validar_dados_processo4_valido():
    p4_valido = {"dados_prontos_para_p5": True, "status_sac": "CONCLUIDO"}
    assert validar_dados_processo4(p4_valido) is True


def test_validar_dados_processo4_invalido():
    assert validar_dados_processo4("entrada invalida") is False  # type: ignore


def test_executar_relatorios_sucesso():
    p4_payload = {
        "sucesso": True,
        "protocolo_sac": "SAC-20260818-0001",
        "status_sac": "CONCLUIDO",
        "cliente": {"nome": "Teste P5", "email": "p5@email.com", "cpf": "11111111111"},
        "registro_atendimento": {},
        "monitoramento": {"tempo_execucao_ms": 1.2},
        "dados_prontos_para_p5": True,
    }
    res_p5 = executar_relatorios(p4_payload)
    assert res_p5["sucesso"] is True
    assert res_p5["status"] == "PROCESSO_CONCLUIDO"
    assert "metricas" in res_p5
    assert Path(res_p5["arquivo_relatorio"]).exists()


def test_executar_relatorios_fallback():
    res_p5 = executar_relatorios("dados invalidos")  # type: ignore
    assert res_p5["sucesso"] is False
    assert res_p5["status"] == "FALLBACK"
