#!/bin/bash
echo "Starting server..."
pwd
ls -la
#exec gunicorn --bind :${PORT:-10011} --workers ${WORKERS:-1} --threads ${THREADS:-4} --timeout 0 _server:app

python3 -c "
import torch
print('CUDA available:', torch.cuda.is_available())
print('Device count:', torch.cuda.device_count())
if torch.cuda.is_available():
    print('Device name:', torch.cuda.get_device_name(0))
"
# shellcheck disable=SC2093
exec gunicorn --bind :${PORT:-10011} \
    --workers ${WORKERS:-1} \
    --threads ${THREADS:-4} \
    --timeout 0 \
    --worker-class gthread \  # เพิ่ม worker class
    --preload \              # preload application
    _server:app