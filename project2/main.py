from sqlmodel import Session, select
from database import User, engine

def create_users():
    new_user = User(
        username = "spiderman",
        email = "spiderman@gmail.com"
    )

    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

    print(f"User successfuly created! ID: {new_user.id}, name: {new_user.username}")


def get_users():
    with Session(engine) as session:

        statement = select(User)

        results = session.exec(statement).all()

        print("--- ALL USERS IN THE DATABASE ---")
        for user in results:
            print(f"ID: {user.id} | name: {user.username} | email: {user.email}")


def update_users():
    with Session(engine) as session:

        statement = select(User).where(User.id == 1)
        user = session.exec(statement).first()

        if user:
            print(f"old name: {user.username} | old mail: {user.email}")

            user.email = "peter.parker@gmail.com"

            session.add(user)
            session.commit()
            session.refresh(user)

            print(f"new mail successfuly saved: {user.email}")

        else:
            print("user not found")


def delete_users():
    with Session(engine) as session:

        statement = select(User).where(User.id == 1)
        user = session.exec(statement).first()

        if user:
            session.delete(user)
            session.commit()
            print(f"User '{user.username}' with ID {user.id} was successfuly deleted!")

        else:
            print("user not found - nothing to delete")


if __name__ == "__main__":
    #create_users()
    #update_users()
    delete_users()
    get_users()