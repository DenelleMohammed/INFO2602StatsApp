from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from sqlalchemy.sql import func
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(50)) 

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'user_type': self.user_type
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def __repr__(self):
        return f'<User {self.id} - {self.username}>'
    

class Admin(User):
    __tablename__ = 'admin'
    staff_id = db.Column(db.String(120), unique=True)

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    datafiles = db.relationship('DataFile', backref='admin', lazy=True)
    reports = db.relationship('Report', backref='admin', lazy=True)

    def upload_datafile(self, filename):
        new_file = DataFile(filename=filename, admin_id=self.id)
        db.session.add(new_file)
        db.session.commit()
        return new_file

    def create_report(self, title, datafile_id, description=""):
        new_report = Report(
            title=title,
            description=description,
            admin_id=self.id,
            datafile_id=datafile_id
        )
        db.session.add(new_report)
        db.session.commit()
        return new_report

    def __init__(self, staff_id, username, email, password):
        super().__init__(username, email, password)
        self.staff_id = staff_id

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "staff_id": self.staff_id,
            "user_type": self.user_type
        }

    def __repr__(self):
        return f'<Admin {self.id} - {self.username}>'

