"""
Módulo de integração com a Google Drive API — Processo 1 (Atendimento).

Responsável por:
1. Autenticar usando credentials.json (OAuth2) e gerar token.json.
2. Localizar ou criar a estrutura de pastas no Google Drive:
   ERP_Portal_Fake/
   ├── Downloads/
   ├── Documentos_OK/
   ├── Documentos_Pendentes/
   └── Encaminhados/
3. Criar subpastas de solicitações no Google Drive.
4. Fazer upload de arquivos para essas pastas.
5. Mover pastas entre categorias (Downloads -> OK/Pendente -> Encaminhados)
   atualizando os parents na API do Google Drive.
"""

import logging
import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

# Escopos necessários para acessar o Google Drive (leitura e gravação de arquivos)
SCOPES = ["https://www.googleapis.com/auth/drive"]

def obter_servico_drive() -> build:
    """
    Autentica o usuário e retorna o serviço da Google Drive API.
    Utiliza credentials.json e gera/reutiliza token.json.
    """
    raiz_projeto = Path(__file__).resolve().parent.parent.parent
    caminho_credenciais = raiz_projeto / "credentials.json"
    caminho_token = raiz_projeto / "token.json"

    creds = None
    if caminho_token.exists():
        creds = Credentials.from_authorized_user_file(str(caminho_token), SCOPES)

    # Se não houver credenciais válidas, realiza o login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Atualizando token de acesso do Google Drive expirado...")
            creds.refresh(Request())
        else:
            if not caminho_credenciais.exists():
                raise FileNotFoundError(
                    f"Arquivo credentials.json não encontrado em {caminho_credenciais}. "
                    "Por favor, siga as instruções para baixar as credenciais OAuth do Google Cloud."
                )
            logger.info("Iniciando fluxo de autenticação do Google Drive (OAuth2)...")
            flow = InstalledAppFlow.from_client_secrets_file(str(caminho_credenciais), SCOPES)
            # Executa o servidor local para autenticação automática no navegador
            creds = flow.run_local_server(port=0)
        
        # Salva as credenciais para as próximas execuções
        with open(caminho_token, "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def obter_ou_criar_pasta(servico, nome_pasta: str, parent_id: str | None = None) -> str:
    """
    Busca uma pasta pelo nome e ID do pai. Se não existir, cria.
    Retorna o ID da pasta.
    """
    query = f"name = '{nome_pasta}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    else:
        query += " and 'root' in parents"

    resultados = servico.files().list(q=query, fields="files(id, name)").execute()
    arquivos = resultados.get("files", [])

    if arquivos:
        return arquivos[0]["id"]

    # Se não encontrar, cria a pasta
    metadados = {
        "name": nome_pasta,
        "mimeType": "application/vnd.google-apps.folder"
    }
    if parent_id:
        metadados["parents"] = [parent_id]

    pasta = servico.files().create(body=metadados, fields="id").execute()
    logger.info("Pasta criada no Google Drive: %s (ID: %s)", nome_pasta, pasta["id"])
    return pasta["id"]


def inicializar_estrutura_erp(servico) -> dict[str, str]:
    """
    Garante que a estrutura de pastas ERP no Google Drive esteja criada.
    Retorna um dicionário com os IDs das pastas.
    """
    id_raiz = obter_ou_criar_pasta(servico, "ERP_Portal_Fake")
    
    pastas = {}
    for subpasta in ["Downloads", "Documentos_OK", "Documentos_Pendentes", "Encaminhados"]:
        pastas[subpasta] = obter_ou_criar_pasta(servico, subpasta, id_raiz)
        
    return pastas


def upload_arquivo(servico, caminho_local: Path, folder_id: str) -> str:
    """
    Faz upload de um arquivo local para uma pasta específica do Google Drive.
    Retorna o ID do arquivo no Google Drive.
    """
    metadados = {
        "name": caminho_local.name,
        "parents": [folder_id]
    }
    
    media = MediaFileUpload(str(caminho_local), resumable=True)
    
    arquivo = servico.files().create(
        body=metadados,
        media_body=media,
        fields="id"
    ).execute()
    
    logger.info("Upload concluído: %s -> ID: %s", caminho_local.name, arquivo["id"])
    return arquivo["id"]


def mover_pasta_drive(servico, folder_id: str, old_parent_id: str, new_parent_id: str) -> None:
    """
    Move uma pasta no Google Drive atualizando seus parents.
    """
    # Recupera os pais anteriores
    arquivo = servico.files().get(fileId=folder_id, fields="parents").execute()
    parents_atuais = ",".join(arquivo.get("parents", []))
    
    if not parents_atuais:
        parents_atuais = old_parent_id

    # Atualiza os pais
    servico.files().update(
        fileId=folder_id,
        addParents=new_parent_id,
        removeParents=parents_atuais,
        fields="id, parents"
    ).execute()
    
    logger.info("Pasta de ID %s movida no Google Drive.", folder_id)
