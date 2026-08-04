"""
Módulo de validação de regras de negócio — Processo 2 (Organização de Dados).
"""

import re
from datetime import datetime

def validar_cpf(cpf_str: str) -> bool:
    """
    Valida um CPF brasileiro usando a regra dos dígitos verificadores.
    """
    # Remove formatação (. e -)
    cpf = re.sub(r'\D', '', cpf_str)

    if len(cpf) != 11:
        return False

    # CPFs com todos os números iguais são inválidos
    if cpf == cpf[0] * 11:
        return False

    # Primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito_1 = 0 if resto in (10, 11) else resto

    if int(cpf[9]) != digito_1:
        return False

    # Segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito_2 = 0 if resto in (10, 11) else resto

    if int(cpf[10]) != digito_2:
        return False

    return True

def validar_email(email: str) -> bool:
    """Valida o formato de e-mail usando expressão regular."""
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(padrao, email.strip()))

def validar_telefone(telefone_str: str) -> bool:
    """Valida o telefone, aceitando formatos com DDD (10 ou 11 dígitos)."""
    tel = re.sub(r'\D', '', telefone_str)
    # Geralmente, telefones no Brasil têm DDD + 8 ou 9 dígitos (total de 10 ou 11 dígitos)
    return len(tel) in (10, 11)

def validar_data_nascimento(data_str: str) -> tuple[bool, str]:
    """
    Valida a data de nascimento.
    
    Returns:
        tuple: (bool, str) -> (Validade, Mensagem de erro)
    """
    try:
        data_nasc = datetime.strptime(data_str.strip(), "%d/%m/%Y")
    except ValueError:
        return False, "Formato inválido (esperado DD/MM/AAAA)"

    hoje = datetime.now()
    if data_nasc > hoje:
        return False, "Data de nascimento está no futuro"

    # Regra de negócio: idade mínima de 18 anos e idade máxima razoável (115 anos)
    idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    
    if idade < 18:
        return False, f"Cliente menor de idade ({idade} anos)"
    if idade > 115:
        return False, f"Idade inconsistente ({idade} anos)"

    return True, ""

def validar_dados_cliente(dados: dict) -> tuple[bool, list[str]]:
    """
    Realiza a validação completa de um dicionário contendo os dados do cliente.
    
    Args:
        dados: Dicionário retornado pela extração.
        
    Returns:
        tuple: (bool, list[str]) -> (Se é válido, Lista com mensagens de erro)
    """
    erros = []
    
    campos_obrigatorios = ["nome", "sobrenome", "cpf", "email", "telefone", "data_nascimento", "endereco"]
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            erros.append(f"Campo obrigatório ausente ou vazio: '{campo}'")

    # Se já houver campos ausentes básicos, retorna logo
    if erros:
        return False, erros

    # Validações detalhadas
    if not validar_cpf(dados["cpf"]):
        erros.append(f"CPF inválido: '{dados['cpf']}'")
        
    if not validar_email(dados["email"]):
        erros.append(f"E-mail inválido: '{dados['email']}'")
        
    if not validar_telefone(dados["telefone"]):
        erros.append(f"Telefone inválido: '{dados['telefone']}'")
        
    data_valida, msg_erro_data = validar_data_nascimento(dados["data_nascimento"])
    if not data_valida:
        erros.append(f"Data de nascimento inválida: '{dados['data_nascimento']}' ({msg_erro_data})")
        
    if len(dados["endereco"].strip()) < 5:
        erros.append(f"Endereço curto demais: '{dados['endereco']}'")

    return len(erros) == 0, erros
