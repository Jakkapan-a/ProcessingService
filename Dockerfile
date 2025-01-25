FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime
ARG DEBIAN_FRONTEND=noninteractive
ARG TEST_ENV

WORKDIR /app

RUN conda update conda -y

RUN --mount=type=cache,target="/var/cache/apt",sharing=locked \
    --mount=type=cache,target="/var/lib/apt/lists",sharing=locked \
    apt-get -y update \
    && apt-get install -y git \
    && apt-get install -y wget \
    && apt-get install -y g++ freeglut3-dev build-essential libx11-dev \
    libxmu-dev libxi-dev libglu1-mesa libglu1-mesa-dev libfreeimage-dev \
    && apt-get -y install ffmpeg libsm6 libxext6 libffi-dev python3-dev python3-pip gcc

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_CACHE_DIR=/.cache \
    PORT=10010 \
    WORKERS=1 \
    THREADS=2 \
    CUDA_HOME=/usr/local/cuda \
    DEBUG=false

# Install Python, pip, and required build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv python3-distutils build-essential \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 && \
    rm -rf /var/lib/apt/lists/*


RUN conda install -c "nvidia/label/cuda-12.4" cuda -y
ENV CUDA_HOME=/opt/conda \
    TORCH_CUDA_ARCH_LIST="6.0;6.1;7.0;7.5;8.0;8.6+PTX;8.9;9.0"

# Install timezone data
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set the timezone to Thailand (Asia/Bangkok)
ENV TZ=Asia/Bangkok

# install model requirements
COPY requirements.txt .
RUN --mount=type=cache,target=${PIP_CACHE_DIR},sharing=locked \
    pip3 install -r requirements.txt

WORKDIR /app

COPY . ./


ENV PYTHONPATH=/app

# Change permissions for start.sh
RUN chmod +x /app/start.sh

EXPOSE 10011

CMD ["/app/start.sh"]