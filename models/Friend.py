from app import db

class Friend(db.Model):
    __tablename__ = 'friends'
    friendship_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    