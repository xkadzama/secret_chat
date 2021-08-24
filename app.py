from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = '<SECRET KEY>'


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(10), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String, nullable=False)


class Msg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    channel = db.Column(db.Integer, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('key'):
        return redirect('/chat')
    if request.method == 'POST':
        key = request.form['key']
        check_key = db.session.query(Channel.id).filter_by(key=key).scalar() is not None
        if check_key:
            error = 'Such a key is already exists!'
            return render_template('index.html', error=error)
        else:
            channel = Channel(key=key)
            try:
                db.session.add(channel)
                db.session.commit()
                success = "You have successfully created a channel"
                return render_template('join.html', success=success)
            except:
                return 'DB Error!'
    else:
        return render_template('index.html')


@app.route('/join', methods=['GET', 'POST'])
def join():
    if session.get('key'):
        return redirect('/chat')
    if request.method == 'POST':
        key = request.form['key']
        nickname = request.form['nick']
        check_key = db.session.query(Channel.id).filter_by(key=key).scalar() is None
        if check_key:
            error = 'The key not found!'
            return render_template('join.html', error=error)
        else:
            user = User(nickname=nickname)
            try:
                db.session.add(user)
                db.session.commit()
                session['key'] = key
                session['author'] = nickname
                return redirect('/chat')
            except:
                return 'DB Error!'
    else:
        return render_template('join.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    if not session.get('key'):
        return "Error!"
    else:
        if request.method == 'POST':
            key = session.get('key')
            author = session.get('author')
            msg = request.form['msg']
            new_msg = Msg(channel=key, author=author, msg=msg)
            try:
                db.session.add(new_msg)
                db.session.commit()
                return "Success"
            except:
                return 'DB Error!'


@app.route('/chat')
def chat():
    if not session.get('key'):
        return redirect('/')
    else:
        key = session.get('key')
        messages = Msg.query.filter_by(channel=key).order_by(Msg.id.desc()).all()
        return render_template('chat.html', messages=messages)


@app.route('/get_msg')
def get_msg():
    if not session.get('key'):
        return redirect('/')
    else:
        key = session.get('key')
        messages = Msg.query.filter_by(channel=key).order_by(Msg.id.desc()).all()
        return render_template('msg.html', messages=messages)


@app.route('/logout')
def logout():
    session.pop('key')
    session.pop('author')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)