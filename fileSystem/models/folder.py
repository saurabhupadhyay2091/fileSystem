from app import db


class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    files = db.relationship('File', backref='folder', lazy=True)
    subfolders = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def as_dict(self):
        return {'id': self.id, 'name': self.name, 'parent_id': self.parent_id}
