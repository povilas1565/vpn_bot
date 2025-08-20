FROM python:3.11-slim

# Системные пакеты: wireguard-tools (wg), ssh-клиент
RUN apt-get update && apt-get install -y --no-install-recommends \
    wireguard-tools openssh-client curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY . .

# Порт FastAPI (внутренний, не наружу)
EXPOSE 8084

# Запуск бота + uvicorn
CMD ["python", "main.py"]

