from flask import Flask,redirect,request,render_template,url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from flask_script import Manager
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from PIL import Image
from forms import *
import smtplib
import os
import secrets

app= Flask(__name__)

app.config['SECRET_KEY'] =os.environ.get('KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('URI')
app.config['UPLOADED_IMAGES_DEST']= 'static/pictures'
mail= Mail(app)

# images=UploadSet('images', IMAGES)
# configure_uploads(app,images)
     
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
migrate= Migrate(app,db)
manager= Manager(app)
manager.add_command('db', MigrateCommand)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))

class User(db.Model, UserMixin):
   id=db.Column(db.Integer, primary_key= True)
   profile=db.relationship("Profile", backref="user", uselist=False)
   userfields=db.relationship("User_fields", backref="user")
   posts=db.relationship("Post", backref="user")
   postlikes=db.relationship("Like_post", backref="user", uselist=False)
   postcomments=db.relationship("Comment_post", backref="user")
   post_notification=db.relationship("Post_notification", backref="user")
   suggs=db.relationship("Sugg", backref="user")
   sugglikes=db.relationship("Like_sugg", backref="user", uselist=False)
   suggcomments=db.relationship("Comment_sugg", backref="user")
   sugg_notifications=db.relationship("Sugg_notification", backref="user")

   def get_reset_token(self,expires_sec=1800):
      s= Serializer(app.config['SECRET_KEY'], expires_sec)
      return s.dumps({'user_id': self.id}).decode('utf-8')

   @staticmethod
   def verify_reset_token(token):
      s= Serializer(app.config['SECRET_KEY'])
      try:
         user_id= s.loads(token)['user_id']
      except:
         return None
      return User.query.get(user_id)

class User_fields(db.Model):
   id=db.Column(db.Integer, primary_key= True)
   user_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)   
   field= db.Column(db.String(30), nullable=False)

class Profile(db.Model):
   id=db.Column(db.Integer, primary_key= True)   
   first_name=db.Column(db.String(30), unique=True, nullable=False)
   last_name=db.Column(db.String(30), unique=True, nullable=False)
   email=db.Column(db.String(30), unique=True, nullable=False)
   image_file=db.Column(db.String(20), default='default.jpg')
   number=db.Column(db.String(20), unique=True, nullable=False)
   state=db.Column(db.String(100), nullable=False)
   password=db.Column(db.String(60), nullable=False)   
   role=db.Column(db.String(20), nullable=False)
   date_created=db.Column(db.DateTime, default= datetime.utcnow)
   user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
class Post_notification(db.Model):
   id=db.Column(db.Integer, primary_key=True)
   triggered_by=db.Column(db.String(20), nullable=False)
   post_id=db.Column(db.Integer, db.ForeignKey('post.id'))
   user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
   read=db.Column(db.Boolean, default=True)
   date_created=db.Column(db.DateTime, default= datetime.utcnow)

class Post(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   image_file=db.Column(db.String(20), nullable=False)
   description=db.Column(db.String(120), nullable=False)
   price=db.Column(db.String(20), nullable=False)
   fields = db.relationship("Post_field", backref="post")
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   date_created=db.Column(db.DateTime, default= datetime.utcnow)
   likes=db.relationship("Like_post", backref="post")
   comments=db.relationship("Comment_post", backref="post")

class Post_field(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
   field= db.Column(db.String(30), nullable=False)

class Comment_post(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   post_id=db.Column(db.Integer, db.ForeignKey('post.id'))
   user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
   comment=db.Column(db.String(120), primary_key=True)
   date_created=db.Column(db.DateTime, default= datetime.utcnow)

class Like_post(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   post_id=db.Column(db.Integer, db.ForeignKey('post.id'))
   user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
   date_created=db.Column(db.DateTime, default= datetime.utcnow)

class Sugg_notification(db.Model):
   id=db.Column(db.Integer, primary_key=True)
   triggered_by=db.Column(db.String(20), nullable=False)
   post_id=db.Column(db.Integer, db.ForeignKey('sugg.id'))
   user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
   read=db.Column(db.Boolean, default=True)
   date_created=db.Column(db.DateTime, default= datetime.utcnow)

class Sugg(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   sugg=db.Column(db.String(120), nullable=False)
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   date_created=db.Column(db.DateTime, default= datetime.utcnow)
   likes=db.relationship("Like_sugg", backref="sugg")
   comments=db.relationship("Comment_sugg", backref="sugg")

class Comment_sugg(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   sugg_id=db.Column(db.Integer, db.ForeignKey('sugg.id'))
   user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
   comment=db.Column(db.String(120), primary_key=True)
   date_created=db.Column(db.DateTime, default= datetime.utcnow)

class Like_sugg(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   sugg_id=db.Column(db.Integer, db.ForeignKey('sugg.id'))
   user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
   date_created=db.Column(db.DateTime, default= datetime.utcnow)


@app.route('/')
@app.route('/home')
def home():
   return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
   form=RegistrationForm()
   
   if current_user.is_authenticated:
      return redirect(url_for('account'))
   # if request.method =='POST':
   #    #form.fields.data= request.form.get('fields')
   #    print(form.fields.data)
   #    print(form.role.data)      
   if form.validate_on_submit():
      # print(form.role.data)
      # print(form.fields.data)
      hashedPw=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
      user= User()
      profile=Profile(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,
                     number=form.number.data,state=form.state.data.lower(),password=hashedPw,role=form.role.data,user=user)
      user_details=[user,profile]
      for field in form.fields.data:
         i=User_fields(field=field,user=user)
         user_details.append(i)
      db.session.add_all(user_details)
      db.session.commit()
      flash(f'Account created successfully, You can now Login', 'success')
      return redirect(url_for('login'))
   
   return render_template('signup.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
   if current_user.is_authenticated:
      return redirect(url_for('account'))
   form= LoginForm()
   if form.validate_on_submit():
      profile=Profile.query.filter_by(email=form.email.data).first()
      if profile and bcrypt.check_password_hash(profile.password, form.password.data):
         login_user(profile.user, remember=form.remember.data)
         flash(f'You have been logged in!!', 'success')
         next_page=request.args.get('next')
         return redirect (next_page) if next_page else redirect(url_for('account'))
      else:
         flash(f'Login Unsuccessful. Please check your email and password', 'danger')
   return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('home'))


@app.route('/teachers')
def teachers():
   return render_template('teachers.html')

@app.route('/account')
@login_required
def account():
   posts=Post.query.all()
   image_file=url_for('static', filename='pictures/'+ current_user.profile.image_file)
   return render_template('account.html', image_file=image_file, posts=posts)

@app.route('/suggestions')
@login_required
def sugg():
   form=SuggForm()
   if form.validate_on_submit():
      sugg=Sugg(sugg=form.description.data, user=current_user)
      db.session.add(sugg)
      db.session.commit()
      flash('Your suggestions has been posted','success')
      return redirect(url_for('sugg'))      
   return render_template('sugg.html')

@app.route('/suggestions/<int:sugg_id>')
@login_required
def suggview(sugg_id):
   sugg= Sugg.query.get(int(sugg.id))
   form=SuggCommentForm()
   if form.validate_on_submit():
      comment=Comment_sugg(comments=form.description.data, user=current_user, sugg=sugg)
      db.session.add(comment)
      db.session.commit()
   return render_template('suggview.html')

@app.route('/suggestions/<int:sugg_id>/delete', methods=['POST'])
@login_required
def delete_sugg(sugg_id):
   sugg=Sugg.query.get_or_404(post_id)
   if current_user!=post.user:
      abort(403)
   else:
      db.session.delete(sugg)
      db.session.commit()
      flash(f'Your Suggestion has been deleted', 'success')
      return redirect(url_for('sugg'))
   return render_template('suggview.html', post=post)

def save_picture(form_picture):
   random_hex= secrets.token_hex(8)
   _, f_ext= os.path.splitext(form_picture.filename)
   picture_fn=random_hex+f_ext
   picPath= os.path.join(app.root_path,'static/pictures', picture_fn)
   output_size =(200,200)
   i= Image.open(form_picture)
   i.thumbnail(output_size)
   i.save(picPath)
   return picture_fn

def save_post_picture(form_picture):
   random_hex= secrets.token_hex(8)
   _, f_ext= os.path.splitext(form_picture.filename)
   picture_fn=random_hex+f_ext
   picPath= os.path.join(app.root_path,'static/post_pictures', picture_fn)
   output_size =(200,200)
   i= Image.open(form_picture)
   i.thumbnail(output_size)
   i.save(picPath)
   return picture_fn


@app.route('/account/update_profile', methods=['GET','POST'])
def update_profile():
   form=UpdateForm()
   if form.validate_on_submit():
      print(form.picture.data)
      if form.picture.data:
         picture_file=save_picture(form.picture.data)
         #picture_file= save_picture(form.picture.data)
         current_user.profile.image_file= picture_file      
      current_user.profile.first_name= form.first_name.data
      current_user.profile.last_name= form.last_name.data
      current_user.profile.email = form.email.data
      current_user.profile.number=form.number.data
      current_user.profile.state=form.state.data
      db.session.commit()
      flash(f'Your account has been updated', 'success')
      return redirect(url_for('account'))
   elif request.method =='GET':
      form.first_name.data=current_user.profile.first_name
      form.last_name.data=current_user.profile.last_name
      form.email.data=current_user.profile.email
      form.number.data=current_user.profile.number
      form.state.data=current_user.profile.state
   return render_template('update_profile.html', form=form)

@app.route('/create_post', methods=['GET','POST'])
@login_required
def create_post():
   form=CreatePostForm()
   if form.validate_on_submit():
      picture_fn=save_post_picture(form.picture.data)
      post= Post(image_file=picture_fn, description=form.description.data, price=form.price.data, user=current_user)   
      post_details=[post]
      for field in form.fields.data:
         i=Post_field(field=field,post=post)
         post_details.append(i)
      db.session.add_all(post_details)
      db.session.commit()
      flash(f'Your Ad has been posted successfully', 'success')
      return redirect(url_for('account'))
   return render_template('create_post.html', form=form)

@app.route('/post/<int:post_id>',methods=['GET','POST'])
@login_required
def view_product(post_id):
   post=Post.query.get_or_404(post_id)
   post_fields=[field.field for field in post.fields]
   user_fields=[field.field for field in post.user.userfields]
   return render_template('view_product.html', post=post, post_fields=post_fields, user_fields=user_fields, user_fieldsToStr=' '.join(map(str,user_fields)), post_fieldsToStr=' '.join(map(str,post_fields)))

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_product(post_id):
   post=Post.query.get_or_404(post_id)
   if current_user!=post.user:
      abort(403)
   else:
      db.session.delete(post)
      db.session.commit()
      flash(f'Your Ad has been deleted', 'success')
      return redirect(url_for('account'))
   return render_template('view_product.html', post=post)

@app.route('/userprofile')
@login_required
def userprofile():
   return render_template('userprofile.html')

@app.route('/user/notifications')
def notifications():
   return render_template('notification.html')

@app.route('/popular')
def popular():
   return render_template('popular.html')

@app.route('/recent')
def recent():
   return render_template('recent.html')

@app.route('/recom')
def recom():
   return render_template('recom.html')

def send_reset_email(user):
   token= user.get_reset_token()
   msg = Message('Password Reset Request', sender = os.environ.get('EMAIL_USER'), recipients = [user.profile.email])
   msg.body = f'''To reset your password, visit the following link: 
             {url_for('reset_token', token=token, _external=True)}
            
             '''
   mail.send(msg)
   #token= user.get_reset_token()
   # msg=Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.profile.email])
   # msg.body=f'''To reset your password, visit the following link: 
   #          {url_for('reset_token', token=token, _external=True)}
            
   #          '''
   # mail.send(msg)
   # message="To reset your password, visit the following link: "
   # server= smtplib.SMTP("smtp.gmail.com", 587)
   # server.starttls()
   # server.login('victorgbonna@gmail.com',os.environ.get('EMAIL_PASS'))
   # sever.sendmail('victorgbonna@gmail.com', user.profile.email, message)
   
@app.route('/reset_password',methods=['GET','POST'])
def reset_password():
   if current_user.is_authenticated:
      return redirect(url_for('account'))
   form=ResetRequestForm()
   if form.validate_on_submit():
      profile=Profile.query.filter_by(email=form.email.data).first()
      send_reset_email(profile.user) 
      flash('An email has been sent to you on how to reset your password.', 'info')
      return redirect(url_for('login'))
   return render_template('reset_request.html', form=form)

@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
   if current_user.is_authenticated:
      return redirect(url_for('account'))
   user= User.verify_reset_token(token)
   if not user:
      flash('That is an invalid or expired token', 'warning')
      return redirect(url_for('reset_password'))   
   form=ResetPasswordForm()
   if form.validate_on_submit():
      hashedPw=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
      user.profile.password= hashedPw
      db.session.commit()
      flash(f'You password has been updated! You can now log in', 'success')
      return redirect(url_for('login'))
   return render_template('reset_token.html', form=form)
   
if __name__== '__main__':
   app.run(debug=True)