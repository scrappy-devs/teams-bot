FROM python:3.15-rc-slim

WORKDIR /app
COPY . /app

# ARG TOKEN
# ENV TOKEN=$TOKEN

# Install build tools and libraries required for aiohttp
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
