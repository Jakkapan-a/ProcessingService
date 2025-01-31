import torch

def check_gpu():
    cuda_available = torch.cuda.is_available()

    if cuda_available:
        gpu_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        return {
            "cuda_available": True,
            "gpu_count": gpu_count,
            "gpu_name": gpu_name
        }
    return {
        "cuda_available": False
    }
