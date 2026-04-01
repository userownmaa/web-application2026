from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db, login_manager          
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from validators import validate_user_form, validate_password
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'lab4_momina_antonina_super_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_lab4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)                         
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему'
login_manager.login_message_category = 'warning'

from models import User, Role

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():    
    users = User.query.all()
    return render_template('index.html', users=users, title='Список пользователей')


@app.route('/users/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user, title='Просмотр пользователя')


@app.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    roles = Role.query.all()
    if request.method == 'POST':
        form_data = {
            'login': request.form.get('login', '').strip(),
            'password': request.form.get('password', ''),
            'last_name': request.form.get('last_name', '').strip(),
            'first_name': request.form.get('first_name', '').strip(),
            'middle_name': request.form.get('middle_name', '').strip(),
            'role_id': request.form.get('role_id', '')
        }

        errors = validate_user_form(form_data, is_edit=False, require_password=True)

        if errors:
            return render_template('user_form.html',
                                 form_data=form_data,
                                 errors=errors,
                                 roles=roles,
                                 is_edit=False,
                                 title='Создание пользователя')

        try:
            user = User(
                login=form_data['login'],
                last_name=form_data['last_name'] or None,
                first_name=form_data['first_name'],
                middle_name=form_data['middle_name'] or None,
                role_id=int(form_data['role_id']) if form_data['role_id'] else None,
                created_at=datetime.utcnow()
            )
            user.set_password(form_data['password'])
            db.session.add(user)
            db.session.commit()
            flash('Пользователь успешно создан', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании: {str(e)}', 'danger')

    return render_template('user_form.html',
                         form_data={},
                         errors={},
                         roles=roles,
                         is_edit=False,
                         title='Создание пользователя')


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()

    if request.method == 'POST':
        form_data = {
            'last_name': request.form.get('last_name', '').strip(),
            'first_name': request.form.get('first_name', '').strip(),
            'middle_name': request.form.get('middle_name', '').strip(),
            'role_id': request.form.get('role_id', '')
        }

        errors = validate_user_form(form_data, is_edit=True, require_password=False)

        if errors:
            return render_template('user_form.html',
                                 form_data=form_data,
                                 errors=errors,
                                 roles=roles,
                                 is_edit=True,
                                 user=user,
                                 title='Редактирование пользователя')

        try:
            user.last_name = form_data['last_name'] or None
            user.first_name = form_data['first_name']
            user.middle_name = form_data['middle_name'] or None
            user.role_id = int(form_data['role_id']) if form_data['role_id'] else None
            db.session.commit()
            flash('Данные успешно обновлены', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении: {str(e)}', 'danger')

    form_data = {
        'last_name': user.last_name or '',
        'first_name': user.first_name or '',
        'middle_name': user.middle_name or '',
        'role_id': str(user.role_id) if user.role_id else ''
    }

    return render_template('user_form.html',
                         form_data=form_data,
                         errors={},
                         roles=roles,
                         is_edit=True,
                         user=user,
                         title='Редактирование пользователя')


@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь удалён', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении: {str(e)}', 'danger')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        login_name = request.form.get('login', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(login=login_name).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Вы вошли в систему', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('login.html', title='Вход')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old = request.form.get('old_password', '')
        new_p = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        errors = {}

        if not current_user.check_password(old):
            errors['old_password'] = ['Неверный старый пароль']

        pw_errors = validate_password(new_p)
        if pw_errors:
            errors['new_password'] = pw_errors

        if new_p != confirm:
            errors['confirm_password'] = ['Пароли не совпадают']

        if errors:
            return render_template('change_password.html', errors=errors, title='Изменение пароля')

        try:
            current_user.set_password(new_p)
            db.session.commit()
            flash('Пароль успешно изменён', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')

    return render_template('change_password.html', errors={}, title='Изменение пароля')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()           
    app.run(debug=True)