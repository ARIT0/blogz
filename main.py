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
    body = db.Column(db.Text())

    def __init__(self, title, body):
        self.title = title
        self.body = body



@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

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
            new_post = Blog(entry_title, blog_entry)
            db.session.add(new_post)
            db.session.commit()

            #blog_id = new_post.id
            #blog = Blog.query.filter_by(id = blog_id).first()

            return redirect('/blog')
    
    return render_template('add_new_post.html')
    

@app.route('/blog')  #displays all blog posts
def blog():
    blog = Blog.query.all()

    return render_template('main_blog_page.html', blog=blog)


@app.route('/')
def index():
    return redirect('/newpost')


if __name__ == '__main__':
    app.run()
