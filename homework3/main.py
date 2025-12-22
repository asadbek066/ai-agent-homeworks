from getpass import getpass
from dotenv import load_dotenv

from db import engine, SessionLocal
from models import Base, ChatRoom
from auth import register_user, login_user, DuplicateUser, UserNotFound
from agent import Agent,show_history_pairs
from google.genai import types
load_dotenv()
Base.metadata.create_all(bind=engine)
def main():
    db = SessionLocal()
    
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("> ")

        if choice == "1":
            username = input("Username: ")

            while True:
                password1 = getpass("Password: ")
                password2 = getpass("Password (again): ")

                if password1 != password2:
                    print(f"Passwords do not match for user '{username}'. Please try again.\n")
                    continue

                try:
                    register_user(db, username, password1)
                    print("Registered successfully")
                    break
                except DuplicateUser as e:
                    print(e)
                    break


        elif choice == "2":
            username = input("Username: ")
            password = getpass("Password: ")
            try:
                user = login_user(db, username, password)
            except UserNotFound as e:
                print(e)
                continue

            rooms = db.query(ChatRoom).filter_by(owner_id=user.id).all()
            print("\nChat Rooms:")
            for i, r in enumerate(rooms, 1):
                print(f"{i}. {r.name}")
            print("0. New room")

            sel = int(input("Enter a room number to join, or 0 to create a new room:"))
            if sel == 0:
                name = input("Room name: ")
                room = ChatRoom(name=name, owner_id=user.id)
                db.add(room)
                db.commit()
            else:
                room = rooms[sel - 1]
            agent = Agent(room.id)

            print("Type /bye to exit chat")
            while True:
                msg = input(f"{username}> ").strip()
                if not msg or msg == ' ':
                    print("Please type a message or /help.")
                    continue
                if msg.lower() == "/bye":
                    break
                if msg.startswith("/help"):
                    print("""Commands:
        /bye         Exit chat
        /history N   Show last N message pairs (e.g. /history 10)
                """)
                    continue

                if msg.startswith("/history"):
                    parts = msg.split()
                    if len(parts) != 2 or not parts[1].isdigit():
                        print("Usage: /history N")
                        continue

                    n = int(parts[1])
                    show_history_pairs(agent.session, room.id, n)
                    continue

                print("Agent:", agent.ask(msg))

        else:
            break

if __name__ == "__main__":
    main()
