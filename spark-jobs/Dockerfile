FROM apache/spark:3.5.0

USER root

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1 \
    && rm -rf /var/lib/apt/lists/*

# RUN ln -sf /usr/bin/python3 /usr/bin/python && \
#     ln -sf /usr/bin/pip3 /usr/bin/pip

COPY requirements.txt /opt/app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /opt/app/requirements.txt

WORKDIR /opt/app
COPY frame-processor.py /opt/app/frame-processor.py

ENTRYPOINT ["/opt/spark/bin/spark-submit", "--master", "local[*]", "/opt/app/frame-processor.py"]
