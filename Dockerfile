FROM python:3.13-alpine AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --target=/app/vendor -r requirements.txt

FROM python:3.13-alpine

WORKDIR /application

COPY --from=builder /app/vendor /application/vendor

COPY . .

ENV PYTHONPATH=/application/vendor

EXPOSE 5000

CMD [ "python", "app.py" ]
