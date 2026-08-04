import unittest
from pathlib import Path
import sys
import os

# Permite importar do diretório source
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "source"))

from organizacao.planilha_mestra import inicializar_planilha, checar_duplicado_hash, adicionar_registro

class TestPlanilhaMestra(unittest.TestCase):
    def setUp(self):
        self.caminho_teste = Path(__file__).resolve().parent / "planilha_teste.xlsx"
        if self.caminho_teste.exists():
            self.caminho_teste.unlink()

    def tearDown(self):
        if self.caminho_teste.exists():
            self.caminho_teste.unlink()

    def test_inicializacao_e_cabecalho(self):
        inicializar_planilha(self.caminho_teste)
        self.assertTrue(self.caminho_teste.exists())
        
        # Testar se duplicado retorna falso para hash inexistente
        self.assertFalse(checar_duplicado_hash(self.caminho_teste, "hash_inexistente"))

    def test_adicao_registro_e_duplicidade(self):
        inicializar_planilha(self.caminho_teste)
        
        dados = {
            "nome": "João",
            "sobrenome": "Silva",
            "cpf": "123.456.789-00",
            "email": "joao@exemplo.com",
            "telefone": "(92) 99999-9999",
            "data_nascimento": "01/01/2000",
            "endereco": "Rua das Flores, 123"
        }
        hash_mock = "abcdef1234567890"
        
        adicionar_registro(
            caminho_local=self.caminho_teste,
            dados=dados,
            hash_ficha=hash_mock,
            status="VALIDADO",
            erros=[],
            nome_ficha="ficha_joao.pdf"
        )
        
        # Agora o hash deve constar como duplicado!
        self.assertTrue(checar_duplicado_hash(self.caminho_teste, hash_mock))
        # Hash diferente não deve ser duplicado
        self.assertFalse(checar_duplicado_hash(self.caminho_teste, "outro_hash"))

if __name__ == "__main__":
    unittest.main()
