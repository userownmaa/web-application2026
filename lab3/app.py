from flask import Flask, render_template, request, redirect, url_for, make_response, flash, session

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user, login_manager


app = Flask(__name__)
application = app
app.secret_key = 'secret_key_lab3_momina_antonina' 


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_page'          
login_manager.login_message = 'Пожалуйста, войдите, чтобы получить доступ к этой странице.'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

fake_users = {
    "user": {"id": "1", "password": "qwerty"}
}

@login_manager.user_loader
def load_user(user_id):
    for username, data in fake_users.items():
        if data["id"] == user_id:
            return User(data["id"], username)
    return None


@app.route('/')
def index():
    message = None
    if current_user.is_authenticated:
        message = f"Вы вошли как: {current_user.username}"
    return render_template('index.html', title='Задание', message=message)


@app.route('/counter', methods=['GET', 'POST'])
def counter_page():

    if 'visit_count' not in session:
        session['visit_count'] = 0
    
    session['visit_count'] += 1
    
    count = session['visit_count']
    
    return render_template('counter.html', title='Счетчик посещений', count=count)


@app.route('/auth', methods=['GET', 'POST'])
def auth_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        if username in fake_users and fake_users[username]["password"] == password:
            user = User(fake_users[username]["id"], username)
            login_user(user, remember=remember)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('auth.html', title='Аутентификация')

@app.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('index'))


@app.route('/secret', methods=['GET'])
def secret_page():

    return render_template('secret.html', title='Секретная страница')


if __name__ == '__main__':
    app.run(debug=True)