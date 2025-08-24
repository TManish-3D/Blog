from new_projects import db,login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))
class User(db.Model,UserMixin):
   id=db.Column(db.Integer,primary_key=True )
   username=db.Column(db.String(20),nullable=True )
   email=db.Column(db.String(50),unique=True,nullable=True )
   password=db.Column(db.String(24),nullable=True )
   image_file=db.Column(db.String(20),nullable=True ,default='default.jpg')
   posts=db.relationship('Post',backref='author',lazy=True)
   def __repr__(self):
      return f"User('{self.username}','{self.email}','{self.image_file}')"
class Post(db.Model):
   id=db.Column(db.Integer,primary_key=True )
   title=db.Column(db.String(20),nullable=False )
   date=db.Column(db.DateTime,nullable=True,default=datetime.utcnow )
   content=db.Column(db.Text,nullable=False )
   user_id=db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)

   def __repr__(self):
      return f"Post('{self.title})','{self.date}"