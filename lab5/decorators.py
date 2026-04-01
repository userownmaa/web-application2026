from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def check_rights(required_role=None, resource_owner_check=False):
    """
    Декоратор для проверки прав доступа
    :param required_role: название роли, которая имеет доступ ('admin' или None)
    :param resource_owner_check: проверять ли, что пользователь является владельцем ресурса
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if required_role == 'admin':
                if not current_user.role or current_user.role.name != 'Администратор':
                    flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                    return redirect(url_for('index'))
            
            if resource_owner_check:
                user_id = kwargs.get('user_id')
                if user_id and current_user.id != user_id:
                    if not current_user.role or current_user.role.name != 'Администратор':
                        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                        return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator