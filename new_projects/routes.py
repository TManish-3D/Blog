
from flask import render_template,url_for,redirect,flash,request,abort
from new_projects import app,db, bcrypt,mail
import os
import secrets
from flask_mail import Message
from new_projects.forms import (RegistrationForm,LoginForm,PictureForm,PostForm,RequestResetForm,ResetPasswordForm)
from new_projects.models import User, Post
from flask_login import login_user,current_user,logout_user,login_required
from werkzeug.security import generate_password_hash,check_password_hash
from new_projects.decorators import admin_required

@app.route("/")
def home():
    posts=Post.query.order_by(Post.date.desc())
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
    
    image_file = url_for('static', filename='images/'+ (current_user.image_file if current_user.image_file else 'default.jpg'))
        # Optional: log or flash form errors
    if form.errors:
            print(form.errors)
    return render_template('account.html',title='Account',image_file=image_file,form=form)

@app.route("/user/<string:username>")
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).all()
    return render_template('user.html', user=user, posts=posts)


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
      if not user.is_active:
          flash('Your account has been deactivated', 'danger')
          return render_template('login.html', form=form)
      login_user(user)
      return redirect(url_for('home'))
     else:
        flash('Invalid credentials','danger')
   
   return render_template('login.html', form=form)

@app.route("/newpost",methods=['GET','POST'])
def newpost():
   form=PostForm()
   if form.validate_on_submit():
      
     image_file = None

     if form.picture.data:
            image_file = save_picture(form.picture.data)

     post=Post(title=form.title.data,content=form.content.data,image_file=image_file,author=current_user)
     db.session.add(post)
     db.session.commit()   
     flash('Your post has been published','success')
     return redirect(url_for('home'))
   return render_template('newpost.html',title='New Post',form=form)

@app.route("/newpost/<int:post_id>")
@login_required
def post(post_id):
   post=Post.query.get_or_404(post_id)
   return render_template('post.html',title=post.title,post=post)

@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # Forbidden if not the author
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated!", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    
    return render_template("newpost.html", title="Update Post", form=form, legend="Update Post")


# Delete Post
@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", "success")
    return redirect(url_for("home"))

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('If your email exists, a reset link has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title='Reset Password', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('reset_token', token=token, _external=True)
    msg = Message('Password Reset Request',
                   
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{reset_url}
If you did not make this request, simply ignore this email.
'''
    mail.send(msg)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form)

# Admin login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin = User.query.filter_by(username=username, role="admin").first()

        if admin and check_password_hash(admin.password,password):
            login_user(admin)
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials","danger")

    return render_template("admin/login.html")

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    user_count = User.query.count()
    post_count = Post.query.count()

    return render_template(
        "admin/dashboard.html",
        user_count=user_count,
        post_count=post_count
    )

#admin users
@app.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all() 
    return render_template("admin/users.html", users=users)

# DELETE USER
@app.route("/admin/users/delete/<int:id>")
@admin_required
def admin_delete_user(id):
    user = User.query.get_or_404(id)

    if user.role == "admin":
        flash("Cannot delete admin user", "danger")
        return redirect(url_for("admin_users"))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted", "success")
    return redirect(url_for("admin_users"))

@app.route("/admin/posts")
@admin_required
def admin_posts():
    posts = Post.query.all()
    return render_template("admin/posts.html", posts=posts)


@app.route("/admin/posts/delete/<int:id>")
@admin_required
def admin_delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("admin_posts"))


@app.route("/admin/logout")
@admin_required
def admin_logout():
    logout_user()
    return redirect(url_for("admin_login"))
