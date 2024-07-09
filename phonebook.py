from pymongo import MongoClient
import re
client = MongoClient("mongodb://localhost:27017/")
db = client["phonebook"]
contacts_collection = db["Person"]

if "Person" not in db.list_collection_names():
    
    contacts_collection.insert_one({"name": "Test User", "phone": "0000000000", "email": "test@example.com"})
  
    contacts_collection.delete_one({"name": "Test User"})

def is_valid_phone(phone):
    pattern = r'^\d{10}$'  
    return re.match(pattern, phone) is not None

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def add_contact(name, phone, email):
      if not is_valid_phone(phone):
        print("Invalid phone number. Please enter a 10-digit phone number.")
        return
      if not is_valid_email(email):
        print("Invalid email address. Please enter a valid email.")
        return
      contact = {
        "name": name,
        "phone": phone,
        "email": email
    }
      contacts_collection.insert_one(contact)
      print("Contact added successfully!")

def get_contacts():
    contacts = contacts_collection.find()
    for contact in contacts:
        print(contact)

def update_contact(contact_id, name=None, phone=None, email=None):
    update_fields = {}
    if name:
        update_fields["name"] = name
    if phone:
          if not is_valid_phone(phone):
            print("Invalid phone number. Please enter a 10-digit phone number.")
            return
          update_fields["phone"] = phone
    if email:
         if not is_valid_email(email):
            print("Invalid email address. Please enter a valid email.")
            return
         update_fields["email"] = email
    contacts_collection.update_one({"_id": contact_id}, {"$set": update_fields})
    print("Contact updated successfully!")

def delete_contact(contact_id):
    contacts_collection.delete_one({"_id": contact_id})
    print("Contact deleted successfully!")

def main():
    while True:
        print("\nPhonebook Menu:")
        print("1. Add Contact")
        print("2. View Contacts")
        print("3. Update Contact")
        print("4. Delete Contact")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter name: ")

            phone = input("Enter phone number: ")
            email = input("Enter email: ")
            add_contact(name, phone, email)

        elif choice == '2':
            get_contacts()
        elif choice == '3':
            contact_id = input("Enter contact ID to update: ")
            name = input("Enter new name (leave blank to keep current): ")
            phone = input("Enter new phone number (leave blank to keep current): ")
            email = input("Enter new email (leave blank to keep current): ")
            update_contact(contact_id, name, phone, email)
        elif choice == '4':
            contact_id = input("Enter contact ID to delete: ")
            delete_contact(contact_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
  main()