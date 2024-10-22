FROM ubuntu:20.04

RUN apt update && \
    apt install -y sudo \
                   bash \
                   build-essential \
                   git \
                   curl \
                   ca-certificates \
                   python3 \
                   python3-dev \
                   python3-pip \
                   libpq-dev

WORKDIR /work
COPY experiments ./experiments
COPY Makefile poetry.lock pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry
# Create virtualenv at .venv in the project instead of ~/.cache/
RUN poetry config virtualenvs.in-project true
# Install production dependencies
RUN poetry install --no-dev --no-ansi

CMD ["make", "run"]
