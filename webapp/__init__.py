import os
from flask import Flask, render_template, request, redirect, url_for, flash, session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField
from wtforms import Form, StringField, TextAreaField, validators, BooleanField, PasswordField, ValidationError, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, InputRequired
from sqlalchemy.ext.horizontal_shard import ShardedSession
from flask_sqlalchemy.session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from sqlalchemy import desc
from flask_ckeditor import CKEditor, CKEditorField
#from flask_tinymce import TinyMCE

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whatsupbuddy.sqlite3'
app.config['SECRET_KEY'] = "jbcisbiuifvuuugiohouhhoisoishoviuhiu"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
mail = Mail(app)
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = "vudviiaohohoauhouh47859709309"
app.config['RECAPTCHA_PRIVATE_KEY'] = "hldcijidjij74989tii"
app.config['RECAPTCHA_PARAMETERS'] = {'hl': 'zh', 'render': 'explicit'}
app.config['RECAPTCHA_DATA_ATTRS'] = {'theme': 'white'}
app.config['BCRYPT_SECRET_KEY'] = 'hsdhuhouhofhoij76598380mlklfnghiuhiu'  # Replace with a secret key for production
#UPLOAD_FOLDER = '/path/to/the/uploads'
#ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif'}
bcrypt = Bcrypt(app)
ckeditor = CKEditor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'standard'
datetime=datetime

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


################## GUESTBOOK #############   

# Define guestbook model
class GuestBook(db.Model):
    __tablename__="guestbook"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    scrap = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(12), nullable=False)
    
    """ def __init__(self, name=None, scrap=None):
        self.name = name
        self.scrap = scrap """
        

 
# WTForms for guestbook      
class GuestBookForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=5, max=30)])
    scrap = CKEditorField('Scrap', validators=[DataRequired(), Length(min=5, max=300)])
    #recaptcha = RecaptchaField()
    
    submit = SubmitField('Post Scrap')
    

@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(GuestBook).order_by(desc(GuestBook.date)))
    form = GuestBookForm()
    if form.validate_on_submit():
        guestbook = GuestBook(name=form.name.data, scrap=form.scrap.data, date=datetime.now().strftime("%Y-%m-%d %H:%M"))
        db.session.add(guestbook)
        db.session.commit()
        flash('Your scrap has been posted!', 'success')
        
        return redirect(url_for('guestbook'))
    return render_template('guestbook.html', form=form, pagination=pagination)


#################################### CONTACT #####################

# Define contacts model
class Contact(db.Model):
    __tablename__="contact"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(12), nullable=False) 
    
""" def __init__(self, name=None, email=None, message=None):
        self.name = name
        self.email = email
        self.message = message
  """

# WTForms for contact
class ContactForm(FlaskForm):
    name = StringField('name', [validators.Length(min=3, max=25), DataRequired()])
    email = StringField('email', [validators.Length(min=6, max=100), DataRequired()])
    message = CKEditorField('message', [validators.Length(min=3, max=1000), DataRequired()])
    #recaptcha = RecaptchaField()
    submit = SubmitField('Submit')
    
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(name=form.name.data, email=form.email.data, message=form.message.data, date=datetime.now().strftime("%Y-%m-%d %H:%M"))
        db.session.add(contact)
        db.session.commit()
        flash('Your Message Has Been Sent!', 'success')
        return redirect(url_for('thank_you'))
    return render_template('contact.html', form=form)



# Thank you page route
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

################## USER REGISTRATION, LOGIN, PROFILE, LOGOUT, PASSWORD, RECOVERY #########################


# Define the User model
class User(UserMixin, db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    confirm_password = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(19), nullable=False) 
    posts = db.relationship('Post', backref='author', lazy=True)
    comment = db.relationship('Comments', backref='author', lazy=True)
    
    """ def __init__(self, username=None, email=None, password=None):
        self.username = username
        self.email = email
        self.password = password """
        
        
# WTForms for registration 
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=16)])
    email = StringField('Email', validators=[DataRequired(), Length(min=5, max=60)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    #date = StringField('Email', validators=[DataRequired(), Length(min=2, max=10)])
    #recaptcha = RecaptchaField()
    submit = SubmitField('Sign Up')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """ if current_user.is_authenticated:
        return redirect(url_for('profile'))
     """
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, confirm_password=hashed_password, date=datetime.now().strftime("%Y-%m-%d %H:%M"))
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# WTForms for login
class LoginForm(FlaskForm):
    #username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Length(min=5, max=60)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your Email and Password.', 'danger')
    return render_template('login.html', form=form)

  


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out Successfully!', 'success')
    return redirect(url_for('home'))


# WTForms for password recovery
class PwdRecover(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=5, max=60)])
    submit = SubmitField('Login')


