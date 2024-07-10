from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
import re

app= Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')


client = MongoClient("mongodb://localhost:27017/")
db = client["phonebook"]
contacts_collection = db["Person"]

phone_pattern = re.compile(r'^\d{11}$')

def validate_phone(phone):
    if phone_pattern.match(phone):
        return True
    else:
        return False


email_pattern = re.compile( r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def validate_email(email):
    if email_pattern.match(email):
        return True
    else:
        return False

@app.route('/contacts', methods=['POST'])
def add_contact():
    data = request.json
    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    
    if validate_phone(phone):
        contact = {
            "name":name,
            "phone": phone,
            "email":email
        }
        contacts_collection.insert_one(contact)
        return jsonify({"message": "Contact added successfully!"}), 201
    else:
        return jsonify({"message": "Invalid phone. It should be 11 digits."}), 400

@app.route('/contacts', methods=['GET'])
def get_contacts():
    contacts = list(contacts_collection.find())
    for contact in contacts:
        contact["_id"] = str(contact["_id"])
    return jsonify(contacts), 200

@app.route('/contacts/<contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data = request.json
    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    
    update_fields = {}
    if name:
        update_fields["name"] = name
    if phone and validate_phone(phone):
        update_fields["phone"] = phone
    if email:
        update_fields["email"] = email    
    if phone:
        return jsonify({"message": "Invalid phone number. It should be 11 digits."}), 400
    elif email:
         return jsonify({"message": "email is incorrect."}), 400

    contacts_collection.update_one({"_id": ObjectId(contact_id)}, {"$set": update_fields})
    return jsonify({"message": "Contact updated successfully!"}), 200

@app.route('/contacts/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    contacts_collection.delete_one({"_id": ObjectId(contact_id)})
    return jsonify({"message": "Contact deleted successfully!"}), 200

if __name__ == "__main__":
    app.run(debug=True)