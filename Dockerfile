# 1. Imagem base oficial do Python
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Variáveis de ambiente para execução otimizada do Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 4. Atualiza o gerenciador de pacotes e instala dependências básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia o arquivo de dependências e instala os pacotes Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Instala o navegador Chromium e suas dependências de sistema para o Playwright
RUN playwright install --with-deps chromium

# 7. Copia todo o código da aplicação para o container
COPY . .

# 8. Define o comando padrão de execução (inicia o orquestrador principal)
CMD ["python", "source/main.py"]
