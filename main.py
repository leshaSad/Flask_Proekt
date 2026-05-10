from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('main.html')
    elif request.method == 'POST':
        print(request.form)

@app.route('/advertisement')
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


if __name__ == '__main__':
    app.run(port=7777, host='127.7.7.7')
