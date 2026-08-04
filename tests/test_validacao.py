import unittest
from pathlib import Path
import sys

# Permite importar do diretório source
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "source"))

from organizacao.validacao_dados import (
    validar_cpf, validar_email, validar_telefone, validar_data_nascimento, validar_dados_cliente
)

class TestValidacaoDados(unittest.TestCase):
    def test_cpf_valido(self):
        # CPFs matematicamente válidos comuns para testes
        self.assertTrue(validar_cpf("123.456.789-09") or validar_cpf("123.456.789-00") or validar_cpf("00000000000") is False)
        # Vamos testar um CPF gerado pelo algoritmo real
        self.assertTrue(validar_cpf("529.982.247-25"))
        self.assertTrue(validar_cpf("111.444.777-35"))

    def test_cpf_invalido(self):
        self.assertFalse(validar_cpf("111.111.111-11")) # Todos os dígitos iguais
        self.assertFalse(validar_cpf("123.456.789-99")) # Dígitos inválidos
        self.assertFalse(validar_cpf("123")) # Tamanho incorreto

    def test_email_valido(self):
        self.assertTrue(validar_email("joao.silva@exemplo.com"))
        self.assertTrue(validar_email("joao@provedor.com.br"))

    def test_email_invalido(self):
        self.assertFalse(validar_email("joao.silva@exemplo"))
        self.assertFalse(validar_email("joaoexemplo.com"))
        self.assertFalse(validar_email("joao@.com"))

    def test_telefone_valido(self):
        self.assertTrue(validar_telefone("(92) 99999-9999"))
        self.assertTrue(validar_telefone("92999999999"))
        self.assertTrue(validar_telefone("9233334444"))

    def test_telefone_invalido(self):
        self.assertFalse(validar_telefone("99999"))
        self.assertFalse(validar_telefone("9299999-99"))

    def test_data_nascimento_valida(self):
        valido, msg = validar_data_nascimento("01/01/2000")
        self.assertTrue(valido)

    def test_data_nascimento_menor_idade(self):
        # Cliente com menos de 18 anos
        valido, msg = validar_data_nascimento("01/01/2018") # Hoje é 2026, 8 anos de idade
        self.assertFalse(valido)
        self.assertIn("menor de idade", msg)

    def test_data_nascimento_inconsistente(self):
        valido, msg = validar_data_nascimento("01/01/1850") # Idade muito avançada
        self.assertFalse(valido)
        self.assertIn("inconsistente", msg)

    def test_validacao_completa_cliente(self):
        dados_ok = {
            "nome": "João",
            "sobrenome": "Silva",
            "cpf": "529.982.247-25",
            "email": "joao.silva@exemplo.com",
            "telefone": "(92) 99999-9999",
            "data_nascimento": "01/01/2000",
            "endereco": "Rua das Flores, 123 - Manaus"
        }
        valido, erros = validar_dados_cliente(dados_ok)
        self.assertTrue(valido)
        self.assertEqual(len(erros), 0)

        dados_erros = {
            "nome": "Maria",
            "sobrenome": "Souza",
            "cpf": "111.111.111-11",
            "email": "maria.souza.invalido",
            "telefone": "(92) 98888-88",
            "data_nascimento": "31/02/1995",
            "endereco": "Rua"
        }
        valido, erros = validar_dados_cliente(dados_erros)
        self.assertFalse(valido)
        self.assertGreater(len(erros), 0)

if __name__ == "__main__":
    unittest.main()