@app.route('/pwdrecover', methods=['GET', 'POST'])
def pwdrecover():
    form = PwdRecover()
    if form.validate_on_submit():
        pwd = User.query.filter_by(email=form.email.data).first()
        
        if pwd:            
            flash('Recovery Of Password is successful!', 'success')
            return redirect(url_for('pwdsetnew'))
        else:
            flash('Recovery failed. Check your email.', 'danger')
    return render_template('pwdrecover.html', form=form)


# Define the Post model
class Profile(db.Model):
    __tablename__="profile"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)
    name = db.Column(db.String(30), nullable=True)
    age = db.Column(db.String(2), nullable=True)
    country = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(20), nullable=True)
    education = db.Column(db.String(120), nullable=True)
    hobbies = db.Column(db.String(120), nullable=True)
    fcolour = db.Column(db.String(20), nullable=True)
    skills = db.Column(db.String(120), nullable=True)
    personality = db.Column(db.String(120), nullable=True)
    about = db.Column(db.String(1000), nullable=True)
    profilepic = db.Column(db.String(), nullable=True)
    


# Define the ProfileForm using WTForms
class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[ Length(max=30)])
    age = StringField('Age', validators=[ Length(max=2)])
    country = StringField('Country', validators=[Length( max=20)])
    city = StringField('City', validators=[ Length( max=20)])
    education = StringField('Education', validators=[Length( max=120)])
    hobbies = StringField('Hobbies', validators=[Length(max=120)])
    fcolour = StringField('Favorite Colour', validators=[Length( max=20)])
    skills = StringField('Skills', validators=[Length( max=120)])
    personality = StringField('Personality', validators=[Length( max=120)])
    about = CKEditorField('More About You', validators=[ Length( max=1000)])
    profilepic = FileField('Profile Picture')
    submit = SubmitField('Update Profile')
    


@app.route('/myprofile', methods=['GET', 'POST'])
@login_required
def myprofile():
    profile = Profile.query.filter_by(username=current_user.username).first()
    return render_template('myprofile.html',profile=profile)


@app.route('/userprofile/<string:username>')
def userprofile(username):
    user = User.query.filter_by(username=username).first()
    post = Post.query.filter_by(writer=user.username).all()
    profile = Profile.query.filter_by(username=user.username).first()
    #friendname = db.select(Friends).query.filter_by(friendname=user).first()
    friends = Friends.query.filter_by(friendname=user.username).first()
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Post).order_by(desc(Post.date)))
    return render_template('userprofile.html',pagination=pagination, page=page, user=user, friends=friends, post=post, profile=profile)

@app.route('/profileupdate', methods=['GET', 'POST'])
@login_required
def profileupdate():
    
    form = ProfileForm()
    profile = db.one_or_404(db.select(Profile).filter_by(username=current_user.username))
    if form.validate_on_submit():
        profile.name=form.name.data
        profile.age=form.age.data
        profile.country=form.country.data
        profile.city=form.city.data
        profile.education=form.education.data
        profile.fcolour=form.fcolour.data
        profile.skills=form.skills.data
        profile.hobbies=form.hobbies.data
        profile.personality=form.personality.data
        profile.about=form.about.data
        profile.profilepic=form.profilepic.data
        
        db.session.add(profile)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('myprofile', profile=profile))
    
    form.name.data = profile.name
    form.age.data = profile.age
    form.country.data = profile.country
    form.city.data = profile.city
    form.education.data = profile.education
    form.fcolour.data = profile.fcolour
    form.skills.data = profile.skills
    form.hobbies.data = profile.hobbies
    form.personality.data = profile.personality
    form.about.data = profile.about
    
    return render_template('profileupdate.html', form=form, profile=profile)


######################## FRIEND #############################

# Define the Friends model
class Friends(db.Model):
    __tablename__="friends"
    id = db.Column(db.Integer, primary_key=True)
    friendname = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)
    myname = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    
