# services/filemanager.py
import os
import uuid
from flask import current_app
from sqlalchemy import or_
from app import db
from app.models.filemanager import FileManager
from werkzeug.utils import secure_filename

class FileManagerService:
    IMAGE_DIR = "public/images/"
    SIZE_MAP = {
        'thumbnail': (150, 100),
        'small': (300, 200),
        'large': (600, 400),
    }

    @staticmethod
    def get_file_list(search=None, page=1, per_page=10):
        """
        Query file list with pagination
        :param search:
        :param page:
        :param per_page:
        :return:
        """
        query = FileManager.query

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    FileManager.name.ilike(search_term),
                    FileManager.file_type.ilike(search_term),
                    FileManager.description.ilike(search_term)
                )
            )

        total_items = query.count()
        total_pages = (total_items + per_page - 1) // per_page
        page = min(max(page, 1), total_pages) if total_pages > 0 else 1

        items = query.order_by(FileManager.created_at.desc()) \
            .offset((page - 1) * per_page) \
            .limit(per_page) \
            .all()

        return {
            'items': [item.to_dict() for item in items],
            'pagination': {
                'total_items': total_items,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }

    @staticmethod
    def validate_name(name):
        """
        Validate file name
        :param name:
        :return:
        """
        if not name or len(name) > 255:
            return False

        existing = FileManager.query.filter(FileManager.name == name).first()
        return existing is None

    @staticmethod
    def handle_chunk_upload(file, data):
        """
        Handle chunk upload
        :param file:
        :param data:
        :return:
        """
        try:
            path_temp = os.path.join('public', 'temp', data['file_type'])
            os.makedirs(path_temp, exist_ok=True)

            filename = data['filename'].split('.')[0]
            extension = os.path.splitext(file.filename)[1]
            temp_filename = f"{filename}_{data['chunk_number']}{extension}"

            file.save(os.path.join(path_temp, temp_filename))

            # if this is the last chunk, merge all chunks
            if data['chunk_number'] == data['total_chunks'] - 1:
                return FileManagerService._process_final_chunk(file, data, extension)

            return {
                "message": "Chunk uploaded successfully",
                "filename": temp_filename,
                "type": "chunk"
            }, 201


        except Exception as e:
            current_app.logger.error(f"Error in chunk upload: {str(e)}")
            raise

    @staticmethod
    def _process_final_chunk(file, data, extension):
        """
        Process final chunk
        :param file:
        :param data:
        :param extension:
        :return:
        """
        path_models = os.path.join('models', data['file_type'])
        new_filename = FileManagerService._merge_chunks(
            data['filename'],
            data['total_chunks'],
            data['file_type'],
            extension
        )

        #
        image = data.get('image')
        image_filename = FileManagerService._save_image(image) if image else ""

        # save file record
        if data.get('id'):
            file_manager = FileManager.query.get(data['id'])
            if not file_manager:
                raise Exception("Data not found for update")

            file_manager.name = data['name']
            file_manager.description = data['description']
            file_manager.filename = new_filename
            file_manager.image_name = image_filename

            file_manager.updated_at = db.func.now()
            file_manager.save()
        else:

            file_manager = FileManager(
                name=data['name'],
                description=data['description'],
                filename=new_filename,
                image_name=image_filename
            )
            file_manager.save()

    @staticmethod
    def _merge_chunks(filename, total_chunks, file_type, extension):
        """
        Merge chunks into a single file
        :param filename:
        :param total_chunks:
        :param file_type:
        :param extension:
        :return:
        """
        path_temp = os.path.join('public', 'temp', file_type)
        path_models = os.path.join('models', file_type)
        os.makedirs(path_models, exist_ok=True)

        new_filename = f"{filename}_{uuid.uuid4()}{extension}"
        new_filename = secure_filename(new_filename)

        with open(os.path.join(path_models, new_filename), 'wb') as final_file:
            for i in range(total_chunks):
                chunk_path = os.path.join(path_temp, f"{filename}_{i}{extension}")
                with open(chunk_path, 'rb') as chunk_file:
                    final_file.write(chunk_file.read())
                os.remove(chunk_path)

        return new_filename

    @staticmethod
    def _save_image(image):
        """
        Save image file
        :param image:
        :return:
        """
        if not image:
            return ""

        extension = os.path.splitext(image.filename)[1]
        filename = secure_filename(image.filename.split('.')[0])
        new_filename = f"{filename}_{uuid.uuid4()}{extension}"

        os.makedirs(os.path.join('public', 'images'), exist_ok=True)
        image.save(os.path.join('public', 'images', new_filename))

        return new_filename

    @staticmethod
    def delete_image(image_name):
        """
         Delete image files
        :param image_name:
        :return:
        """
        try:
            for size in FileManagerService.SIZE_MAP:
                path = os.path.join('public', 'images', size, image_name)
                if os.path.exists(path):
                    os.remove(path)
                    current_app.logger.info(f"Removed {size} file: {image_name}")

            original_path = os.path.join('public', 'images', image_name)
            if os.path.exists(original_path):
                os.remove(original_path)
                current_app.logger.info(f"Removed original file: {image_name}")

        except Exception as e:
            current_app.logger.error(f"Error deleting image: {str(e)}")
            raise