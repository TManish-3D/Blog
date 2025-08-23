
from flask import render_template,url_for,redirect,flash
from new_projects import app,db, bcrypt
import os
import secrets
from new_projects.forms import RegistrationForm,LoginForm,PictureForm,PostForm
from new_projects.models import User, Post
from flask_login import login_user,current_user,logout_user,login_required

@app.route("/")
def home():
    posts=Post.query.all()
    return render_template("base.html",posts=posts)

def save_picture(form_picture):
   random_hex=secrets.token_hex(8)
   _,f_ext=os.path.splitext(form_picture.filename)
   picture_fn=random_hex + f_ext
   picture_path=os.path.join(app.root_path, 'static/images',picture_fn)
   form_picture.save(picture_path)
   return picture_fn

@app.route("/account",methods=["GET","POST"])
@login_required
def account():
    form=PictureForm()
    if form.validate_on_submit():
     if form.picture.data:
        picture_file=save_picture(form.picture.data)
        current_user.image_file=picture_file
        db.session.commit()
    
     flash('Photo Uploaded!', 'success')
    
    image_file = url_for('static', filename='images/'+ current_user.image_file)
        # Optional: log or flash form errors
    if form.errors:
            print(form.errors)
    return render_template('account.html',title='Account',image_file=image_file,form=form)

@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
       return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))  # or redirect to login/home
    return render_template('register.html', form=form)
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
@app.route("/login",methods=['GET','POST'])
def login():
   if current_user.is_authenticated:
       return redirect(url_for('home'))
   form = LoginForm()
   if form.validate_on_submit():
     user=User.query.filter_by(email=form.email.data).first()
     if user and bcrypt.check_password_hash(user.password,form.password.data):
      login_user(user)
      return redirect(url_for('home'))  # or redirect to login/home
     else:
        flash('Invalid cerentials','danger')
        
    
   return render_template('login.html', form=form)

@app.route("/newpost",methods=['GET','POST'])
def newpost():
   form=PostForm()
   if form.validate_on_submit():
      post=Post(title=form.title.data,content=form.content.data,author=current_user)
      db.session.add(post)
      db.session.commit()
      flash('Your post has been published','success')
      return redirect(url_for('home'))
   return render_template('newpost.html',title='New Post',form=form)