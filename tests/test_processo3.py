"""
Testes unitários para o Processo 3 (Cadastro).
"""

import pytest
from processo3.cadastro import (
    executar_cadastro,
    validar_cliente,
    verificar_duplicidade,
    fallback_cadastro,
)


def test_validar_cliente_valido():
    cliente = {"nome": "Teste", "email": "teste@email.com", "cpf": "12345678901"}
    assert validar_cliente(cliente) is True


def test_validar_cliente_invalido():
    cliente_sem_cpf = {"nome": "Teste", "email": "teste@email.com"}
    assert validar_cliente(cliente_sem_cpf) is False


def test_executar_cadastro_sucesso():
    cliente = {
        "nome": "Carlos Silva",
        "email": "carlos.p3@email.com",
        "cpf": "11122233301",
        "simular_erro_api": False,
    }
    resultado = executar_cadastro(cliente)
    assert resultado["sucesso"] is True
    assert "api" in resultado
    assert resultado["api"]["status_code"] == 201


def test_executar_cadastro_duplicado():
    cliente = {
        "nome": "Carlos Silva",
        "email": "carlos.p3@email.com",
        "cpf": "11122233301",
    }
    # Tenta cadastrar novamente com o mesmo CPF
    resultado_dup = executar_cadastro(cliente)
    assert resultado_dup["sucesso"] is False
    assert "já cadastrado" in resultado_dup["mensagem"].lower() or "duplicad" in resultado_dup["mensagem"].lower()


def test_executar_cadastro_falha_api_fallback():
    cliente = {
        "nome": "Erro API",
        "email": "erro.api@email.com",
        "cpf": "99988877700",
        "simular_erro_api": True,
    }
    resultado = executar_cadastro(cliente)
    assert resultado["sucesso"] is False
    assert "fallback" in resultado["mensagem"].lower()
