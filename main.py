from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:mynewpassword@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

#titles = []
posts = []

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        entry_title = request.form['entry_title']
        blog_entry = request.form["blog_entry"]
        #titles.append(entry_title)
        posts.append(entry_title)
        posts.append(blog_entry)

        return redirect('/blog')
    
    return render_template('add_new_post.html')
    

@app.route('/blog')  #displays all blog posts
def blogs():
    return render_template('main_blog_page.html', posts=posts)

#@app.route('/newpost', ['POST'])

if __name__ == '__main__':
    app.run()
