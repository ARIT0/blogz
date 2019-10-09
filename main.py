from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
#from flask_paginate import Pagination, get_page_args

from datetime import datetime
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:myblogzpassword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "anDArIa19"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())
    blog_date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, blog_date=None):
        self.title = title
        self.body = body
        self.owner = owner #relationship owner for every task
        self.blog_date = blog_date
        

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner') #won't be a column

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login',  'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect('/login')


@app.route('/newpost', methods=['POST', 'GET'])
def new_post(): 
    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        entry_title = request.form["entry_title"]
        blog_entry = request.form["blog_entry"]
               
        title_error = ""
        entry_error = ""

        if not entry_title:
            title_error= "Please enter a title"
            return render_template('add_new_post.html', blog_entry= blog_entry, title_error=title_error)
        if not blog_entry:
            entry_error = "Please enter a blog post"
            return render_template('add_new_post.html', entry_title=entry_title, entry_error=entry_error)
        else:
            new_post = Blog(entry_title, blog_entry, owner)
            db.session.add(new_post)
            db.session.commit()

            return redirect("/blog?id={0}".format(new_post.id))
    
    return render_template('add_new_post.html')
    

@app.route('/blog', methods=['POST', 'GET'])  #displays all blog posts
def blog():

    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    per_page = 5
    
    #Individual Blog Entry
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('singlepost.html', blog=blog, user=blog.owner.username)

    #All post from a specific user
    if user_id:
        page = request.args.get('page', 1, type=int)
        user_name = User.query.get(user_id) #this worked
        blogz = Blog.query.filter_by(owner_id=user_id).order_by(Blog.blog_date.desc()).paginate(page, per_page, False)
        #In order for url_for to work you must import url_for in the first line of code
        next_url = url_for('blog', page=blogz.next_num) \
            if blogz.has_next else None
        prev_url = url_for('blog', page=blogz.prev_num) \
            if blogz.has_prev else None
        return render_template('singleUser.html', user=user_name, blogs=blogz.items,
                                next_url=next_url, prev_url=prev_url)

    #All the posts from all the users 
    else:
        page = request.args.get('page',1,type=int)
        entries = Blog.query.order_by(Blog.blog_date.desc()).paginate(page, per_page, False)
        next_url = url_for('blog', page=entries.next_num) \
            if entries.has_next else None
        prev_url = url_for('blog', page=entries.prev_num) \
            if entries.has_prev else None
        return render_template('main_blog_page.html', blog=entries.items,
                                 next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session["username"] = username
            flash("Logged In!") 
            return redirect("/newpost")
        elif not user:
            flash("Username does not exist.", 'error')
            return render_template("login.html")
        elif not check_pw_hash(password, user.pw_hash):
            flash("Password is incorrect.", 'error')
            return render_template("login.html", username=username)
        
    return render_template("login.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = ""

    if request.method == "GET":
        return render_template("signup.html")
    
    else: 
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not username or not password:
            flash('Must enter a username and a password', 'error')
        elif existing_user:
            flash('Username already exists')
        elif len(username) < 3 or len(password) < 3:
            flash('Invalid username or password.', 'error')
        elif password != verify:
            flash("Passwords don't match.", 'error')
        elif not existing_user and password == verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        
    return render_template('signup.html', username=username)


@app.route('/logout')
def logout():
    del session['username'] #deletes username from session
    flash("Logged Out!")
    return redirect('/blog')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template("index.html", users=users)


if __name__ == '__main__':
    app.run()
