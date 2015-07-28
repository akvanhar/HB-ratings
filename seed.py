"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app
from datetime import datetime


def load_users():
    """Load users from u.user into database."""
    user_file = open('seed_data/u.user')
    for line in user_file:
        line = line.rstrip()
        user_id, age, gender, occupation, zipcode = line.split("|")
        the_user = User(user_id=user_id,  
                        age=age, 
                        zipcode=zipcode)
        db.session.add(the_user)
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""
    movie_file = open('seed_data/u.item')
    for line in movie_file:
        line = line.rstrip()
        movie_info = line.split("|")
        if movie_info[1] == "unknown":
            continue
        else:
            movie_id = movie_info[0]
            title = movie_info[1][:-6]
            title = title.decode("latin-1")
            title = title.rstrip()
            date = movie_info[2]
            released_at = datetime.strptime(date, "%d-%b-%Y")
            imdb_url = movie_info[4]
            the_movie = Movie(movie_id=movie_id, 
                              title=title, 
                              released_at=released_at, 
                              imdb_url=imdb_url)
            db.session.add(the_movie)
    db.session.commit()

def load_ratings():
    """Load ratings from u.data into database."""
    ratings_file = open('seed_data/u.data')
    for i, line in enumerate(ratings_file):
        line = line.rstrip()
        user_id, movie_id, score, timestamp = line.split("\t")
        the_rating = Rating(movie_id=movie_id, 
                            user_id=user_id, 
                            score=score)
        db.session.add(the_rating)

        if i % 1000 == 0:
            print i
            db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    # load_movies()
    # load_ratings()


# from datetime import datetime

# date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')