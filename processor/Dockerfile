FROM jrottenberg/ffmpeg:4.1-nvidia

USER root
RUN apt-get update && apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
ENTRYPOINT []
# CMD ["bash"]
CMD ["python3", "main.py"]