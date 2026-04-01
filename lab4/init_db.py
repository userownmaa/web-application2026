from app import app
from extensions import db
from models import User, Role

def init_database():
    with app.app_context():
        print("Удаление существующих таблиц...")
        db.drop_all()

        print("Создание таблиц...")
        db.create_all()

        print("Создание ролей...")
        roles_data = [
            {'name': 'Администратор', 'description': 'Полный доступ к системе'},
            {'name': 'Пользователь',  'description': 'Обычный пользователь'},
        ]

        roles = {}
        for role_data in roles_data:
            role = Role(**role_data)
            db.session.add(role)
            roles[role_data['name']] = role

        db.session.commit()
        print(f"Создано ролей: {len(roles)}")

        print("Создание тестовых пользователей...")
        users_data = [
            {
                'login': 'admin',
                'password': 'Admin2026!',
                'last_name': 'Момина',
                'first_name': 'Антонина',
                'middle_name': 'Алексеевна',
                'role': roles['Администратор']
            },
            {
                'login': 'moder',
                'password': 'Moder2026!',
                'last_name': 'Иванова',
                'first_name': 'Мария',
                'middle_name': 'Петровна',
                'role': roles['Администратор']
            },
            {
                'login': 'user1',
                'password': 'User2026!',
                'last_name': 'Петрова',
                'first_name': 'Елена',
                'middle_name': None,
                'role': roles['Пользователь']
            },
            {
                'login': 'guest',
                'password': 'Guest2026!',
                'last_name': None,
                'first_name': 'Гость',
                'middle_name': 'Гость',
                'role': None
            },
        ]

        for user_data in users_data:
            password = user_data.pop('password')
            role = user_data.pop('role')
            user = User(**user_data)
            user.set_password(password)
            user.role = role
            db.session.add(user)

        db.session.commit()
        print(f"Создано пользователей: {len(users_data)}")



if __name__ == '__main__':
    init_database()