@app.route('/addfriend/<string:friendname>', methods=['GET', 'POST'])
@login_required
def addfriend(friendname):
    user = User.query.filter_by(username=friendname).first()
    profile = Profile.query.filter_by(username=friendname).first()
    #friends = Friends.query.filter_by(friendname=friendname).all()
    #myname = Friends.query.filter_by(myname=current_user.username).all()
    friend = (Friends.query.filter_by(friendname=friendname).all()) and (Friends.query.filter_by(myname=current_user.username).all())
   
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Post).order_by(desc(Post.date)))
    if friend:
        flash('This Friend Is Already In your Friend List!', 'danger')
    
    else:
        friendadd = Friends(myname=current_user.username, friendname=friendname, date=datetime.now().strftime("%Y-%m-%d %H:%M"))
        db.session.add(friendadd)
        db.session.commit()
        flash('Friend added successfully!', 'success')
    return render_template('userprofile.html', user=user, profile=profile, pagination=pagination, page=page, friend=friend)


@app.route('/removefriend/<string:friendname>', methods=['GET', 'POST'])
@login_required
def removefriend(friendname):
    user = User.query.filter_by(username=friendname).first()
    profile = Profile.query.filter_by(username=friendname).first()
    friend = (Friends.query.filter_by(friendname=friendname).all()) and (Friends.query.filter_by(myname=current_user.username).all())
    
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Post).order_by(desc(Post.date)))
    
    if not friend:
        flash('This Friend Is Not In your Friend List!', 'danger')
    
    else:
        db.session.delete(friend)
        db.session.commit()
        flash('Friend Removed successfully!', 'success')
    return render_template('userprofile.html', user=user, profile=profile, pagination=pagination, page=page, friend=friend)



@app.route('/friends')
@login_required
def friends():
        #friends = Friends.query.filter_by(myname=current_user.username).all()
        page = request.args.get('page', 1, type=int)
        pagination = db.paginate(db.select(Friends).filter_by(myname=current_user.username).order_by(Friends.date))
        return render_template('friends.html',  page=page, pagination=pagination)
    
    
####################### POST ###############################

# Define the Post model
class Post(db.Model):
    __tablename__="post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(12), nullable=False)
    writer = db.Column(db.Integer, db.ForeignKey('user.username'), nullable=False)
    
# Define the comment model
class Comments(db.Model):
    __tablename__="comments"
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(12), nullable=False)
    username = db.Column(db.Integer, db.ForeignKey('user.username'), nullable=False)

# Define the PostForm using WTForms
class PostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min=4, max=100)])
    content = CKEditorField('Post', validators=[InputRequired(), Length(min=6, max=10000)])
    submit = SubmitField('Post Article')
    
# Define the CommentsForm using WTForms
class CommentsForm(FlaskForm):
    comment = CKEditorField('Comments', validators=[InputRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Post Comment')

@app.route('/postnew', methods=['GET', 'POST'])
def postnew():
    form = PostForm()
    if form.validate_on_submit():
        postnew = Post(title=form.title.data, content=form.content.data, writer=current_user.username, date=datetime.now().strftime("%Y-%m-%d %H:%M"))
        db.session.add(postnew)
        db.session.commit()
        flash('You Have Posted a New Article!', 'success')
        return redirect(url_for('myposts'))
    return render_template('postnew.html', form=form)
   



@app.route('/myposts')
@login_required
def myposts():
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Post).order_by(desc(Post.date)))
    return render_template('myposts.html',pagination=pagination, page=page)


@app.route('/blogs')
def blogs():
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Post).order_by(desc(Post.date)))
    return render_template('blogs.html', pagination=pagination, page=page)


@app.route('/postview/<int:id>')
def postview(id):
    form = CommentsForm()
    post = Post.query.filter_by(id=id).first()
    comments = Comments.query.filter_by(postid=post.id).all()
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Comments).filter_by(postid=post.id).order_by(Comments.date))
    return render_template("postview.html", post=post, comments=comments, form=form, page=page, pagination=pagination)



@app.route('/commentnew/<int:id>', methods=['GET', 'POST'])
@login_required
def commentnew(id):
    #post = Post.query.filter_by(id=id).first()
    post = Post.query.get_or_404(id)
    form = CommentsForm()
    if form.validate_on_submit():
        commentnew = Comments(postid=post.id, comment=form.comment.data, username=current_user.username, date=datetime.now().strftime("%Y-%m-%d %H:%M"))
        db.session.add(commentnew)
        db.session.commit()
        flash('You Comment Has Been Added To The Post!', 'success')
        return redirect(url_for('postview', form=form, post=post, id=id))
    return render_template('postview.html', form=form, post=post)

