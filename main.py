from flask import Flask, render_template, request, redirect
from flask_json import FlaskJSON, json_response, as_json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__, static_url_path='/static')
json = FlaskJSON(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campaign-database.sqlite'
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    campaigns = db.relationship('Campaign', backref='user')

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    player_count = db.Column(db.Integer)
    player_level = db.Column(db.Integer)
    completion = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    players = db.relationship('Player', backref='campaign')

combatants = db.Table('combatants',
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key=True),
    db.Column('combat_id', db.Integer, db.ForeignKey('combat.id'), primary_key=True)
)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(40))
    character_name = db.Column(db.String(40))
    damage_dealt = db.Column(db.Integer)
    damage_received = db.Column(db.Integer)
    healing_dealt = db.Column(db.Integer)
    average_saving_throw = db.Column(db.Integer)
    saves_made = db.Column(db.Integer)
    crit_successes = db.Column(db.Integer)
    crit_failures = db.Column(db.Integer)
    average_attack_roll = db.Column(db.Float)
    attacks_made = db.Column(db.Integer)
    enemy_save_rate = db.Column(db.Float)
    saves_forced = db.Column(db.Integer)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    combatant = db.relationship('Combat', secondary=combatants,
        backref=db.backref('combatants', lazy='dynamic'), lazy='dynamic')
    def __repr__(self):
        return f'<Player {self.player_name}'

class Combat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    def __repr__(self):
        return f'<Combat {self.name}'

with app.app_context():
    db.create_all()

app.config['SECRET_KEY'] = "sQ7ZZ2ujk2NqzQKIkeSSIOhR7EP7i0ZV"
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', error=0)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_check = request.form['confirm-password']

        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', error=1)

        if password != password_check:
            return render_template('register.html', error=2)

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect('/')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', error=0)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user is None:
            return render_template('login.html', error=1)

        if user.password == password:
            login_user(user)
            return redirect('/')
        else:
            return render_template('login.html', error=2)

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/campaigns')
@login_required
def campaigns():
    campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    return render_template('campaigns.html',campaigns=campaigns)

@app.route('/campaigns/create', methods=['GET','POST'])
@login_required
def campaign_create():
    if request.method == 'GET':
        return render_template('campaign-create.html',error=0)
    elif request.method == 'POST':
        name = request.form['name']
        count = request.form['count']
        level = request.form['level']
        completion = request.form['completion']
        if completion == 'True':
            completion = True
        else:
            completion = False

        campaign_test = Campaign.query.filter_by(name=name).first()
        if campaign_test:
            return render_template('campaign-create.html',error=1)

        campaign = Campaign(name=name, player_count=count, player_level=level,
                            completion=completion,user_id=current_user.id)
        db.session.add(campaign)
        db.session.commit()

        return redirect('/campaigns/' + str(campaign.id))

@app.route('/campaigns/<id>')
@login_required
def campaign(id):
    c = Campaign.query.filter_by(id=id).first()
    return render_template('campaign-id.html', campaign=c)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/api/players')
@as_json
def players():
    return redirect('/campaigns')

@app.errorhandler(401)
def e401(err):
    return render_template('error.html', error=401)

@app.errorhandler(403)
def e403(err):
    return render_template('error.html', error=403)

@app.errorhandler(404)
def e404(err):
    return render_template('error.html', error=404)

@app.errorhandler(502)
def e502(err):
    return render_template('error.html', error=502)

app.run(debug=True)
