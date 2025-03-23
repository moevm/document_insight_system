# Используем более современный базовый образ
FROM python:3.9-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip setuptools && \
    pip install --prefer-binary -r /requirements.txt

# Копируем приложение
COPY app /app

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
WORKDIR /app

# Устанавливаем приложение в режиме разработки
RUN cd /usr/local/lib/python3.9/site-packages && \
    python /app/setup.py develop