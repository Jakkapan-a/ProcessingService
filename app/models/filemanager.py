from app import db

class FileManager(db.Model):
    """
    File manager model class
    """

    __tablename__ = 'file_manager'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    image_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return f'<FileManager {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'filename': self.filename,
            'image_name': self.image_name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }