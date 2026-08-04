import unittest
from pathlib import Path
import sys
import shutil

# Permite importar do diretório source
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "source"))

from organizacao.arquivamento import calcular_hash_arquivo, arquivar_pasta_local

class TestArquivamento(unittest.TestCase):
    def setUp(self):
        self.diretorio_base = Path(__file__).resolve().parent / "arquivamento_teste"
        self.diretorio_base.mkdir(exist_ok=True)
        
        self.pasta_origem = self.diretorio_base / "pasta_origem"
        self.pasta_destino_base = self.diretorio_base / "pasta_arquivados"
        
        self.pasta_origem.mkdir(exist_ok=True)
        self.pasta_destino_base.mkdir(exist_ok=True)
        
        self.arquivo_teste = self.pasta_origem / "documento.pdf"
        self.arquivo_teste.write_text("conteudo para gerar hash", encoding="utf-8")

    def tearDown(self):
        if self.diretorio_base.exists():
            shutil.rmtree(self.diretorio_base)

    def test_calcular_hash_arquivo(self):
        hash_result = calcular_hash_arquivo(self.arquivo_teste)
        # O hash SHA-256 para "conteudo para gerar hash" deve ser consistente
        import hashlib
        h = hashlib.sha256(b"conteudo para gerar hash").hexdigest()
        self.assertEqual(hash_result, h)

    def test_arquivar_pasta_local(self):
        origem = self.pasta_origem
        destino_base = self.pasta_destino_base
        
        caminho_final = arquivar_pasta_local(origem, destino_base)
        self.assertTrue(caminho_final.exists())
        self.assertFalse(origem.exists()) # A pasta original foi movida
        self.assertEqual(caminho_final.name, "pasta_origem")
        
        # Testar colisão (duplicidade no destino)
        # Cria outra pasta com o mesmo nome na origem
        nova_origem = self.diretorio_base / "pasta_origem"
        nova_origem.mkdir(exist_ok=True)
        (nova_origem / "doc.txt").write_text("outro arquivo", encoding="utf-8")
        
        caminho_final_dup = arquivar_pasta_local(nova_origem, destino_base)
        self.assertTrue(caminho_final_dup.exists())
        self.assertIn("pasta_origem_dup", caminho_final_dup.name)

if __name__ == "__main__":
    unittest.main()
