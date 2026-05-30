FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install uv
RUN uv sync

CMD ["uv", "run", "uvicorn", "main_beta:app", "--host", "0.0.0.0", "--port", "8000"]
