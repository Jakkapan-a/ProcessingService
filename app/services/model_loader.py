# app/services/model_loader.py

import os
from ultralytics import YOLO
from datetime import datetime, timedelta

model_cache = {}
model_access_time = {}

def clean_model_cache(max_age_hours=2):
    current_time = datetime.now()
    print(f"Running clean_model_cache at {current_time}")

    to_delete = []
    for model_name, access_time in model_access_time.items():
        if current_time - access_time > timedelta(hours=max_age_hours):
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

    model = YOLO(model_path)
    model_cache[model_id] = model # Store model in cache
    model_access_time[model_id] = datetime.now()  # Set access time
    return model

