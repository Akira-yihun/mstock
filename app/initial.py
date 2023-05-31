from . import db
from .models import Role, User

def initial_database(email, password):
    '''
    insert data into Role & User
    '''
    try:
        roles = Role.query.all()
    except Exception as e:
        db.create_all()
    try:
        roles = Role.query.all()
    except Exception as e:
        print(e)
    try:
        rolelis = [
            [10, 'ADMIN', 'Manage system.'],
            [20, 'USER', 'Use system'],
            [30, 'CHECKER', 'Check comment.']
        ]
        for i in rolelis:
            role = Role(
                roleid = i[0],
                rolename = i[1],
                description = i[2]
            )
            db.session.add(role)
        admin = User(
            userid = 10001,
            username = 'admin',
            roleid = 10,
            password = password,
            email = email
        )
        db.session.add(admin)
        try:
            db.session.commit()
            print('success')
        except Exception as e:
            print(e)
            db.session.rollback()
        roles = Role.query.all()
    except Exception as e:
        print(e)
    print(roles)
    users = User.query.all()
    print(users)