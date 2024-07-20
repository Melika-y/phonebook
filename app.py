from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

client = MongoClient("mongodb://localhost:27017/")
db = client["phonebook"]
contacts_collection = db["Person"]
users_collection = db["Users"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'

phone_pattern = re.compile(r'^\d{11}$')

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user["_id"]))
    return None

def validate_phone_number(phone):
    if phone_pattern.match(phone):
        return True
    else:
        return False

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            user_obj = User(str(user["_id"]))
            login_user(user_obj)
            return redirect(url_for('index'))
        return "Invalid email or password", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if users_collection.find_one({"email": email}):
            return "Email already exists", 400
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({"email": email, "password": hashed_password})
        return redirect(url_for('user_login'))
    return render_template('register.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_login'))

@app.route('/contacts', methods=['POST'])
@login_required
def add_contact():
    data = request.json
    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
        
    if validate_phone_number(phone):
        contact = {
            "name": name,
            "phone": phone,
            "email": email,
            "user_id": current_user.id
        }
        contacts_collection.insert_one(contact)
        return jsonify({"message": "Contact added successfully!"}), 201
    else:
        return jsonify({"message": "Invalid phone number. It should be 11 digits."}), 400

@app.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    contacts = list(contacts_collection.find({"user_id": current_user.id}))
    for contact in contacts:
        contact["_id"] = str(contact["_id"])
    return jsonify(contacts), 200

@app.route('/contacts/<contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    data = request.json
    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    
    update_fields = {}
    if name:
        update_fields["name"] = name
    if phone and validate_phone_number(phone):
        update_fields["phone"] = phone
    if email:
        update_fields["email"] = email
    elif phone:
        return jsonify({"message": "Invalid phone number. It should be 11 digits."}), 400
    
    contacts_collection.update_one({"_id": ObjectId(contact_id), "user_id": current_user.id}, {"$set": update_fields})
    return jsonify({"message": "Contact updated successfully!"}), 200

@app.route('/contacts/<contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    contacts_collection.delete_one({"_id": ObjectId(contact_id), "user_id": current_user.id})
    return jsonify({"message": "Contact deleted successfully!"}), 200

if __name__ == "__main__":
    app.run(debug=True)
