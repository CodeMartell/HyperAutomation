"""
Testes unitários para o Processo 4 (SAC).
"""

import pytest
from processo3.cadastro import executar_cadastro
from processo4.sac import (
    executar_sac,
    verificar_status_p3,
    tratar_resultado_sac,
    fallback_sac,
    gerar_protocolo_sac,
)


def test_gerar_protocolo_sac():
    proto = gerar_protocolo_sac()
    assert proto.startswith("SAC-")


def test_executar_sac_sucesso():
    p3_sucesso = {
        "sucesso": True,
        "mensagem": "Cliente cadastrado com sucesso",
        "cliente": {"nome": "Gabriel Santos", "email": "gabriel@email.com", "cpf": "12312312312"},
        "api": {"status_code": 201, "id_cliente": "CLI-999"}
    }
    res_p4 = executar_sac(p3_sucesso)
    assert res_p4["sucesso"] is True
    assert res_p4["status_sac"] == "CONCLUIDO"
    assert res_p4["protocolo_sac"].startswith("SAC-")
    assert res_p4["dados_prontos_para_p5"] is True


def test_executar_sac_duplicidade():
    p3_dup = {
        "sucesso": False,
        "mensagem": "Cliente já cadastrado",
        "cliente": {"nome": "Gabriel Santos", "email": "gabriel@email.com", "cpf": "12312312312"}
    }
    res_p4 = executar_sac(p3_dup)
    assert res_p4["status_sac"] == "ALERTA_DUPLICIDADE"


def test_executar_sac_erro_tecnico():
    p3_erro = {
        "sucesso": False,
        "mensagem": "Falha na comunicação com a API",
        "cliente": {"nome": "Luciana Silva", "email": "luciana@email.com", "cpf": "45645645645"}
    }
    res_p4 = executar_sac(p3_erro)
    assert res_p4["status_sac"] == "PENDENCIA_TECNICA"


def test_executar_sac_fallback_corrompido():
    p3_corrompido = "Entrada inválida"
    res_p4 = executar_sac(p3_corrompido)  # type: ignore
    assert res_p4["status_sac"] in ["FALLBACK", "ERRO_DADOS"]


def test_executar_sac_falha_comunicacao_retida():
    p3_email_erro = {
        "sucesso": True,
        "mensagem": "Cliente cadastrado com sucesso",
        "cliente": {
            "nome": "Fernando",
            "email": "fernando@email.com",
            "cpf": "77788899900",
            "simular_erro_comunicacao": True
        }
    }
    res_p4 = executar_sac(p3_email_erro)
    assert res_p4["status_sac"] == "COMUNICACAO_RETIDA"
    assert res_p4["monitoramento"]["status_execucao"] == "ALERTA_COMUNICACAO"
