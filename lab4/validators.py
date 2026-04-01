import re

def validate_login(login):
    errors = []
    if not login:
        errors.append("Логин не может быть пустым")
    if len(login) < 5:
        errors.append("Логин должен быть не короче 5 символов")
    if not re.match(r'^[a-zA-Z0-9]+$', login):
        errors.append("Логин может содержать только латинские буквы и цифры")
    return errors


def validate_password(password):
    errors = []
    if not password:
        errors.append("Пароль не может быть пустым")
        return errors

    if len(password) < 8:
        errors.append("Пароль должен содержать не менее 8 символов")
    if len(password) > 128:
        errors.append("Пароль должен содержать не более 128 символов")

    if not re.search(r'[A-ZА-ЯЁ]', password):
        errors.append("Должна быть хотя бы одна заглавная буква")
    if not re.search(r'[a-zа-яё]', password):
        errors.append("Должна быть хотя бы одна строчная буква")

    if not re.search(r'[0-9]', password):
        errors.append("Должна быть хотя бы одна цифра")

    if ' ' in password:
        errors.append("Пароль не должен содержать пробелы")

    allowed = r'~!?@#$%^&*_\-+()[\]{}<>/\\|"\'.,:;'
    pattern = rf'^[a-zA-Zа-яА-ЯёЁ0-9{re.escape(allowed)}]+$'
    if not re.match(pattern, password):
        errors.append("Пароль содержит недопустимые символы")

    has_latin = bool(re.search(r'[a-zA-Z]', password))
    has_cyr = bool(re.search(r'[а-яА-ЯёЁ]', password))
    if has_latin and has_cyr:
        errors.append("Нельзя смешивать латинские и кириллические буквы")

    return errors


def validate_name(value, field_name):
    if not value or not value.strip():
        return [f"{field_name} не может быть пустым"]
    return []


def validate_user_form(form_data, is_edit=False, require_password=True):
    errors = {}

    if not is_edit:
        login_err = validate_login(form_data.get('login', ''))
        if login_err:
            errors['login'] = login_err

        if require_password:
            pw_err = validate_password(form_data.get('password', ''))
            if pw_err:
                errors['password'] = pw_err

    name_err = validate_name(form_data.get('first_name', ''), "Имя")
    if name_err:
        errors['first_name'] = name_err


    return errors