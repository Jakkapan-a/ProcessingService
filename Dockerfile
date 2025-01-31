FROM ultralytics/ultralytics:latest

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10011 \
    WORKERS=1 \
    THREADS=2 \
    DEBUG=false \
    TZ=Asia/Bangkok

# Install additional dependencies if needed
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# เปลี่ยนสิทธิ์ start.sh
RUN chmod +x /app/start.sh

# Health check with GPU
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python3 -c "import torch; assert torch.cuda.is_available()" || exit 1

EXPOSE 10011

CMD ["/app/start.sh"]