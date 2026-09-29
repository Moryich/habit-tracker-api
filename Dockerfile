FROM python:3.14-slim

WORKDIR /app

RUN useradd --create-home --shell /bin/bash worker_user

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=worker_user:worker_user . .

USER worker_user

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
