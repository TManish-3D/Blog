from new_projects import db,login_manager,app
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    # Only allow active users to be loaded
    if user and user.is_active:
        return user
    return None


class User(db.Model,UserMixin):
   __tablename__ = "users"
   id=db.Column(db.Integer,primary_key=True )
   username=db.Column(db.String(20),nullable=True )
   email=db.Column(db.String(50),unique=True,nullable=True )
   password=db.Column(db.String(255),nullable=True )
   image_file=db.Column(db.String(20),nullable=True ,default='default.jpg')
   created_at = db.Column(db.DateTime, default=datetime.utcnow)
   is_active=db.Column(db.Boolean, default=True, nullable=False, server_default='1')

   role=db.Column(db.String(20),default='user')
   posts=db.relationship('Post',backref='author',lazy=True)

   def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
   
   @staticmethod
   def verify_reset_token(token, expires_sec=1800):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=expires_sec)
        user_id = data['user_id']
    except Exception:
        return None
    return User.query.get(user_id)

   
   def is_admin(self):
      return self.role == "admin"
   
   def __repr__(self):
      return f"User('{self.username}','{self.email}','{self.image_file} {self.role}')"
   
class Post(db.Model):
   __tablename__ = "posts"
   id=db.Column(db.Integer,primary_key=True )
   title=db.Column(db.String(20),nullable=False )
   date=db.Column(db.DateTime,nullable=True,default=datetime.utcnow )
   content=db.Column(db.Text,nullable=False )
   image_file=db.Column(db.String(20),nullable=True ,default='default.jpg')
   user_id=db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)

   def __repr__(self):
      return f"Post('{self.title})','{self.date}"