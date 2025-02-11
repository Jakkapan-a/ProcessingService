# app/services/model_loader.py

import os
import torch
from ultralytics import YOLO
from datetime import datetime, timedelta

model_cache = {}
model_access_time = {}

def check_gpu():
    """Check GPU availability and return device"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    if device == 'cuda':
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    return device


def clean_model_cache(max_age_minutes=45):
    current_time = datetime.now()
    print(f"Running clean_model_cache at {current_time}")

    to_delete = []
    for model_name, access_time in model_access_time.items():
        if current_time - access_time > timedelta(minutes=max_age_minutes):
            to_delete.append(model_name)

    for model_name in to_delete:
        del model_cache[model_name]
        del model_access_time[model_name]
        print(f"Removed model from cache: {model_name}")

    print(f"Cleaning up model cache: {len(to_delete)} models removed.")

# noinspection PyTypeChecker
def get_model(model_name, model_folder,model_id):
    # Check if model is in cache and update last accessed time
    if model_id in model_cache:
        model_access_time[model_id] = datetime.now()
        return model_cache[model_id]

    # Load the model and store it in the cache
    model_path = os.path.join(model_folder, model_name)
    if not os.path.exists(model_path):
        return None

    # Check GPU availability
    device = check_gpu()
    model = YOLO(model_path)

    if device == 'cuda':
        model.to('cuda')


    model_cache[model_id] = model # Store model in cache
    model_access_time[model_id] = datetime.now()  # Set access time
    return model

# def remove_model_not_db():
#     """
#     Remove model that not in cache and db
#     :return:
#     """
#     # Get all in folder
#     list_cls = os.listdir("models/cls")
#     list_detect = os.listdir("models/detect")
#
#     print('list_cls')
#     # endpoint = /api/v1/filemanager/:filename/validate
#     # url = 'http://localhost:'+port.__str__()+'/api/v1/filemanager'
#     for key in list_cls:
#         exit_file = 0
#         if not exit_file:
#             print('remove :',key)
#             os.remove(f"models/cls/{key}")
#             list_cls.remove(key)
#
#
#     print('list_detect')
#     for key in list_detect:
#         # exit_file = FileManager.query.filter_by(filename=key).first()
#         exit_file = 0 # FileManager.query.filter_by(filename=key).first()
#         if not exit_file:
#             print('remove :',key)
#             os.remove(f"models/detect/{key}")
#             list_detect.remove(key)

