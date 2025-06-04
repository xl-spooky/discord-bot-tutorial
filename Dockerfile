FROM python:3.11

RUN apt update && apt install -y python3-pip python3-wheel gcc

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.toml setup.cfg .python-version /app/

RUN poetry install --no-root

COPY . /app/

CMD ["poetry", "run", "python3", "-m", "tutorialbot.bot"]
