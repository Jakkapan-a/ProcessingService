from http import HTTPStatus

from flask import Blueprint, jsonify,request

from app.services.filemanager import get_file_list

filemanager_bp = Blueprint('filemanager', __name__, url_prefix='/filemanager')
from app.models.filemanager import FileManager
from app import db

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

        # Validate pagination parameters
        if page < 1:
            return jsonify({'error': 'Page number must be greater than 0'}), HTTPStatus.BAD_REQUEST
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'Per page must be between 1 and 100'}), HTTPStatus.BAD_REQUEST

        # Get file list from service
        result = get_file_list(search=search, page=page, per_page=per_page)

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
        name = request.json['name']
        is_valid = validate_name(name)
        if is_valid:
            return jsonify({'status': 'success', 'message': 'Name is valid'}), HTTPStatus.OK
        else:
            return jsonify({'status': 'error', 'message': 'Name is invalid'}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


