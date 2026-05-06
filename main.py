from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/advertisement')
def adver():
    return render_template('advertisement.html')

@app.route('/shops.html')
def shops():
    return render_template('shop.html')

@app.route('/favour')
def favour():
    return render_template('favourites.html')


if __name__ == '__main__':
    app.run(port=777, host='127.7.7.7')
