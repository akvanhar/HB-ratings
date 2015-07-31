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

@app.route('/logbutton')
def logbutton():
    """You get here if you click the login/logout button from any page other than login"""
    if 'user_id' in session:
        del session['user_id']
        flash("Logout successful!") 
    return redirect("/login")

@app.route('/signup')
def signup():
    """Allow a user to sign up and add them to the database"""
    return render_template('signup.html')

@app.route('/signup_portal', methods=['POST'])
def signup_portal():
    """Create new user and add the user to the database"""
    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')


    User.add_user(email, password, age, zipcode)

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

@app.route('/movies/<int:movie_id>')
def movie_info(movie_id):
    """Display information about a specific movie"""

    BERATEMENT_MESSAGES = [
        "Yeah. I suppose you're taste isn't so bad. I guess. Blah.",
        "What were you thinking?? That's how you rated it? Seriously??!",
        "Good grief! You have awful taste in moves.",
        "That movie is great. For a clown to watch. Idiot.",
        "Barf."
        ]

    movie_info = Movie.query.get(movie_id)
    rating_list = movie_info.ratings
    user_id = session.get('user_id')

    if user_id:
        user_rating = Rating.query.filter_by(
                        movie_id=movie_id, user_id=user_id).first()
    else:
        user_rating = None


    #Get average rating of movie

    rating_scores = [r.score for r in rating_list]
    avg_rating = float(sum(rating_scores)/len(rating_scores))

    prediction = None

    #Prediciton code: only if the user hasn't rated it yet and a user is logged in
    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie_info)

    if prediction:
        #User hasn't scored; use our prediction if we made one
        effective_rating = prediction
    elif user_rating:
        #User has already scored for real; use that rating
        effective_rating = user_rating.score
    else:
        #User hasn't scored, we couldn't get a prediction
        effective_rating = None

    #Get the eye's rating, either by prediction or using real rating
    the_eye = User.query.get(946)
    eye_rating = Rating.query.filter_by(
                                        user_id=the_eye.user_id,
                                        movie_id=movie_info.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie_info)

    else:
        eye_rating = eye_rating.score

    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)
    else:
        #Can't get an eye rating. We skip difference.
        difference = None

    if difference is not None:
        beratement = BERATEMENT_MESSAGES[int(difference)]
    else:
        beratement = "You get a pass. This time."
   
    return render_template("movie_info.html", 
                            movie_info=movie_info, 
                            rating_list=rating_list,
                            average=avg_rating,
                            prediction=prediction,
                            beratement=beratement)

@app.route('/rate_movie/<int:movie_id>', methods=['POST'])
def rating_info(movie_id):
    """Update or insert user rating into db and reload the movie info page"""

    score = request.form.get("score")
    user_id = session['user_id']
    
    rating_exists = Rating.query.filter_by(user_id = user_id,
                                           movie_id = movie_id).first()

    #if the rating exists, update, otherwise add it to the database.
    if rating_exists:
        rating_exists.update_rating(movie_id, user_id, score)
    else:
        Rating.add_rating(movie_id, user_id, score)

    return redirect('/movies/' + str(movie_id))



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = False

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()