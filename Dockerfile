FROM python:3.11.5-alpine

WORKDIR /app

RUN apk add --no-cache build-base libffi-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app.main:app"]

