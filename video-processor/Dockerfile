FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    && pip install opencv-python-headless

COPY main.py /app/main.py

WORKDIR /app
CMD ["python", "main.py"]
