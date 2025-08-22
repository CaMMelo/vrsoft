# ================================================
# Estágio base (comum a todos os serviços)
# ================================================
FROM python:3.13 AS base

# Instala o Poetry de forma segura e isolada
RUN curl -sSL https://install.python-poetry.org | python3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH="/root/.local/bin:${PATH}"


# Configura diretório de trabalho
WORKDIR /code

# Copia arquivos de dependências primeiro (melhor para cache)
COPY pyproject.toml poetry.lock README.md ./

# ================================================
# Estágio de desenvolvimento (com dependências completas)
# ================================================
FROM base AS dev

# Copia código fonte
COPY src/backend ./src/backend

# Instala todas as dependências (incluindo dev)
RUN poetry install && rm -rf $POETRY_CACHE_DIR

# ================================================
# Estágio de produção
# ================================================
FROM base AS prod

# Copia código fonte
COPY src/backend ./src/backend

# Instala as dependencias de produção
RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

