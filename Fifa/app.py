from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app3.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])  # obsługa /login
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


class MatchFifa(db.Model):
    id_match = db.Column(db.Integer, primary_key=True)
    country_one = db.Column(db.String)
    country_two = db.Column(db.String)
    country_one_goals = db.Column(db.Integer)
    country_two_goals = db.Column(db.Integer)
    date_match = db.Column(db.DateTime)


with app.app_context():
    db.create_all()
    #new_user = User(username='root', password='root')
    #db.session.add(new_user)
    db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        country_one = request.form['country_one']
        country_two = request.form['country_two']
        country_one_goals = request.form['country_one_goals']
        country_two_goals = request.form['country_two_goals']
        date_match = datetime.strptime(request.form['date_match'], '%Y-%m-%d')
        new_match = MatchFifa(country_one=country_one, country_two=country_two, country_one_goals=country_one_goals, country_two_goals=country_two_goals, date_match=date_match)
        db.session.add(new_match)
        db.session.commit()

    sort_by = request.args.get('sort_by', 'id_match')
    if sort_by == 'id_match':
        matches = MatchFifa.query.order_by(MatchFifa.id_match).all()
    elif sort_by == 'country_one':
        matches = MatchFifa.query.order_by(MatchFifa.country_one).all()
    elif sort_by == 'country_two':
        matches = MatchFifa.query.order_by(MatchFifa.country_two).all()
    elif sort_by == 'country_one_goals':
        matches = MatchFifa.query.order_by(MatchFifa.country_one_goals).all()
    elif sort_by == 'country_two_goals':
        matches = MatchFifa.query.order_by(MatchFifa.country_two_goals).all()
    elif sort_by == 'date_match':
        matches = MatchFifa.query.order_by(MatchFifa.date_match).all()
    else:
        matches = MatchFifa.query.all()

    return render_template('index.html', matches=matches)


@app.route('/delete_match', methods=['POST'])  # obsługa /delete_game
@login_required
def delete_match():
    id_match = request.form['id_match']
    match = MatchFifa.query.get(id_match)
    db.session.delete(match)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.run(debug=False, port=3000, host='0.0.0.0')
