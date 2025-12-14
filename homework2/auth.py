from models import User

class DuplicateUser(Exception):
    pass

class UserNotFound(Exception):
    pass


def register_user(db, username, password):
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        raise DuplicateUser("User already exists")

    user = User(
        username=username,
        password=password
    )
    db.add(user)
    db.commit()


def login_user(db, username, password):
    user = db.query(User).filter_by(
        username=username,
        password=password
    ).first()
    if not user:
        raise UserNotFound("Invalid credentials")
    return user
