
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
#from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import Form, StringField, TextAreaField, validators, BooleanField, PasswordField, ValidationError, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, InputRequired
from sqlalchemy.ext.horizontal_shard import ShardedSession
from flask_sqlalchemy.session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from sqlalchemy import desc
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whatsupbuddy.sqlite3'
app.config['SECRET_KEY'] = "jbcisbiuifvuuugiohouhhoisoishoviuhiu"

bp = Blueprint("guestbook", __name__, url_prefix="/guestbook")

db = SQLAlchemy(app)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

with app.app_context():
    db.create_all()
    
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
    scrap = TextAreaField('Scrap', validators=[DataRequired(), Length(min=5, max=300)])
    #recaptcha = RecaptchaField()
    
    submit = SubmitField('Post Scrap')
    

@bp.route('/guestbook', methods=['GET', 'POST'])
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



""" @app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        name = request.form['name']
        scrap = request.form['scrap']
        
        if not request.form['name'] or not request.form['scrap']:
            flash('Please enter all the fields', 'error')
        else:
        # Insert data into the database
            guestscrap = Guestbook(name = name, scrap = scrap, date=datetime.now())
            db.session.add(guestscrap)
            db.session.commit()
            flash('Your Scrap Has Been Posted!', 'success')
            return redirect(url_for('guestbook'))
    page = db.paginate(db.select(Guestbook).order_by(Guestbook.date) )
    return render_template("guestbook.html", page = page)  
 """
