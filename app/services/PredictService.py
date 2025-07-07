# app/services/PredictService.py
from http import HTTPStatus

import torch

from app.services.model_loader import get_model, clean_model_cache

ALLOWED_EXTENSIONS = { 'jpg', 'png', 'pt'} # set of allowed file extensions

class PredictService:
    """
    Check if the file extension is allowed
    @param filename: The name of the file
    """
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    """
    Service class for the prediction
    """
    @staticmethod
    def predict(_id, image):
        """
        Predict the class of the image
        """
        # Load the image
        from app.models.filemanager import FileManager
        file_manager = FileManager.query.filter_by(id=_id).first()

        if not file_manager:
            return {
                'status': 'error',
                'message': 'File not found'
            }, HTTPStatus.NOT_FOUND

        # Load the model
        path_model = "models"
        if file_manager.file_type == 'cls':
            path_model = "models/cls"
        elif file_manager.file_type == 'detect':
            path_model = "models/detect"
        print("path_model", path_model)
        print("file_manager.filename", file_manager.filename)

        model = get_model(file_manager.filename, path_model, file_manager.id)

        if not model:
            return {
                'status': 'error',
                'message': 'Model not found'
            }, HTTPStatus.NOT_FOUND

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model.info()

        print("Model loaded successfully on device:", device)

        
        # Predict the
        with torch.no_grad():
            result = model.predict(image)

        # Clean the model cache
        if device.type == 'cuda':
            torch.cuda.empty_cache()

        processed_result = (PredictService.process_cls_result(result)
                            if file_manager.file_type == 'cls'
                            else PredictService.process_detect_result(result))

        clean_model_cache(max_age_minutes=45)

        # Return the result
        print("======= End of Prediction Result =======")
        return {
            'status': 'success',
            'type': file_manager.file_type,
            'result': processed_result
        }, HTTPStatus.OK

    @staticmethod
    def process_detect_result(result):
        """
        Process the detection result
        """
        boxes = result[0].boxes
        names = result[0].names

        detections = []
        for i in range(len(boxes.xyxy)):
            detections.append({
                'box': boxes.xyxy[i].tolist(),
                'confidence': float(boxes.conf[i]),
                'class': int(boxes.cls[i]),
                'name': names[int(boxes.cls[i])]
            })

        return detections

    @staticmethod
    def process_cls_result(result):
        try:
            probs = result[0].probs
            return {
                'class': int(probs.data.argmax()),
                'confidence': float(probs.data.max()),
                'class_name': probs.names[int(probs.data.argmax())]
            }
        except AttributeError:
            return {
                'class': None,
                'confidence': None
            }