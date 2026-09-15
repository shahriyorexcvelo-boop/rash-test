FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PORT=8080

RUN pip install --no-cache-dir "aiogram>=3.15.0" "aiofiles>=24.1.0" "python-dotenv>=1.0.1" "requests>=2.32.3"

COPY . .

EXPOSE 8080

CMD ["python3", "test_bot.py"]
