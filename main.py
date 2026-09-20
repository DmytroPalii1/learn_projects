import os
from dotenv import load_dotenv
load_dotenv()
secret=os.getenv("SECRET_KEY")
if not secret:
  print("Warnung! Kein Secret Key in der .env-Datei gefunden")

from database import(
    create_user_profile,
    login_user,
    load_users,
    add_user,
    delete_user,
    get_user,
    update_user_role 
)

def main_menu():
    current_user=None

    while True:
        print("=== Backend CLI ===")
        if current_user:
            user_data = get_user(current_user)
            role = user_data.get("role") if user_data else "User"
            print(f"Status: Eingeloggt als [{current_user}] | Rolle: [{role}]")
        else:
            print("Status: Nicht eingeloggt (Gast)")
        
        print("1. User hinzufügen (Registrieren)")
        print("2. User suchen (Nur für Eingeloggte)") 
        print("3. User-Rolle aktualisieren (Nur für Admins)")  
        print("4. User löschen (Nur für Admins)") 
        print("5. Alle User anzeigen")
        print("6. " + ("Abmelden" if current_user else "Anmelden")) 
        print("7. Beenden")

        choice = input("Wähle eine Option (1-7): ")
    
    
        if choice=="1":
            username=input("Benutzername: ")
            try:
                age=int(input("Alter: "))
            except ValueError:
                print("Ungültige Eingabe. Bitte gib eine Zahl ein")
                continue
            password=input("Passwort erstellen: ")
            role=input("User-Rolle (Standard: User): ")or "User"
            if add_user(create_user_profile(username,age,password,role)):
               print("User erfolgreich hinzugefügt")
            else:
                print("Fehler: Benutzername bereits vergeben")

        elif choice=="2":
               if not current_user:
                   print("Zugriff verweigert! Du musst dich einloggen um User zu suchen")
                   continue
               username=input("Benutzername: ")
               user=get_user(username)
               if user:
                   print(user)
               else:
                   print("Dieser User existiert nicht")

        elif choice=="3":
               if not current_user:
                   print("Zugriff verweigert. Bitte zuerst einloggen")
                   continue
               current_user_data=get_user(current_user)
               if current_user_data.get("role")!="Admin":
                   print("Zugriff verweigert! Nur Admin dürfen Rollen ändern")
                   continue
               
               username=input("Benutzername: ")
               new_role=input("Neue Rolle: ")
               if update_user_role(username,new_role):
                   print("User-Rolle erfolgreich aktualisiert.")
               else:
                   print("Dieser Benutzer existiert nicht.")

        elif choice=="4":
               if not current_user:
                  print("Zugriff verweigert. Bitte zuerst einloggen")
                  continue
               current_user_data=get_user(current_user)
               if current_user_data.get("role")!="Admin":
                    print("Zugriff verweigert! Nur Admin dürfen Rollen ändern")
                    continue
               username=input("Benutzername: ")
               if delete_user(username):
                   print("User erfolgreich gelöscht")
               else:
                   print("Dieser Benutzer existiert nicht.")

        elif choice=="5":
            print(load_users())

        elif choice=="6":
            if current_user:
               print(f"Auf Wiedersehen {current_user}!")
               current_user=None
            else:   
               username=input("Benutzername: ")
               password=input("Passwort: ")
               result=login_user(username,password)
               if result is True:
                   current_user=username
                   print(f"Erfolgreich angemeldet als {current_user}")
               elif result is None:
                   print("Dieser User existiert nicht")
               else:
                   print("Falsches Passwort")

        elif choice=="7":
            print("Programm wird beendet. Auf Wiedersehen!")
            break

        else:
            print("Ungültige Eingabe. Bitte wähle 1-7")

main_menu()
