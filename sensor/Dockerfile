FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir requests msgpack

CMD ["python", "sensor.py"]
