FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime
ARG DEBIAN_FRONTEND=noninteractive
ARG TEST_ENV

WORKDIR /app

RUN --mount=type=cache,target="/var/cache/apt",sharing=locked \
    --mount=type=cache,target="/var/lib/apt/lists",sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    git wget g++ freeglut3-dev build-essential libx11-dev \
    libxmu-dev libxi-dev libglu1-mesa libglu1-mesa-dev \
    libfreeimage-dev ffmpeg libsm6 libxext6 libffi-dev python3-dev python3-pip gcc \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_CACHE_DIR=/.cache \
    PORT=10011 \
    WORKERS=1 \
    THREADS=2 \
    CUDA_HOME=/usr/local/cuda \
    DEBUG=false

RUN apt-get update && apt-get install -y --no-install-recommends tzdata && \
    rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Bangkok

# create virtual environment
WORKDIR /app
#RUN python3 -m venv /venv
#ENV PATH="/venv/bin:$PATH"

# install model requirements
COPY requirements.txt .
RUN --mount=type=cache,target=${PIP_CACHE_DIR},sharing=locked \
    pip3 install -r requirements.txt

WORKDIR /app

COPY . ./


ENV PYTHONPATH=/app

ENV NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility,video \
    CUDA_VISIBLE_DEVICES=all

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD nvidia-smi || exit 1
#
#RUN if command -v nvidia-smi > /dev/null; then \
#        echo "✅ GPU detected: Using CUDA"; \
#        echo "ENV CUDA_VISIBLE_DEVICES=all" >> /etc/environment; \
#        echo "ENV NVIDIA_VISIBLE_DEVICES=all" >> /etc/environment; \
#    else \
#        echo "⚠️ No GPU found: Running on CPU"; \
#        echo "ENV CUDA_VISIBLE_DEVICES=" >> /etc/environment; \
#        echo "ENV NVIDIA_VISIBLE_DEVICES=" >> /etc/environment; \
#    fi
#
## Use a conditional healthcheck that supports both CPU & GPU
#HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#    CMD sh -c "if command -v nvidia-smi > /dev/null; then nvidia-smi; else echo 'No GPU found, running on CPU'; fi"
#
#
# Change permissions for start.sh
RUN chmod +x /app/start.sh

EXPOSE 10011

CMD ["/app/start.sh"]