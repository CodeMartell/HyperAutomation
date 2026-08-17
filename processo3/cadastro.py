import logging


# Configuração dos logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Banco de clientes simulado
clientes_cadastrados = []


def validar_cliente(cliente):
    """
    Valida os dados recebidos do Processo 2.
    """

    logger.info("Iniciando validação dos dados do cliente.")

    campos_obrigatorios = ["nome", "email", "cpf"]

    for campo in campos_obrigatorios:
        if campo not in cliente or not cliente[campo]:
            logger.error(f"Campo obrigatório ausente: {campo}")
            return False

    logger.info("Dados do cliente validados com sucesso.")

    return True


def verificar_duplicidade(cliente):
    """
    Verifica se o CPF já está cadastrado.
    """

    logger.info("Verificando se o cliente já está cadastrado.")

    for cliente_cadastrado in clientes_cadastrados:
        if cliente_cadastrado["cpf"] == cliente["cpf"]:
            logger.warning(
                f"Cliente já cadastrado: CPF {cliente['cpf']}"
            )
            return True

    logger.info("Cliente não encontrado. Cadastro permitido.")

    return False


def integrar_api_cadastro(cliente):
    """
    Simula integração com uma API externa de cadastro.
    Também permite simular uma falha para testar o fallback.
    """

    logger.info("Enviando dados do cliente para API de cadastro.")

    try:
        # Simulação de falha da API para testes
        if cliente.get("simular_erro_api") is True:
            raise ConnectionError("API de cadastro indisponível.")

        # Resposta simulada de sucesso da API
        resposta_api = {
            "status_code": 201,
            "id_cliente": f"CLI-{len(clientes_cadastrados) + 1:03}",
            "status": "cadastrado"
        }

        logger.info(
            f"API confirmou o cadastro. "
            f"ID gerado: {resposta_api['id_cliente']}"
        )

        return resposta_api

    except Exception as erro:
        logger.error(f"Erro na integração com API: {erro}")
        return None


def cadastrar_cliente(cliente):
    """
    Realiza o cadastro utilizando a API simulada.
    """

    logger.info(f"Iniciando cadastro do cliente: {cliente['nome']}")

    try:
        # Chamada para a API
        resposta_api = integrar_api_cadastro(cliente)

        if resposta_api is None:
            raise Exception("Falha na comunicação com a API.")

        # Adiciona o cliente no banco local simulado
        cliente_completo = cliente.copy()

        cliente_completo["id_cliente"] = resposta_api["id_cliente"]

        clientes_cadastrados.append(cliente_completo)

        logger.info(
            f"Cliente {cliente['nome']} cadastrado com sucesso."
        )

        return {
            "sucesso": True,
            "mensagem": "Cliente cadastrado com sucesso",
            "cliente": cliente_completo,
            "api": resposta_api
        }

    except Exception as erro:
        logger.error(f"Erro durante o cadastro: {erro}")

        return {
            "sucesso": False,
            "mensagem": "Erro ao realizar cadastro",
            "erro": str(erro),
            "cliente": cliente
        }


def fallback_cadastro(cliente):
    """
    Fallback utilizado quando ocorre uma falha no cadastro.
    """

    logger.warning(
        f"Fallback acionado para o cliente: "
        f"{cliente.get('nome', 'Desconhecido')}"
    )

    return {
        "sucesso": False,
        "mensagem": "Cadastro não realizado. Fallback acionado.",
        "cliente": cliente
    }


def executar_cadastro(cliente):
    """
    Função principal do Processo 3.
    """

    logger.info("===== PROCESSO 3 - CADASTRO =====")

    try:

        # 1. Validar dados
        if not validar_cliente(cliente):
            return {
                "sucesso": False,
                "mensagem": "Dados inválidos",
                "cliente": cliente
            }

        # 2. Verificar duplicidade
        if verificar_duplicidade(cliente):
            return {
                "sucesso": False,
                "mensagem": "Cliente já cadastrado",
                "cliente": cliente
            }

        # 3. Cadastro com integração API
        resultado = cadastrar_cliente(cliente)

        # 4. Fallback
        if not resultado["sucesso"]:
            return fallback_cadastro(cliente)

        logger.info("Processo 3 concluído com sucesso.")

        return resultado

    except Exception as erro:

        logger.error(
            f"Erro inesperado no Processo 3: {erro}"
        )

        return fallback_cadastro(cliente)