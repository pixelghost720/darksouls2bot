FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY init-model.sh /app/init-model.sh

RUN sed -i 's/\r$//' /app/init-model.sh && \
    chmod +x /app/init-model.sh

# Create the images directory
RUN mkdir -p /app/images

CMD ["/app/init-model.sh"]
