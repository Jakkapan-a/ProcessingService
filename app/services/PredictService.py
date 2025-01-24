# app/services/PredictService.py
from http import HTTPStatus
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

        model = get_model(file_manager.filename, path_model, file_manager.id)

        if not model:
            return {
                'status': 'error',
                'message': 'Model not found'
            }, HTTPStatus.NOT_FOUND

        result = model.predict(image)

        processed_result = (PredictService.process_cls_result(result)
                            if file_manager.file_type == 'cls'
                            else PredictService.process_cls_result(result))
        clean_model_cache(max_age_hours=1)

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
        names = result[0].names  # Get class name mapping

        # Convert class indices to names
        class_names = [names[int(c)] for c in boxes.cls.tolist()]

        return {
            'boxes': boxes.xyxy.tolist(),
            'labels': boxes.get_field('labels').tolist(),
            'conf': boxes.conf.tolist(),
            'cls': boxes.cls.tolist()
        }

    @staticmethod
    def process_cls_result(result):
        return {
            'class': int(result[0].probs.top1),
            'confidence': float(result[0].probs.top1conf)
        }