#!/bin/bash
echo "Starting server..."
pwd
ls -la
# shellcheck disable=SC2093

python3 -c "
import torch
print('CUDA available:', torch.cuda.is_available())
print('Device count:', torch.cuda.device_count())
if torch.cuda.is_available():
    print('Device name:', torch.cuda.get_device_name(0))
"

exec gunicorn --bind :${PORT:-10011} --workers ${WORKERS:-1} --threads ${THREADS:-4} --timeout 0 --worker-class gthread _server:app
#exec gunicorn --bind :${PORT:-10011} \
#    --workers ${WORKERS:-1} \
#    --threads ${THREADS:-4} \
#    --timeout 0 \
#    --worker-class gthread \
#    _server:app