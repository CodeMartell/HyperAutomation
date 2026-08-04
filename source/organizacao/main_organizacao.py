"""
HyperAutomation — Orquestrador do Processo 2 (Setor de Organização de Dados).

Fluxo completo:
    1. Localizar documentos aprovados (Documentos_OK/ ou Encaminhados/)
    2. Baixar/Acessar arquivos (local ou via Google Drive API)
    3. Extrair dados da Ficha de Cadastro (texto nativo ou OCR)
    4. Validar os dados conforme regras de negócio (CPF, e-mail, idade, etc.)
    5. Preencher a Planilha Mestra (Planilha_Mestra.xlsx) com os dados
    6. Salvar e sincronizar a planilha (local e nuvem)
    7. Arquivar os documentos processados (mover para pasta Arquivados/)
    8. Evitar reprocessamento (idempotência por hash do arquivo)
"""

import logging
import sys
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Permite execução direta
_RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_RAIZ_PROJETO / "source"))
sys.path.insert(0, str(_RAIZ_PROJETO / "source" / "organizacao"))

from organizacao.config import (
    PASTA_ERP, PASTA_OK, PASTA_ENCAMINHADOS, PASTA_ARQUIVADOS,
    CAMINHO_PLANILHA, PASTA_SISTEMA_INTEGRADOR, USAR_DRIVE, garantir_pastas_locais
)
from organizacao.extracao_dados import extrair_dados_ficha
from organizacao.validacao_dados import validar_dados_cliente
from organizacao.planilha_mestra import (
    inicializar_planilha, checar_duplicado_hash, adicionar_registro,
    baixar_planilha_drive, subir_planilha_drive
)
from organizacao.arquivamento import calcular_hash_arquivo, arquivar_pasta_local, arquivar_pasta_drive

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            _RAIZ_PROJETO / "evidencias" / "organizacao.log",
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("main_organizacao")

def _banner(texto: str, largura: int = 60) -> None:
    print("=" * largura)
    print(f"  {texto}")
    print("=" * largura)

