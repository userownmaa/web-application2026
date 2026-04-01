from flask import Flask, render_template, request, redirect, url_for, make_response, flash


app = Flask(__name__)
application = app
app.secret_key = 'my_secret_key_lab2' 


@app.route('/')
def index():
    return render_template('index.html', title='Задание')


@app.route('/request', methods=['GET', 'POST'])
def request_data():
    data = {
        'method': request.method,
        'url': request.url,
        'args': dict(request.args),
        'form': dict(request.form) if request.method == 'POST' else {},
        'headers': dict(request.headers),
        'cookies': request.cookies,
    }

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username and password:
            flash(f'Успешно отправлены данные: логин = {username}, пароьл = {password}', 'success')
        else:
            flash('Пустой ввод', 'warning')


    resp = make_response(render_template('request.html', title='Данные запроса', data=data))

    if 'lab2_test' not in request.cookies:
        resp.set_cookie('lab2_cookie', 'Test Flask', max_age=3600)

    return resp


@app.route('/phone_number', methods=['GET', 'POST'])
def phone_check():
    phone = ''
    formatted = ''
    error = None
    is_valid = False

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()

        if not phone:
            error = 'Поле не может быть пустым. Введите номер телефона.'
        else:
            allowed_chars = set('0123456789 +-().')
            invalid_chars = [c for c in phone if c not in allowed_chars]
            if invalid_chars:
                error = f'Недопустимые символы: {", ".join(set(invalid_chars))}. ' \
                        f'Разрешены только цифры, пробелы, +, -, (, ), .'
            else:
                if phone[:2] == '+8':
                    error = 'Неверный формат, может быть только +7'
                else:
                    digits = ''.join(c for c in phone if c.isdigit())
                    len_digits = len(digits)

                    if len_digits == 10:
                        digits = '7' + digits
                    elif len_digits == 11:
                        if digits[0] not in ('7', '8'):
                            error = 'Номер из 11 цифр должен начинаться с 7 или 8 (российский формат).'
                        else:
                            if digits[0] == '8':
                                digits = '7' + digits[1:]
                    else:
                        error = f'Неверное количество цифр: найдено {len_digits}. ' \
                                f'Должно быть 10 или 11 цифр.'

                    if not error:
                        is_valid = True
                        ten_digits = digits[-10:]
                        formatted = f"8-{ten_digits[0:3]}-{ten_digits[3:6]}-{ten_digits[6:8]}-{ten_digits[8:10]}"

    return render_template('phone.html',
                           title='Проверка номера',
                           phone=phone,
                           formatted=formatted,
                           error=error,
                           is_valid=is_valid)


if __name__ == '__main__':
    app.run(debug=True)