@app.route("/postdelete/<int:id>")
@login_required
def postdelete(id):
    post = Post.query.filter_by(id=id).first()
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Post).order_by(desc(Post.date)))
    if post:
        db.session.delete(post)
        db.session.commit()
        flash('Your Selected Post Has Been Deleted!', 'success')
        return redirect(url_for('myposts', pagination=pagination, page=page))

    else:
        flash('Your Selected Post Has Not Been Deleted!', 'danger')
    return render_template("myposts.html",post=post)

@app.route("/postupdate/<int:id>", methods=['GET','POST'])
@login_required
def postupdate(id):
    post = Post.query.get_or_404(id)
    #post = Post.query.filter_by(id=id).first()
    form = PostForm()
    if form.validate_on_submit():
        post.title=form.title.data 
        post.content=form.content.data 
        post.writer=current_user.username
        post.date=datetime.now().strftime("%Y-%m-%d %H:%M")
        db.session.add(post)
        db.session.commit()
        flash('Your Selected Post Has Been Updated!', 'success')
        return redirect(url_for('myposts', id=post.id))    
    form.title.data = post.title
    form.content.data = post.content
    current_user.username = post.writer
    post.date=datetime.now().strftime("%Y-%m-%d %H:%M")
    return render_template("postupdate.html", form=form, post=post)


############################### MESSAGE #################################

# Define the Post model
class Message(db.Model):
    __tablename__="message"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    sender = db.Column(db.Text, db.ForeignKey('user.username'), nullable=False)
    receiver = db.Column(db.Text, db.ForeignKey('user.username'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(12), nullable=False)
    

# Define the PostForm using WTForms
class MessageForm(FlaskForm):
    receiver = StringField('Receiver', validators=[InputRequired(), Length(min=4, max=30)])
    title = StringField('Title', validators=[InputRequired(), Length(min=4, max=100)])
    message = CKEditorField('Post', validators=[InputRequired(), Length(min=6, max=10000)])
    submit = SubmitField('Send Message')

@app.route('/messagenew', methods=['GET', 'POST'])
def messagenew():
    form = MessageForm()
    if form.validate_on_submit():
        receiver = form.receiver.data
        receive = User.query.filter_by(username=receiver).first()

        if receive:
            messagenew = Message(title=form.title.data, message=form.message.data, sender=current_user.username, receiver=receiver, date=datetime.now().strftime("%Y-%m-%d %H:%M"))
            db.session.add(messagenew)
            db.session.commit()
            flash('Your Message Has Been Sent!', 'success')
            return redirect(url_for('messagenew'))
        else:
            flash('Receiver not found!', 'danger')
            
    return render_template('messagenew.html', form=form)




@app.route("/messageinbox")
@login_required
def messageinbox():
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Message).order_by(desc(Message.date)))
    return render_template("messageinbox.html",pagination=pagination,page=page)

@app.route("/messageoutbox")
@login_required
def messageoutbox():
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Message).order_by(desc(Message.date)))
    return render_template("messageoutbox.html",pagination=pagination,page=page)


@app.route('/messageread/<int:id>')
@login_required
def messageread(id):
    message = Message.query.filter_by(id=id).first()
    
    return render_template('messageread.html',message=message)


@app.route('/messagedelete/<int:id>')
@login_required
def messagedelete(id):
    message = Message.query.filter_by(id=id).first()
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(db.select(Message).order_by(desc(Message.date)))
    if message:
        db.session.delete(message)
        db.session.commit()
        flash('Your Message Has Been Deleted!', 'success')
        return render_template("messageinbox.html",pagination=pagination,page=page)
    else:
        flash('Your Message Has Not Been Deleted!', 'danger')
    return render_template("messageinbox.html",pagination=pagination,page=page)

###################################################################


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")





""" @app.route("/friends")
@login_required
def friends():
    return render_template("friends.html") """
    



@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")




@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

#############################


""" from flask_admin import Admin
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
from flask_admin.contrib.sqla import ModelView
admin = Admin(app, name='Administrator', template_mode='bootstrap3')
#Admin.init_app(self, app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
app.run() """

########################### APP INITIALIZATION ###############

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

with app.app_context():
    db.create_all()