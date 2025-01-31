import torch
from flask import current_app


def check_gpu():
    current_app.logger.info("Checking GPU")
    print("PyTorch version:", torch.__version__)
    print("CUDA built:", torch.backends.cuda.is_built())
    print("CUDA available:", torch.cuda.is_available())
    current_app.logger.info(f"PyTorch version: {torch.__version__}")
    current_app.logger.info(f"CUDA built: {torch.backends.cuda.is_built()}")
    current_app.logger.info(f"CUDA available: {torch.cuda.is_available()}")
    cuda_available = torch.cuda.is_available()

    if cuda_available:
        # Force CUDA initialization
        torch.cuda.init()
        gpu_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        return {
            "cuda_available": True,
            "gpu_count": gpu_count,
            "gpu_name": gpu_name,
            "cuda_version": torch.version.cuda
        }
    return {
        "cuda_available": False,
        "error": "CUDA not available",
        "cuda_built": torch.backends.cuda.is_built()
    }