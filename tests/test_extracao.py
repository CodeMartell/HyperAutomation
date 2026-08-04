import unittest
from pathlib import Path
import sys

# Permite importar do diretório source
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "source"))

from organizacao.extracao_dados import parse_campos_cadastro, extrair_dados_simulados_de_fallback

class TestExtracaoDados(unittest.TestCase):
    def test_parse_campos_cadastro_valido(self):
        texto = (
            "Nome: João\n"
            "Sobrenome: Silva\n"
            "CPF: 123.456.789-00\n"
            "E-mail: joao@exemplo.com\n"
            "Telefone: (92) 99999-9999\n"
            "Data de nascimento: 01/01/2000\n"
            "Endereço: Rua das Flores, 123"
        )
        dados = parse_campos_cadastro(texto)
        self.assertEqual(dados["nome"], "João")
        self.assertEqual(dados["sobrenome"], "Silva")
        self.assertEqual(dados["cpf"], "123.456.789-00")
        self.assertEqual(dados["email"], "joao@exemplo.com")
        self.assertEqual(dados["telefone"], "(92) 99999-9999")
        self.assertEqual(dados["data_nascimento"], "01/01/2000")
        self.assertEqual(dados["endereco"], "Rua das Flores, 123")

    def test_parse_campos_cadastro_parcial(self):
        texto = (
            "Nome: Maria\n"
            "CPF: 999.999.999-99\n"
        )
        dados = parse_campos_cadastro(texto)
        self.assertEqual(dados["nome"], "Maria")
        self.assertEqual(dados["sobrenome"], "")
        self.assertEqual(dados["cpf"], "999.999.999-99")
        self.assertEqual(dados["email"], "")

    def test_fallback_simulado_joao(self):
        p = Path("dummy_joao.pdf")
        texto = extrair_dados_simulados_de_fallback(p)
        self.assertIn("João", texto)
        self.assertIn("Silva", texto)
        self.assertIn("123.456.789-00", texto)

if __name__ == "__main__":
    unittest.main()
