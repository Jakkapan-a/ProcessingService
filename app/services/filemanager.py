# services/filemanager.py
import os
import uuid
from http import HTTPStatus

from flask import current_app
from sqlalchemy import or_
from app import db
from app.models.filemanager import FileManager
from werkzeug.utils import secure_filename

from app.services.model_loader import clean_model_cache


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
    def get_file_by_id(_id):
        """
        Get file by id
        :param _id:
        :return:
        """
        result = FileManager.query.get(_id)
        if not result:
            return {
                'status': 'error',
                'message': 'File not found'
            }, HTTPStatus.NOT_FOUND

        return {
            'status': 'success',
            'data': result.to_dict(),
            'message': 'File retrieved successfully'
        }, HTTPStatus.OK

    @staticmethod
    def validate_name(_name, _id =0):
        """
        Validate file _name
        :param _name:
        :param _id: default 0
        :return:
        """
        if not _name or len(_name) > 255:
            return False

        if _id > 0:
            query = FileManager.query.filter(FileManager.name == _name, FileManager.id != _id)
        else:
            query = FileManager.query.filter(FileManager.name == _name)

        existing = query.first()
        # return True if name is valid (not exists)
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
        :param file: อัพโหลดไฟล์
        :param data: ข้อมูลที่เกี่ยวข้อง
        :param extension: นามสกุลไฟล์
        :return: tuple ของ response data และ status code
        """
        try:
            path_models = os.path.join('models', data['file_type'])
            new_filename = FileManagerService._merge_chunks(
                data['filename'],
                data['total_chunks'],
                data['file_type'],
                extension
            )

            # save image file
            image = data.get('image')
            image_filename = FileManagerService._save_image(image) if image else ""

            # if data['id'] is provided, update existing record
            if data.get('id'):
                file_manager = FileManager.query.get(data['id'])
                if not file_manager:
                    raise Exception("Data not found for update")

                # update existing record
                file_manager.name = data['name']
                file_manager.description = data['description']
                file_manager.filename = new_filename
                file_manager.image_name = image_filename
                file_manager.file_type = data['file_type']
                file_manager.updated_at = db.func.now()

                db.session.commit()

                return {
                    "message": "File updated successfully",
                    "filename": file_manager.to_dict(),
                    "type": "model",
                    "image_url": f"/images/{image_filename}" if image_filename else None
                }, 200
            else:
                # Add new record
                file_manager = FileManager(
                    name=data['name'],
                    description=data['description'],
                    filename=new_filename,
                    image_name=image_filename,
                    file_type=data['file_type']
                )

                db.session.add(file_manager)
                db.session.commit()

                return {
                    "message": "File uploaded successfully",
                    "filename": file_manager.to_dict(),
                    "type": "model",
                    "image_url": f"/images/{image_filename}" if image_filename else None
                }, 201

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing final chunk: {str(e)}")
            raise

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

    @staticmethod
    def update_info(data):
        """
        Update file information

        Args:
            data (dict): data for update

        Returns:
            dict: updated file information

        Raises:
            ValueError: if name is not provided
        """
        try:
            # Validate input
            if not data.get('name'):
                raise ValueError("Name is required")

            _id = int(data.get('id', 0))
            if _id <= 0:
                raise ValueError("Invalid ID")

            # Get file manager
            file_manager = FileManager.query.get(_id)
            if not file_manager:
                raise ValueError("File not found")

            print(data)
            # Update fields
            file_manager.name = data.get('name')
            file_manager.description = data.get('description', '')

            # Save changes
            db.session.commit()

            return {
                'status': 'success',
                'message': 'File information updated successfully',
                'data': file_manager.to_dict()
            }

        except ValueError as e:
            raise e
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in update_info: {str(e)}")
            raise Exception(f"Failed to update file information: {str(e)}")

    @staticmethod
    def delete_file(data):
        """
        Delete file manager entry
        :param data:
        :return: dict
        """
        try:
            _id = int(data.get('id', 0))
            if _id <= 0:
                raise ValueError("Invalid ID")

            file_manager = FileManager.query.get(_id)
            if not file_manager:
                raise ValueError("File not found")
            # Delete files
            FileManagerService.delete_image(file_manager.image_name)

            file_type = file_manager.file_type if file_manager.file_type else 'cls'
            path_models = os.path.join('models', file_type)

            path = os.path.join(path_models, file_manager.filename)
            if os.path.exists(path):
                os.remove(path)
                current_app.logger.info(f"Removed model file: { file_manager.filename }")

            db.session.delete(file_manager)
            db.session.commit()

            return {
                'status': 'success',
                'message': 'File deleted successfully'
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in delete: {str(e)}")
            raise Exception(f"Failed to delete file: {str(e)}")

    @staticmethod
    def clear_file():
        """
        Clear all files in models/cls and models/detect that are not in the database.
        :return: Response dictionary and HTTP status code
        """
        def clear_directory(directory):
            """
            Helper function to clear files in a directory that are not in the database.
            :param directory: Path to the directory
            """
            if not os.path.exists(directory):
                current_app.logger.warning(f"Directory {directory} does not exist.")
                return

            files = os.listdir(directory)
            for filename in files:
                file_path = os.path.join(directory, filename)
                exit_file = FileManager.query.filter_by(filename=filename).first()
                if not exit_file:
                    try:
                        os.remove(file_path)
                        current_app.logger.info(f"Removed: {filename}")
                    except Exception as e:
                        current_app.logger.error(f"Error deleting {filename}: {str(e)}")
                else:
                    current_app.logger.info(f"Keep: {filename}")

        # Clear files in models/cls
        cls_directory = os.path.join("models", "cls")
        current_app.logger.info("Clearing files in models/cls")
        clear_directory(cls_directory)

        # Clear files in models/detect
        detect_directory = os.path.join("models", "detect")
        current_app.logger.info("Clearing files in models/detect")
        clear_directory(detect_directory)
        clean_model_cache(max_age_minutes=45)
        return {
            'status': 'success',
            'message': 'All files deleted successfully'
        }, HTTPStatus.OK