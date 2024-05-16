import os
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, exc, text
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///StarCrossed.db'
app.config['SQLAlchemy_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "TisASecret"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
def app_context(self):
  with app.app_context():
    db.create_all()
    db.session.commit()
    for user in User.query.all():
      print(user)
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(20), index = True, unique = True)
  email = db.Column(db.String(75), index = True, unique = False)
  date_of_birth = db.Column(db.String(10), index = True, unique = False)
  star_sign = db.Column(db.String(11), index = True, unique = False)
  password_hash = db.Column(db.String(128))
  join_time = db.Column(db.DateTime(), index = True, default = datetime.utcnow)
  #contacts = db.relationship("Contacts", backref="user", lazy="dynamic")
  #set_password method
  def set_password(self, password):
    self.password_hash = generate_password_hash(password)
  def check_password(self, password):
    return check_password_hash(self.password_hash, password)
  def __repr__(self):
    return '{}, born {}'.format(self.username, self.date_of_birth)
#class Contacts(db.Model):
  #id = db.Column(db.Integer, primary_key = True)
  #contact_id = db.Column(db.Integer, db.ForeignKey('user.id'))
class RegistrationForm(FlaskForm):
  email = StringField('Email Address (school)', validators=[DataRequired(), Email()])
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  star_sign = SelectField('Star Sign (Zodiac)', choices=["Aries", "Taurus", "Sagittarius", "Gemini", "Virgo", "Leo", "Cancer", "Scorpio", "Libra", "Pisces", "Capricorn", "Aquarius"], validators=[DataRequired()])
  date_of_birth = DateField('Birthday:', validators=[DataRequired()])
  submit = SubmitField('Submit')
class LoginForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  remember_me = BooleanField('Remember Me')
  submit = SubmitField('Sign In')
#Sign up page route
@app.route('/SignUp.html', methods=['GET', 'POST'])
def register():
  form = RegistrationForm(csrf_enabled = False)
  if form.validate_on_submit():
    user = User(email = form.email.data, username = form.username.data, star_sign = form.star_sign.data, date_of_birth = form.date_of_birth.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    return redirect("/")
  return render_template("SignUp.html", form=form)
@app.route("/", methods=['GET', 'POST'])
def login():
  form = LoginForm(csrf_enabled = False)
  if form.validate_on_submit():
    #Grabs inputted user username from SQL table
    user = User.query.filter_by(username = form.username.data).first()
    #Password and username in the same row and under the same id
    if user and user.check_password(form.password.data):
      login_user(user, remember=form.remember_me.data)
      return redirect('Dashboard.html')
    else:
      return redirect("/")
  return render_template("index.html", form=form)
if os.path.exists('sqlite:///StarCrossed.db'):
  os.remove('sqlite:///StarCrossed.db')
#Loads page route
@login_manager.user_loader
def load_user(id):
  return User.query.get(id)
@login_required
@app.route("/Dashboard.html")
def dashboard():
  app_context(User)
  user = User()
  compatible_with = []
  star_sign_key = {
    "Aries" : ["Gemini", "Aquarius"],
    "Taurus" : ["Cancer", "Pisces"],
    "Gemini" : ["Aries", "Leo"],
    "Cancer" : ["Taurus", "Virgo"],
    "Leo" : ["Gemini", "Libra"],
    "Virgo" : ["Cancer", "Scorpio"],
    "Libra" : ["Leo", "Sagittarius"],
    "Scorpio" : ["Virgo", "Capricorn"],
    "Sagittarius" : ["Libra", "Aquarius"],
    "Capricorn" : ["Scorpio", "Pisces"],
    "Aquarius" : ["Aries", "Sagittarius"],
    "Pisces" : ["Taurus", "Capricorn"],
  }
  for sign, compatibles in star_sign_key.items():
    if current_user.star_sign == sign:
      compatible_with.append(compatibles)
  return render_template("Dashboard.html", compatibled=compatible_with)
@app.route("/aries.html")
def aries():
  list_of_aries = User.query.filter(User.star_sign == "Aries").all() 
  return render_template("aries.html", aries_users = list_of_aries)
@app.route("/taurus.html")
def taurus():
  list_of_taurus = User.query.filter(User.star_sign == "Taurus").all() 
  return render_template("taurus.html", taurus_users = list_of_taurus)
@app.route("/chat.html")
def chat():
  return render_template("chat.html")
@app.route("/")
@login_required
def logout():
  return render_template("userPage.html", user=user)
