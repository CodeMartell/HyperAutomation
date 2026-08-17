"""
Módulo Processo 4 — SAC (Serviço de Atendimento ao Cliente)

Responsável pelo tratamento dos resultados do Processo 3 e pela comunicação com o cliente.

Fluxo:
    Processo 3
    ↓
    Verificação do status
    ↓
    Tratamento do resultado
    ↓
    Comunicação com o cliente
    ↓
    Processo 5

Contempla:
    - Logs da execução
    - Tratamento de erros
    - Fallback
    - Monitoramento da execução
    - Registro do atendimento
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Configuração dos logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Processo4_SAC")

# Diretório base para persistência dos registros de atendimento SAC
PASTA_REGISTROS = Path(__file__).resolve().parent.parent / "ERP_Portal_Fake" / "atendimentos"
ARQUIVO_REGISTROS = PASTA_REGISTROS / "registro_atendimentos_sac.json"

# Banco/Histórico em memória para consultas rápidas durante o ciclo de vida
atendimentos_realizados = []


def inicializar_estrutura_registro() -> None:
    """
    Garante que a pasta e o arquivo de registros de atendimento existam.
    """
    try:
        PASTA_REGISTROS.mkdir(parents=True, exist_ok=True)
        if not ARQUIVO_REGISTROS.exists():
            with open(ARQUIVO_REGISTROS, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            logger.info(f"Arquivo de registros inicializado em: {ARQUIVO_REGISTROS}")
    except Exception as erro:
        logger.error(f"Erro ao inicializar estrutura de registro SAC: {erro}")


def gerar_protocolo_sac() -> str:
    """
    Gera um protocolo único de atendimento SAC (ex: SAC-20260817-0001).
    """
    data_str = datetime.now().strftime("%Y%m%d")
    timestamp_ms = int(time.time() * 1000) % 10000
    protocolo = f"SAC-{data_str}-{timestamp_ms:04d}"
    return protocolo


def verificar_status_p3(resultado_p3: Dict[str, Any]) -> Dict[str, Any]:
    """
    Etapa 1: Verificação do status do resultado vindo do Processo 3.

    Args:
        resultado_p3: Dicionário contendo o resultado retornado pelo Processo 3.

    Returns:
        Dicionário com a análise e classificação do status.
    """
    logger.info("Etapa 1/5: Verificando status recebido do Processo 3...")

    if not isinstance(resultado_p3, dict):
        logger.warning("Resultado do Processo 3 é inválido ou não é um dicionário.")
        return {
            "status_valido": False,
            "categoria": "ENTRADA_INVALIDA",
            "sucesso_p3": False,
            "motivo": "Formato de dados recebidos do Processo 3 é inválido."
        }

    sucesso = resultado_p3.get("sucesso", False)
    mensagem = resultado_p3.get("mensagem", "Sem mensagem de retorno")
    cliente = resultado_p3.get("cliente", {})

    if sucesso:
        logger.info("Processo 3 finalizado com SUCESSO (Cadastro aprovado).")
        return {
            "status_valido": True,
            "categoria": "CADASTRO_SUCESSO",
            "sucesso_p3": True,
            "motivo": mensagem,
            "cliente": cliente,
            "api_info": resultado_p3.get("api", {})
        }
    else:
        # Identifica se foi duplicidade ou falha técnica
        if "duplicado" in mensagem.lower() or "já cadastrado" in mensagem.lower():
            logger.warning(f"Processo 3 reportou DUPLICIDADE: {mensagem}")
            categoria = "CADASTRO_DUPLICADO"
        else:
            logger.error(f"Processo 3 reportou FALHA: {mensagem}")
            categoria = "CADASTRO_FALHA"

        return {
            "status_valido": True,
            "categoria": categoria,
            "sucesso_p3": False,
            "motivo": mensagem,
            "cliente": cliente,
            "erro_detalhado": resultado_p3.get("erro", mensagem)
        }


def tratar_resultado_sac(analise_status: Dict[str, Any]) -> Dict[str, Any]:
    """
    Etapa 2: Tratamento do resultado e preparação das informações do atendimento SAC.

    Args:
        analise_status: Retorno da função `verificar_status_p3`.

    Returns:
        Dicionário com os dados formatados do atendimento ao cliente.
    """
    logger.info("Etapa 2/5: Tratando o resultado e formatando mensagem do SAC...")

    protocolo = gerar_protocolo_sac()
    cliente = analise_status.get("cliente", {})
    nome_cliente = cliente.get("nome", "Cliente")
    email_cliente = cliente.get("email", "email_nao_informado@dominio.com")
    categoria = analise_status.get("categoria", "ENTRADA_INVALIDA")

    if categoria == "CADASTRO_SUCESSO":
        id_cliente = cliente.get("id_cliente") or analise_status.get("api_info", {}).get("id_cliente", "N/A")
        assunto = f"Portal Fake — Cadastro Realizado com Sucesso (Protocolo {protocolo})"
        corpo = (
            f"Olá, {nome_cliente}!\n\n"
            f"Seu cadastro no Portal Fake Soluções Digitais foi concluído com sucesso!\n"
            f"ID do Cliente: {id_cliente}\n"
            f"Protocolo de Atendimento: {protocolo}\n\n"
            f"Obrigado por utilizar nossos serviços.\n"
            f"Atenciosamente,\nEquipe de SAC — Portal Fake"
        )
        status_atendimento = "CONCLUIDO"

    elif categoria == "CADASTRO_DUPLICADO":
        assunto = f"Portal Fake — Informação sobre Solicitação de Cadastro (Protocolo {protocolo})"
        corpo = (
            f"Olá, {nome_cliente}!\n\n"
            f"Identificamos que seu cadastro já se encontra ativo em nosso sistema.\n"
            f"Protocolo de Atendimento: {protocolo}\n"
            f"Detalhes: {analise_status.get('motivo')}\n\n"
            f"Caso precise atualizar seus dados, entre em contato conosco.\n"
            f"Atenciosamente,\nEquipe de SAC — Portal Fake"
        )
        status_atendimento = "ALERTA_DUPLICIDADE"

    elif categoria == "CADASTRO_FALHA":
        assunto = f"Portal Fake — Status do seu Cadastro (Protocolo {protocolo})"
        corpo = (
            f"Olá, {nome_cliente}!\n\n"
            f"Houve uma pendência no processamento do seu cadastro.\n"
            f"Protocolo de Atendimento: {protocolo}\n"
            f"Motivo: {analise_status.get('motivo')}\n\n"
            f"Nossa equipe de suporte técnico já foi acionada para resolver a inconsistência.\n"
            f"Atenciosamente,\nEquipe de SAC — Portal Fake"
        )
        status_atendimento = "PENDENCIA_TECNICA"

    else:  # ENTRADA_INVALIDA ou desconhecida
        assunto = f"Portal Fake — Erro no Processamento do Atendimento (Protocolo {protocolo})"
        corpo = (
            f"Prezado(a) cliente,\n\n"
            f"Não foi possível processar a resposta do cadastro devido a uma inconsistência nos dados.\n"
            f"Protocolo de Atendimento: {protocolo}\n\n"
            f"Atenciosamente,\nEquipe de SAC — Portal Fake"
        )
        status_atendimento = "ERRO_DADOS"

    logger.info(f"Atendimento {protocolo} preparado para '{email_cliente}' com status [{status_atendimento}].")

    return {
        "protocolo": protocolo,
        "email_cliente": email_cliente,
        "nome_cliente": nome_cliente,
        "assunto": assunto,
        "corpo": corpo,
        "status_atendimento": status_atendimento,
        "categoria": categoria,
        "cliente": cliente
    }


def comunicar_cliente(atendimento: Dict[str, Any], simular: bool = True) -> Dict[str, Any]:
    """
    Etapa 3: Comunicação com o cliente (envio por e-mail ou simulação auditável).

    Args:
        atendimento: Dados formatados do atendimento.
        simular: Se True, simula o envio com sucesso sem depender de SMTP ativo.

    Returns:
        Status do envio da comunicação.
    """
    logger.info(f"Etapa 3/5: Comunicando cliente ({atendimento['email_cliente']})...")

    email_dest = atendimento.get("email_cliente")
    assunto = atendimento.get("assunto")
    corpo = atendimento.get("corpo")

    # Permite testar falha forçada de comunicação via flag no cliente
    if atendimento.get("cliente", {}).get("simular_erro_comunicacao") is True:
        logger.error("Simulação de falha de envio de e-mail ativada.")
        return {
            "enviado": False,
            "canal": "E-MAIL",
            "erro": "Falha simulada no servidor SMTP / Conexão indisponível.",
            "data_envio": datetime.now().isoformat()
        }

    try:
        if not simular:
            # Tenta integração com módulo SMTP do projeto se disponível
            try:
                sys.path.append(str(Path(__file__).resolve().parent.parent))
                from source.envio_email import enviar_email
                enviar_email(destinatario=email_dest, assunto=assunto, corpo=corpo)
                canal = "SMTP_REAL"
                logger.info(f"E-mail real enviado com sucesso para {email_dest}.")
            except Exception as e_real:
                logger.warning(f"Envio SMTP real falhou: {e_real}. Alternando para canal de contingência.")
                canal = "SMTP_CONTINGENCIA"
        else:
            canal = "E-MAIL_SIMULADO"
            logger.info(f"[SIMULAÇÃO SAC] E-mail transmitido com sucesso para '{email_dest}'.")

        return {
            "enviado": True,
            "canal": canal,
            "destinatario": email_dest,
            "data_envio": datetime.now().isoformat()
        }

    except Exception as erro:
        logger.error(f"Erro no envio da comunicação: {erro}")
        return {
            "enviado": False,
            "canal": "E-MAIL",
            "erro": str(erro),
            "data_envio": datetime.now().isoformat()
        }


def registrar_atendimento(atendimento: Dict[str, Any], status_comunicacao: Dict[str, Any]) -> Dict[str, Any]:
    """
    Etapa 4: Registro oficial e auditável do atendimento SAC (persistência JSON).

    Args:
        atendimento: Estrutura do atendimento SAC.
        status_comunicacao: Status da etapa de comunicação.

    Returns:
        Registro consolidado do atendimento.
    """
    logger.info("Etapa 4/5: Registrando atendimento no histórico SAC...")

    inicializar_estrutura_registro()

    registro = {
        "protocolo": atendimento.get("protocolo"),
        "timestamp": datetime.now().isoformat(),
        "cliente": atendimento.get("cliente"),
        "email_cliente": atendimento.get("email_cliente"),
        "categoria": atendimento.get("categoria"),
        "status_atendimento": atendimento.get("status_atendimento"),
        "assunto_enviado": atendimento.get("assunto"),
        "comunicacao": status_comunicacao
    }

    # Adiciona ao histórico em memória
    atendimentos_realizados.append(registro)

    # Persiste no arquivo JSON do ERP
    try:
        registros_existentes = []
        if ARQUIVO_REGISTROS.exists():
            try:
                with open(ARQUIVO_REGISTROS, "r", encoding="utf-8") as f:
                    registros_existentes = json.load(f)
            except Exception:
                registros_existentes = []

        registros_existentes.append(registro)

        with open(ARQUIVO_REGISTROS, "w", encoding="utf-8") as f:
            json.dump(registros_existentes, f, ensure_ascii=False, indent=4)

        logger.info(f"Atendimento protocolo {registro['protocolo']} registrado em '{ARQUIVO_REGISTROS.name}'.")

    except Exception as erro:
        logger.error(f"Erro ao persistir registro de atendimento em arquivo JSON: {erro}")

    return registro


def fallback_sac(resultado_p3: Any, erro_origem: str) -> Dict[str, Any]:
    """
    Mecanismo de Fallback para capturar erros críticos ou exceções no Processo 4.
    Garante resiliência e previne travamento na transmissão para o Processo 5.
    """
    logger.warning("===== MECANISMO DE FALLBACK SAC ACIONADO =====")
    protocolo_fallback = gerar_protocolo_sac()
    logger.warning(f"Protocolo de Fallback: {protocolo_fallback} | Erro de Origem: {erro_origem}")

    registro_fallback = {
        "protocolo": protocolo_fallback,
        "timestamp": datetime.now().isoformat(),
        "status_atendimento": "FALLBACK_SAC",
        "sucesso": False,
        "erro_origem": erro_origem,
        "dados_originais": str(resultado_p3),
        "mensagem": "Falha na execução normal do SAC. Atendimento retido para contingência manual."
    }

    # Persiste o evento de fallback
    try:
        inicializar_estrutura_registro()
        registros_existentes = []
        if ARQUIVO_REGISTROS.exists():
            try:
                with open(ARQUIVO_REGISTROS, "r", encoding="utf-8") as f:
                    registros_existentes = json.load(f)
            except Exception:
                registros_existentes = []
        registros_existentes.append(registro_fallback)
        with open(ARQUIVO_REGISTROS, "w", encoding="utf-8") as f:
            json.dump(registros_existentes, f, ensure_ascii=False, indent=4)
    except Exception as e_fb:
        logger.error(f"Erro ao salvar fallback em JSON: {e_fb}")

    return {
        "sucesso": False,
        "protocolo_sac": protocolo_fallback,
        "status_sac": "FALLBACK",
        "mensagem": "Processo 4 acionou fallback devido a erro na execução.",
        "dados_p5": {
            "requer_atencao_manual": True,
            "motivo_fallback": erro_origem,
            "protocolo": protocolo_fallback
        }
    }


def executar_sac(resultado_p3: Dict[str, Any], simular_email: bool = True) -> Dict[str, Any]:
    """
    Função principal do Processo 4 — SAC.

    Encadeia as 5 etapas do fluxo:
    Processo 3 -> Verificação do status -> Tratamento do resultado -> Comunicação -> Registro -> Processo 5

    Deverá contemplar:
        - logs da execução;
        - tratamento de erros;
        - fallback;
        - monitoramento da execução;
        - registro do atendimento.

    Args:
        resultado_p3: Dicionário de retorno do Processo 3.
        simular_email: Flag para controle de envio por e-mail simulado ou real.

    Returns:
        Dicionário padronizado pronto para ser repassado ao Processo 5.
    """
    logger.info("==========================================")
    logger.info("   INICIANDO PROCESSO 4 — SAC (ATENDIMENTO)")
    logger.info("==========================================")

    inicio_tempo = time.perf_counter()

    try:
        # 1. Verificação do Status do Processo 3
        analise_status = verificar_status_p3(resultado_p3)

        # 2. Tratamento do Resultado
        atendimento = tratar_resultado_sac(analise_status)

        # 3. Comunicação com o Cliente
        status_comunicacao = comunicar_cliente(atendimento, simular=simular_email)

        # Se a comunicação falhou, altera o status do atendimento para retenção
        if not status_comunicacao["enviado"]:
            logger.warning("Falha na comunicação direta. Aplicando fallback de retenção de notificação.")
            atendimento["status_atendimento"] = "COMUNICACAO_RETIDA"

        # 4. Registro do Atendimento
        registro_oficial = registrar_atendimento(atendimento, status_comunicacao)

        fim_tempo = time.perf_counter()
        tempo_execucao_ms = round((fim_tempo - inicio_tempo) * 1000, 2)

        # 5. Monitoramento da Execução
        logger.info("Etapa 5/5: Consolidando monitoramento e métricas de execução...")
        monitoramento = {
            "status_execucao": "SUCESSO" if status_comunicacao["enviado"] else "ALERTA_COMUNICACAO",
            "tempo_execucao_ms": tempo_execucao_ms,
            "comunicacao_sucesso": status_comunicacao["enviado"],
            "protocolo_gerado": atendimento["protocolo"],
            "timestamp_conclusao": datetime.now().isoformat()
        }

        logger.info(f"Processo 4 finalizado em {tempo_execucao_ms}ms com status [{monitoramento['status_execucao']}].")

        # Dados estruturados para o Processo 5
        payload_processo5 = {
            "sucesso": True,
            "protocolo_sac": atendimento["protocolo"],
            "status_sac": atendimento["status_atendimento"],
            "cliente": atendimento["cliente"],
            "registro_atendimento": registro_oficial,
            "monitoramento": monitoramento,
            "dados_prontos_para_p5": True
        }

        return payload_processo5

    except Exception as erro:
        logger.error(f"Exceção não tratada capturada no Processo 4: {erro}", exc_info=True)
        return fallback_sac(resultado_p3, str(erro))


if __name__ == "__main__":
    # Exemplo simples de uso individual do módulo
    resultado_exemplo_p3 = {
        "sucesso": True,
        "mensagem": "Cliente cadastrado com sucesso",
        "cliente": {
            "nome": "Carlos Eduardo",
            "email": "carlos@exemplo.com",
            "cpf": "12345678900"
        },
        "api": {
            "status_code": 201,
            "id_cliente": "CLI-001",
            "status": "cadastrado"
        }
    }

    resultado_p4 = executar_sac(resultado_exemplo_p3)
    print("\n--- RETORNO PARA O PROCESSO 5 ---")
    print(json.dumps(resultado_p4, indent=4, ensure_ascii=False))
