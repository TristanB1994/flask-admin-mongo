from flask import Flask, url_for, redirect, render_template, request, flash
from flask_mongoengine import MongoEngine
from mongoengine import Document, StringField, ObjectIdField
import json, random, string
from bson import ObjectId
from wtforms import form, fields, validators
from flask_admin.contrib.pymongo import ModelView
from flask_admin import Admin, AdminIndexView
from itsdangerous import URLSafeSerializer
from flask_login import LoginManager, current_user, login_user, logout_user, UserMixin, login_required

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create Serializer
serializer = URLSafeSerializer(app.secret_key)

# MongoDB settings
app.config['MONGODB_SETTINGS'] = {
    'alias':'registry',
    'db': 'registry',
    'host': '0.0.0.0',
    'port': 27017,
    'username': 'admin',
    'password': 'password'
    }


# Build db connection with straight mongoengine
# mongo = connect('registry', host='mongodb://admin:password@0.0.0.0:27017/registry', alias='registry-db')

mongo = MongoEngine(app)
registry = mongo.get_db('registry')
members = registry.member

# Initialize flask-login
login_manager = LoginManager(app)

# Define login and registation forms (for flask-login)
class LoginForm(form.Form):
    name = fields.TextField(validators=[validators.DataRequired()])    

class RegistrationForm(form.Form):
    name = fields.TextField(validators=[validators.DataRequired()])

    def validate_login(self, field):
        if members.count_documents({'name':field.data}):
            flash('Duplicate username')
            return False
        else:
            return True

################################ ::: Collection Model

# Class definition for Member Collection
class Member(UserMixin, Document):

    _id = ObjectIdField(primary_key=True)
    name = StringField(max_length=80, unique=True)
    session_token = StringField(max_length=120)
    meta = {'db_alias':'registry'}

    def get_id(self):
        if self.session_token:
            return self.session_token
        else:
            return None

    def __repr__(self):
        return f"<Member {self.name}>"

################################ ::: Support Functions

# Generate a member object from dictionary
def member_from_dict(model, obj_dict=None):
        fields = Member._fields.keys()
        new_member = model()
        if obj_dict:        
            keys = obj_dict.keys()
            for k, v in obj_dict.items():
                if str(k) in fields or str(k) == '_id':
                    if str(k) == '_id':
                        key = 'id'
                        setattr(new_member, key, v)
                    setattr(new_member, k, v)
            return new_member
        if obj_dict == None:
            return ValueError('No dict provided')

# Flask-Login Userloader decorator
@login_manager.user_loader
def load_user(session_token):
    member_data = members.find_one({'session_token': session_token})
    if member_data:
        return member_from_dict(Member, member_data)
    return None

# Session token serializer 
def generate_token(form, model):
    random_str = random.sample(string.ascii_letters, 5)
    if not form.name.data or form.name.data == None:
        return ValueError(form.name.data)
    model['session_token'] = serializer.dumps([form.name.data, random_str])
    return model

################################ ::: Admin Classess

# Member View Class
class MemberView(ModelView):

    column_list = ['_id','name','session_token']
    object_id_converter = str
    can_export = True
    export_types = ['csv','xlsx']
    inline_models = [Member]
    form = LoginForm

    def is_accessible(self):
        return current_user.is_authenticated   
    
    def inaccessible_callback(self, name, **kwargs):
        return '<h1> You are not logged in</h1>'

    def on_model_change(self, form, model, is_created):
        generate_token(form, model)
        
# Index View Class
class MyAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return current_user.is_authenticated

# Create admin
admin = Admin(app, index_view=MyAdminIndexView(), template_mode='bootstrap3')

# Create additional admin views
admin.add_view(MemberView(coll=members, name='Member', endpoint='member'))

################################ ::: App routes

@app.route('/')
def home():
    try:
        user_data = members.find_one({'name':current_user.name}).items()
    except:
        user_data = None
    return render_template('index.html', user=current_user, user_data=user_data)

@app.route('/register', methods=['GET','POST'])
def register_view():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate_login(form.name):
        member = members.find_one({'name' : form.name.data})
        if not member == None:
            flash('That user already exists')
            return render_template('form.html', form=form)
        new_user = form.data 
        new_user = generate_token(form, new_user)
        user = member_from_dict(Member, new_user)
        user.save()
        login_user(user)
        return redirect( url_for('home') )
    return render_template('form.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        member_data = members.find_one({'name' : form.name.data})
        #validation stuff
        # member returns dictionary of collection info
        if not member_data == None:
            user = member_from_dict(Member, member_data)
            login_user(user)
            flash(f"Logged in as {user['name']}")
            return redirect('/')
        # No result from member collection
        flash("That username doesn't exist")
        return redirect('/login')
    return render_template('form.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect( url_for('home') )

if __name__ == '__main__':
    # Start app
    app.run(debug=True)