# 1. Imagem base oficial do Python
FROM python:3.14-slim

# 2. Define o diretório de trabalho no container
WORKDIR /app

# 3. Variáveis de ambiente para otimização do Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 4. Atualiza pacotes de sistema e instala ferramentas essenciais
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia o arquivo de dependências e instala pacotes Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Instala navegadores headless do Playwright
RUN playwright install --with-deps chromium

# 7. Copia todo o código-fonte da aplicação
COPY . .

# 8. Define o ponto de entrada principal (orquestrador dos 5 processos)
CMD ["python", "bot.py"]
