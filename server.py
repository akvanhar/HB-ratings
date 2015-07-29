"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/login')
def login():
    """Login page."""

    return render_template("login.html")

@app.route('/login_portal', methods=['POST'])
def login_portal():
    """place holder for successful login"""
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email, password=password).first()
    
    if user:
        user_id = user.user_id
        session['user_id']=user_id
        flash('Login successful!')
        return redirect('/users/'+ str(user_id))
    else:
        flash('Login NOT successful!')
        return redirect('/')
        #When we need to authenticate, we'll have to fix this
        #redirect to sign up page
        #have sign up page add user to database
        #then redirect back to login page

@app.route('/logbutton')
def logbutton():
    """You get here if you click the login/logout button from any page other than login"""
    if 'user_id' in session:
        del session['user_id']
        flash("Logout successful!") 
    return redirect("/login")


@app.route('/users')
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<int:user_id>')
def user_info(user_id):
    """Display information about a specific user"""

    user_info = User.query.filter_by(user_id=user_id).one()
    rating_list = sorted(user_info.ratings) #sorting by memory space! fun!
    return render_template("user_info.html", user_info=user_info, rating_list=rating_list)

@app.route('/movies')
def movies():
    """A list of all the movies"""

    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()