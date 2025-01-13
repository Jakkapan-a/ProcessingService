# routes/filemanager.py
from flask import Blueprint, request, jsonify, current_app
from http import HTTPStatus

from numpy.f2py.auxfuncs import throw_error

from app.services.filemanager import FileManagerService

filemanager_bp = Blueprint('filemanager', __name__)

@filemanager_bp.route('/', methods=['GET'])
def get_filemanager():
    """
    Get file manager entries with pagination and search
    ---
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number
      - name: per_page
        in: query
        type: integer
        default: 10
        description: Items per page
      - name: search
        in: query
        type: string
        description: Search term for filtering files
    responses:
        200:
            description: List of files with pagination info
        400:
            description: Invalid parameters
    """

    try:
        # Get and validate query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', None, type=str)

        # test error handling
        raise TypeError("This is a test error")

        # Validate pagination parameters
        if page < 1:
            return jsonify({'error': 'Page number must be greater than 0'}), HTTPStatus.BAD_REQUEST
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'Per page must be between 1 and 100'}), HTTPStatus.BAD_REQUEST

        # Get file list from service
        result = FileManagerService.get_file_list(search=search, page=page, per_page=per_page)

        # Return response
        return jsonify({
            'status': 'success',
            'data': result,
            'message': 'Files retrieved successfully'
        }), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@filemanager_bp.route('/validate', methods=['POST'])
def validate_name():
    """
    Validate the name of file manager entry
    ---
    parameters:
      - name: name
    responses:
        200:
            description: Name is valid
        400:
            description: Name is invalid
    """
    try:
        name = request.json.get('name')
        if not name:
            return jsonify({'status': 'error', 'message': 'Name is required'}), HTTPStatus.BAD_REQUEST

        is_valid = FileManagerService.validate_name(name)
        if is_valid:
            return jsonify({'status': 'success', 'message': 'Name is valid'}), HTTPStatus.OK

        return jsonify({'status': 'error', 'message': 'Name is invalid'}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        current_app.logger.error(f"Error in validate_name: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


# Base image directory
IMAGE_DIR = "public/images/"
size_map = {
    'thumbnail': (150, 100),
    'small': (300, 200),
    'large': (600, 400),
}

@filemanager_bp.route('/upload-chunk-model', methods=['POST'])
def upload_chunk_model():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    try:
        file = request.files['file']
        data = {
            'name': request.form.get('name'),
            'chunk_number': int(request.form.get('chunk_number', 0)),
            'total_chunks': int(request.form.get('total_chunks', 1)),
            'description': request.form.get('description', ''),
            'filename': request.form.get('filename', 'uploaded_file'),
            'file_type': request.form.get('file_type', 'cls'),
            'id': request.form.get('id', 0),
            'image': request.files.get('image')
        }
        result, status_code = FileManagerService.handle_chunk_upload(file, data)
        return jsonify(result), status_code

    except Exception as e:
        current_app.logger.error(f"Error in upload_chunk_model: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
