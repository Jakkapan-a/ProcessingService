# routes/filemanager.py
from flask import Blueprint, request, jsonify, current_app
from http import HTTPStatus

from app.services.filemanager import FileManagerService
filemanager_bp = Blueprint('filemanager', __name__)

"""
File manager routes
"""
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
        # raise TypeError("This is a test error")

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

@filemanager_bp.route('/<int:_id>/info', methods=['GET'])
def get_file_info(_id):
    """
    Get file manager entry by id
    ---
    parameters:
      - name: _id
        in: path
        type: integer
        required: true
        description: File manager entry id
    responses:
        200:
            description: File manager entry info
        400:
            description: Invalid parameters
    """
    try:
        # Get file info from service
        result, status_code = FileManagerService.get_file_by_id(_id)

        # Return response
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


"""
Create file manager entry
"""
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
        name = request.form.get('name') if request.form else request.json.get('name')
        _id = request.form.get('id') if request.form else request.json.get('id', 0)
        if not name:
            return jsonify({'status': 'error', 'message': 'Name is required','is_valid': False}), HTTPStatus.BAD_REQUEST

        try:
            _id = int(_id) if _id else 0
        except ValueError:
            _id = 0

        is_valid = FileManagerService.validate_name(name, _id)
        if is_valid:
            return jsonify({'status': 'success', 'message': 'Name is valid','is_valid': True}), HTTPStatus.OK

        return jsonify({'status': 'error', 'message': 'Name is invalid','is_valid': False}), HTTPStatus.OK
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

@filemanager_bp.route('/update-info', methods=['POST'])
def update_info():
    """
    Update file manager entry
    """
    try:
        #  JSON และ form-data
        data = request.form.to_dict() if request.form else request.json

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), HTTPStatus.BAD_REQUEST

        result = FileManagerService.update_info(data)
        return jsonify(result), HTTPStatus.OK

    except Exception as e:
        current_app.logger.error(f"Error in update_info: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@filemanager_bp.route('/delete', methods=['POST'])
def delete_file():
    """
    Delete file manager entry
    """
    try:
        data = request.form.to_dict() if request.form else request.json

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), HTTPStatus.BAD_REQUEST

        result = FileManagerService.delete_file(data)
        return jsonify(result), HTTPStatus.OK

    except Exception as e:
        current_app.logger.error(f"Error in delete_file: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@filemanager_bp.post('/clear-file')
def clear():
    """
    Clear file
    return:
    """
    try:
        result, status_code = FileManagerService.clear_file()
        if not result:
            return jsonify({'status': 'error', 'message': 'Error in clear'}), HTTPStatus.NOT_FOUND
        return jsonify({'status': 'success', 'message': 'Remove file success'}), HTTPStatus.OK
    except Exception as e:
        current_app.logger.error(f"Error in clear: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