def obter_ficha_pdf(pasta: Path) -> Path | None:
    """Procura pelo arquivo da Ficha de Cadastro na pasta (busca palavras-chave)."""
    palavras_ficha = ["ficha", "cadastro", "formulario", "formulário"]
    for item in pasta.iterdir():
        if item.is_file() and item.suffix.lower() == ".pdf":
            nome_lower = item.name.lower()
            if any(p in nome_lower for p in palavras_ficha):
                return item
    # Se não encontrar por palavra-chave mas tiver apenas um PDF na pasta, assume ele
    pdfs = [f for f in pasta.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
    if len(pdfs) == 1:
        return pdfs[0]
    return None

def inicializar_estrutura_drive_processo2(servico) -> dict[str, str]:
    """Garante a estrutura de pastas ERP no Google Drive para o Processo 2."""
    from atendimento.google_drive import obter_ou_criar_pasta
    id_raiz = obter_ou_criar_pasta(servico, "ERP_Portal_Fake")
    
    pastas = {}
    for subpasta in ["Documentos_OK", "Encaminhados", "Sistema_Integrador_Portal_Fake", "Arquivados"]:
        pastas[subpasta] = obter_ou_criar_pasta(servico, subpasta, id_raiz)
        
    return pastas

def processar_pasta_local(pasta_cliente: Path) -> dict:
    """Processa um dossiê de cliente local."""
    logger.info("Processando pasta local: %s", pasta_cliente.name)
    ficha_pdf = obter_ficha_pdf(pasta_cliente)
    
    if not ficha_pdf:
        msg = f"Ficha de cadastro não encontrada na pasta {pasta_cliente.name}."
        logger.warning(msg)
        return {"status": "SKIPPED", "motivo": "Ficha de cadastro ausente"}

    # Passo 8: Idempotência via hash do arquivo
    hash_ficha = calcular_hash_arquivo(ficha_pdf)
    if checar_duplicado_hash(CAMINHO_PLANILHA, hash_ficha):
        logger.warning("Documento duplicado detectado (Hash: %s). Arquivando sem processar.", hash_ficha)
        arquivar_pasta_local(pasta_cliente, PASTA_ARQUIVADOS)
        return {"status": "DUPLICATE", "nome_cliente": pasta_cliente.name, "hash": hash_ficha}

    # Passo 3: Extração de Dados
    logger.info("Extraindo dados da ficha: %s", ficha_pdf.name)
    dados = extrair_dados_ficha(ficha_pdf)

    # Passo 4: Validação dos dados
    logger.info("Validando dados cadastrais...")
    valido, erros = validar_dados_cliente(dados)
    status_reg = "VALIDADO" if valido else "ERRO"

    # Passo 5: Atualização da Planilha Mestra
    adicionar_registro(
        caminho_local=CAMINHO_PLANILHA,
        dados=dados,
        hash_ficha=hash_ficha,
        status=status_reg,
        erros=erros,
        nome_ficha=ficha_pdf.name
    )

    # Passo 7: Arquivamento
    arquivar_pasta_local(pasta_cliente, PASTA_ARQUIVADOS)

    return {
        "status": status_reg,
        "nome_cliente": f"{dados.get('nome')} {dados.get('sobrenome')}",
        "hash": hash_ficha,
        "erros": erros
    }

def executar_processo_drive(servico, ids_pastas: dict[str, str]) -> list[dict]:
    """Varre as pastas OK e Encaminhados no Google Drive e as processa."""
    resultados = []
    
    # 1. Sincronizar planilha mestra do Drive para o local
    file_id_planilha = baixar_planilha_drive(servico, ids_pastas["Sistema_Integrador_Portal_Fake"], CAMINHO_PLANILHA)
    inicializar_planilha(CAMINHO_PLANILHA) # Garante que exista localmente

    # Procurar pastas de clientes em Documentos_OK e Encaminhados no Drive
    for pasta_origem_nome in ["Documentos_OK", "Encaminhados"]:
        origem_id = ids_pastas[pasta_origem_nome]
        query = f"'{origem_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        
        folders_list = servico.files().list(q=query, fields="files(id, name)").execute().get("files", [])
        
        for folder in folders_list:
            folder_id = folder["id"]
            folder_name = folder["name"]
            logger.info("[Drive] Dossiê encontrado: %s (ID: %s)", folder_name, folder_id)

            # Baixar arquivos da pasta no Drive para uma pasta local temporária
            temp_local_dir = PASTA_ERP / "Temp_Drive" / folder_name
            temp_local_dir.mkdir(parents=True, exist_ok=True)

            query_files = f"'{folder_id}' in parents and trashed = false"
            files_list = servico.files().list(q=query_files, fields="files(id, name)").execute().get("files", [])

            for f in files_list:
                f_id = f["id"]
                f_name = f["name"]
                # Baixar arquivo
                request = servico.files().get_media(fileId=f_id)
                import io
                from googleapiclient.http import MediaIoBaseDownload
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                (temp_local_dir / f_name).write_bytes(fh.getvalue())
                logger.info("[Drive] Arquivo baixado: %s", f_name)

            # Processar pasta local baixada temporariamente
            ficha_pdf = obter_ficha_pdf(temp_local_dir)
            if not ficha_pdf:
                logger.warning("[Drive] Ficha de cadastro não encontrada na pasta %s.", folder_name)
                shutil.rmtree(temp_local_dir)
                continue

            hash_ficha = calcular_hash_arquivo(ficha_pdf)
            
            # Idempotência
            if checar_duplicado_hash(CAMINHO_PLANILHA, hash_ficha):
                logger.warning("[Drive] Documento duplicado detectado (Hash: %s). Arquivando...", hash_ficha)
                arquivar_pasta_drive(servico, folder_id, origem_id, ids_pastas["Arquivados"])
                shutil.rmtree(temp_local_dir)
                resultados.append({"status": "DUPLICATE", "nome_cliente": folder_name, "hash": hash_ficha})
                continue

            dados = extrair_dados_ficha(ficha_pdf)
            valido, erros = validar_dados_cliente(dados)
            status_reg = "VALIDADO" if valido else "ERRO"

            # Escreve na planilha local
            adicionar_registro(
                caminho_local=CAMINHO_PLANILHA,
                dados=dados,
                hash_ficha=hash_ficha,
                status=status_reg,
                erros=erros,
                nome_ficha=ficha_pdf.name
            )

            # Move a pasta no Google Drive
            arquivar_pasta_drive(servico, folder_id, origem_id, ids_pastas["Arquivados"])

            # Limpa pasta local temporária
            shutil.rmtree(temp_local_dir)

            resultados.append({
                "status": status_reg,
                "nome_cliente": f"{dados.get('nome')} {dados.get('sobrenome')}",
                "hash": hash_ficha,
                "erros": erros
            })

    # Subir planilha de volta para o Drive
    subir_planilha_drive(servico, ids_pastas["Sistema_Integrador_Portal_Fake"], CAMINHO_PLANILHA, file_id_planilha)
    
    # Limpa diretório Temp_Drive se sobrar
    temp_root = PASTA_ERP / "Temp_Drive"
    if temp_root.exists():
        shutil.rmtree(temp_root)

    return resultados

def main() -> None:
    """Execução principal do orquestrador do Processo 2."""
    load_dotenv()
    _banner("HyperAutomation — Processo 2: Organização de Dados")

    # Criar pasta de evidências
    (_RAIZ_PROJETO / "evidencias").mkdir(exist_ok=True)

    drive_servico = None
    ids_pastas = None
    usar_drive = USAR_DRIVE

    if usar_drive:
        logger.info("Integração com Google Drive ATIVADA. Inicializando conexão...")
        from atendimento.google_drive import obter_servico_drive
        try:
            drive_servico = obter_servico_drive()
            ids_pastas = inicializar_estrutura_drive_processo2(drive_servico)
            logger.info("Estrutura do Google Drive inicializada com sucesso!")
        except Exception as e:
            logger.error("Erro ao inicializar o Google Drive: %s. Revertendo para local...", e)
            usar_drive = False

    resultados = []

    if usar_drive:
        resultados = executar_processo_drive(drive_servico, ids_pastas)
    else:
        garantir_pastas_locais()
        inicializar_planilha(CAMINHO_PLANILHA)

        # Varre pastas locais em Documentos_OK e Encaminhados
        pastas_varredura = [PASTA_OK, PASTA_ENCAMINHADOS]
        dossies_locais = []

        for pasta_dir in pastas_varredura:
            if pasta_dir.exists():
                for item in pasta_dir.iterdir():
                    if item.is_dir() and item.name != ".gitkeep":
                        dossies_locais.append(item)

        logger.info("Total de dossiês locais encontrados para processar: %d", len(dossies_locais))

        for pasta_cliente in dossies_locais:
            try:
                res = processar_pasta_local(pasta_cliente)
                resultados.append(res)
            except Exception as e:
                logger.error("Erro crítico ao processar pasta '%s': %s", pasta_cliente.name, e)

    # Exibir resumo da execução
    _banner("Resumo do Processo 2")
    print(f"  Total de dossiês processados: {len(resultados)}")
    validos = sum(1 for r in resultados if r["status"] == "VALIDADO")
    erros = sum(1 for r in resultados if r["status"] == "ERRO")
    duplicados = sum(1 for r in resultados if r["status"] == "DUPLICATE")
    skipped = sum(1 for r in resultados if r["status"] == "SKIPPED")
    
    print(f"  Dossiês Válidos:            {validos}")
    print(f"  Dossiês com Erros:          {erros}")
    print(f"  Dossiês Duplicados:         {duplicados}")
    print(f"  Dossiês Pulados/Ignorados:  {skipped}")
    print("=" * 60)

    for r in resultados:
        if r["status"] == "VALIDADO":
            print(f"  ✓ [VÁLIDO]  {r.get('nome_cliente')} (Hash: {r.get('hash')[:8]})")
        elif r["status"] == "ERRO":
            print(f"  ✗ [ERRO]    {r.get('nome_cliente')} | Erros: {', '.join(r.get('erros', []))}")
        elif r["status"] == "DUPLICATE":
            print(f"  ⚠ [DUPLICADO] {r.get('nome_cliente')} (Hash: {r.get('hash')[:8]}) -> Arquivado sem alteração")

    print(f"\n  Log salvo em: evidencias/organizacao.log")
    print("=" * 60)

if __name__ == "__main__":
    main()
