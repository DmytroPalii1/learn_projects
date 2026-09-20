import json
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user_profile(username,age,password,role="User"):
    data={
        "username":username,
        "age":age,
        "password_hash":hash_password(password),
        "role":role
    }
    return data

def login_user(username,password,filename="users.json"):
    user=get_user(username,filename)
    if not user:
        return None
    if user["password_hash"]==hash_password(password):
        return True
    else:
        return False

def save_users(user_list,filename="users.json"):
    with open(filename,"w")as file:
        json.dump(user_list,file,indent=4)

def load_users(filename="users.json"):
    try:
        with open(filename,"r")as file:
           return json.load(file)
    except FileNotFoundError:
        return[]

def user_exists(username,database):
    for user in database:
        if user["username"]==username:
            return True
    return False


def add_user(new_user,filename="users.json"):
    database=load_users(filename)
    if user_exists(new_user["username"],database):
        return False
    else:
        database.append(new_user)
        save_users(database,filename)
        return True

def get_user(username, filename="users.json"):
    database=load_users(filename)
    for user in database:
        if user["username"]==username:
            return user
    return None

def update_user_role(username, new_role, filename="users.json"):
    database=load_users(filename)
    for user in database:
        if user["username"]==username:
            user["role"]=new_role
            save_users(database,filename)
            return True
    return False

def delete_user(username,filename="users.json"):
    database=load_users(filename)
    if not user_exists(username,database):
        return False
    updated_database=[user for user in database if user["username"]!=username]
    save_users(updated_database,filename)
    return True
