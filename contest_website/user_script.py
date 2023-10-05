import os
import json
import django
# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "contest_website.settings")
django.setup()
from django.contrib.auth.models import User
from django.db.utils import IntegrityError



# Load data from JSON file
with open("user_data.json", "r") as file:
    user_data_list = json.load(file)

# Create a list to store user information
user_info_list = []

# Iterate through the list of user data
for user_data in user_data_list:
    # Extract data from JSON
    username = user_data["Email"]
    phone_number = str(user_data["Phone"])
    name_parts = user_data["Name"].split()
    first_name = name_parts[0]
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    email_parts = username.split('.')
    if len(email_parts) >= 2:
        email_prefix = email_parts[0]
    else:
        email_prefix = username
    password = f"{email_prefix}@{phone_number[-5:]}"

    # Create a new user instance and save it to the database
    try:
        # Try to create a new user
        user = User.objects.create_user(username=username, password=password)
        user.save()

        # Add user info to the list
        user_info_list.append({
            "username": username,
            "password": password
        })
    except IntegrityError:
        # Handle the case where the username (email) is not unique
        print(f"User with username {username} already exists.")

# Convert the user_info_list to JSON
user_info_json = json.dumps(user_info_list, indent=4)

# Save the user info JSON to a file
with open("user_info.json", "w") as info_file:
    info_file.write(user_info_json)

print("User info JSON saved to user_info.json")
