"""
Script de teste do Processo 4 — SAC (Serviço de Atendimento ao Cliente)

Testa a integração entre o Processo 3 (Cadastro) e o Processo 4 (SAC),
validando os fluxos de sucesso, duplicidade, falha técnica, fallback e monitoramento.
"""

import json
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from processo3.cadastro import executar_cadastro
from processo4.sac import executar_sac


def testar_fluxo_completo():
    print("================================================================")
    print("   BATERIA DE TESTES — INTEGRADO PROCESSO 3 + PROCESSO 4 (SAC)")
    print("================================================================\n")

    # ------------------------------------------------------------------
    # TESTE 1: Cadastro com Sucesso (P3 OK -> P4 SAC OK)
    # ------------------------------------------------------------------
    print(">>> TESTE 1: Cadastro Válido (P3 Sucesso -> P4 Comunicação OK)")
    cliente_valido = {
        "nome": "Ana Paula Souza",
        "email": "ana.souza@email.com",
        "cpf": "11122233344",
        "simular_erro_api": False
    }

    resultado_p3 = executar_cadastro(cliente_valido)
    print(f"[P3] Sucesso: {resultado_p3.get('sucesso')} | Msg: {resultado_p3.get('mensagem')}")

    resultado_p4 = executar_sac(resultado_p3)
    print(f"[P4] Sucesso: {resultado_p4.get('sucesso')} | Protocolo: {resultado_p4.get('protocolo_sac')} | Status: {resultado_p4.get('status_sac')}")
    print(f"[P4] Tempo Execução: {resultado_p4['monitoramento']['tempo_execucao_ms']} ms")
    assert resultado_p4["sucesso"] is True
    assert resultado_p4["dados_prontos_para_p5"] is True
    print("✔ TESTE 1 APROVADO\n" + "-" * 60)

    # ------------------------------------------------------------------
    # TESTE 2: Tentativa de Cadastro Duplicado (P3 Alerta -> P4 Trata Duplicidade)
    # ------------------------------------------------------------------
    print("\n>>> TESTE 2: Cliente Duplicado (P3 Alerta -> P4 Notifica Duplicidade)")
    cliente_duplicado = {
        "nome": "Ana Paula Souza",
        "email": "ana.souza@email.com",
        "cpf": "11122233344",  # Mesmo CPF do Teste 1
        "simular_erro_api": False
    }

    resultado_p3_dup = executar_cadastro(cliente_duplicado)
    print(f"[P3] Sucesso: {resultado_p3_dup.get('sucesso')} | Msg: {resultado_p3_dup.get('mensagem')}")

    resultado_p4_dup = executar_sac(resultado_p3_dup)
    print(f"[P4] Status SAC: {resultado_p4_dup.get('status_sac')} | Categoria: {resultado_p4_dup['registro_atendimento']['categoria']}")
    assert resultado_p4_dup["status_sac"] == "ALERTA_DUPLICIDADE"
    print("✔ TESTE 2 APROVADO\n" + "-" * 60)

    # ------------------------------------------------------------------
    # TESTE 3: Erro na API do Processo 3 (P3 Falha -> P4 Notifica Pendência)
    # ------------------------------------------------------------------
    print("\n>>> TESTE 3: Erro de API no P3 (P3 Falha -> P4 Notifica Pendência Técnica)")
    cliente_erro_api = {
        "nome": "Roberto Carlos",
        "email": "roberto@email.com",
        "cpf": "55566677788",
        "simular_erro_api": True  # Força erro na API no Processo 3
    }

    resultado_p3_erro = executar_cadastro(cliente_erro_api)
    print(f"[P3] Sucesso: {resultado_p3_erro.get('sucesso')} | Msg: {resultado_p3_erro.get('mensagem')}")

    resultado_p4_erro = executar_sac(resultado_p3_erro)
    print(f"[P4] Status SAC: {resultado_p4_erro.get('status_sac')} | Categoria: {resultado_p4_erro['registro_atendimento']['categoria']}")
    assert resultado_p4_erro["status_sac"] == "PENDENCIA_TECNICA"
    print("✔ TESTE 3 APROVADO\n" + "-" * 60)

    # ------------------------------------------------------------------
    # TESTE 4: Teste do Mecanismo de Fallback (P4 Entrada Corrompida)
    # ------------------------------------------------------------------
    print("\n>>> TESTE 4: Acionamento do Fallback SAC (Entrada Inválida no P4)")
    resultado_p3_corrompido = "Entrada inválida que não é um dicionário"

    resultado_p4_fb = executar_sac(resultado_p3_corrompido)  # type: ignore
    print(f"[P4 Fallback] Sucesso P4: {resultado_p4_fb.get('sucesso')} | Status SAC: {resultado_p4_fb.get('status_sac')}")
    print(f"[P4 Fallback] Msg: {resultado_p4_fb.get('mensagem')}")
    assert resultado_p4_fb["status_sac"] in ["FALLBACK", "ERRO_DADOS"]
    print("✔ TESTE 4 APROVADO\n" + "-" * 60)

    # ------------------------------------------------------------------
    # TESTE 5: Simulação de Falha na Comunicação (E-mail Retido -> Fallback de Envio)
    # ------------------------------------------------------------------
    print("\n>>> TESTE 5: Falha na Comunicação (E-mail Retido -> Fallback de Comunicação)")
    cliente_falha_email = {
        "nome": "Fernanda Lima",
        "email": "fernanda@email.com",
        "cpf": "99988877766",
        "simular_erro_comunicacao": True  # Força erro no envio de e-mail no Processo 4
    }

    resultado_p3_email = executar_cadastro(cliente_falha_email)
    resultado_p4_email = executar_sac(resultado_p3_email)
    print(f"[P4] Status SAC: {resultado_p4_email.get('status_sac')} | Status Execução: {resultado_p4_email['monitoramento']['status_execucao']}")
    assert resultado_p4_email["status_sac"] == "COMUNICACAO_RETIDA"
    assert resultado_p4_email["monitoramento"]["status_execucao"] == "ALERTA_COMUNICACAO"
    print("✔ TESTE 5 APROVADO\n" + "-" * 60)

    print("\n================================================================")
    print("   TODOS OS TESTES DO PROCESSO 4 (SAC) FORAM EXECUTADOS COM SUCESSO!")
    print("================================================================\n")


if __name__ == "__main__":
    testar_fluxo_completo()
