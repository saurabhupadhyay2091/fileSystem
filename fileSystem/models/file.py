from app import db


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    path = db.Column(db.String(200))
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))

    def as_dict(self):
        return {'id': self.id, 'filename': self.filename, 'path': self.path}
