"""
Flask-приложение EchoMarket
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import database as db

app = Flask(__name__)
app.secret_key = 'echo-market-secret-key-change-in-production-2024'


# ========== ДЕКОРАТОРЫ ==========

def login_required(f):
    """Декоратор для проверки авторизации"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Требуется авторизация'}), 401
        return f(*args, **kwargs)

    return decorated_function


# ========== СТРАНИЦЫ ==========

@app.route('/')
def main():
    """Главная страница"""
    return render_template('main.html')


@app.route('/advertisements')
def adver():
    return render_template('advertisement.html')


@app.route('/shops')
def shops():
    return render_template('shop.html')


@app.route('/favour')
def favour():
    return render_template('favourites.html')


@app.route('/entrance')
def entrance():
    return render_template('enter.html')


# ========== API ЭНДПОИНТЫ ==========

@app.route('/api/register', methods=['POST'])
def api_register():
    """Регистрация пользователя"""
    data = request.get_json()

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    # Валидация
    errors = []
    if len(name) < 2:
        errors.append('Имя должно содержать минимум 2 символа')
    if '@' not in email:
        errors.append('Введите корректный email')
    if len(password) < 6:
        errors.append('Пароль должен содержать минимум 6 символов')
    if password != confirm_password:
        errors.append('Пароли не совпадают')

    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    # Создание пользователя
    result = db.create_user(name, email, phone, password)

    if result['success']:
        # Создаём сессию
        token = db.create_session(result['user_id'])
        session['user_id'] = result['user_id']
        session['user_name'] = result['name']
        session['user_email'] = result['email']
        session['token'] = token

        return jsonify({
            'success': True,
            'message': f'Добро пожаловать, {name}!',
            'user': {
                'id': result['user_id'],
                'name': result['name'],
                'email': result['email'],
                'phone': result['phone']
            }
        }), 201
    else:
        return jsonify({'success': False, 'error': result['error']}), 400


@app.route('/api/login', methods=['POST'])
def api_login():
    """Вход пользователя"""
    data = request.get_json()

    email = data.get('email', '').strip()
    password = data.get('password', '')

    result = db.login_user(email, password)

    if result['success']:
        # Создаём сессию
        token = db.create_session(result['user']['id'])
        session['user_id'] = result['user']['id']
        session['user_name'] = result['user']['name']
        session['user_email'] = result['user']['email']
        session['token'] = token

        return jsonify({
            'success': True,
            'message': f'Добро пожаловать, {result["user"]["name"]}!',
            'user': result['user']
        }), 200
    else:
        return jsonify({'success': False, 'error': result['error']}), 401


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Выход из аккаунта"""
    if 'token' in session:
        db.delete_session(session['token'])
    session.clear()
    return jsonify({'success': True, 'message': 'Вы вышли из аккаунта'}), 200


@app.route('/api/me', methods=['GET'])
@login_required
def api_get_profile():
    """Получение профиля текущего пользователя"""
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)

    if user:
        return jsonify(user), 200
    return jsonify({'error': 'Пользователь не найден'}), 404


@app.route('/api/check-auth', methods=['GET'])
def api_check_auth():
    """Проверка авторизации"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'name': session.get('user_name'),
                'email': session.get('user_email')
            }
        }), 200
    return jsonify({'authenticated': False}), 200


@app.route('/api/users', methods=['GET'])
@login_required
def api_get_users():
    """Получение всех пользователей (только для админа)"""
    users = db.get_all_users()
    return jsonify({'users': users}), 200


@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """Получение статистики"""
    stats = db.get_stats()
    return jsonify(stats), 200


# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 EchoMarket сервер запущен!")
    print("=" * 50)
    print(f"📁 База данных: {db.DB_PATH}")
    print(f"🌐 Адрес: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='127.7.7.7', port=7777)