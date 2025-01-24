# app/routes/predict.py
import io
from http import HTTPStatus
from flask import Blueprint, request, jsonify, current_app
from app.services.PredictService import PredictService
from PIL import Image

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/', methods=['POST'])
def predict():
    """
    Predict the class of the image
    """
    try:
        _id = request.form.get('id')
        image_file = request.files.get('file')

        if not image_file:
            return jsonify({
                'status': 'error',
                'message': 'No image provided'
            }), HTTPStatus.BAD_REQUEST

        if image_file.filename == '' or not PredictService.allowed_file(image_file.filename):
            return jsonify({
                'status': 'error',
                'message': 'No selected file or invalid file type'
            }), HTTPStatus.BAD_REQUEST

        image = Image.open(io.BytesIO(image_file.read()))

        result, status_code = PredictService.predict(_id, image)

        return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"Error in predict: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
