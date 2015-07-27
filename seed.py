"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""
    user_file = open('seed_data/u.user')
    for line in user_file:
        user_id, email, password, age, zipcode = line.split("|")
        the_user = User(user_id=user_id, email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(the_user)
        db.session.commit()


def load_movies():
    """Load movies from u.item into database."""
    movie_file = open('seed_data/u.item')
    for line in movie_file:
        movie_info = line.split("|")
        movie_id = line[0]
        title = line[1][:-6].strip("")
        #now we need to figure out Python datetime
        imdb_url = line[3]



def load_ratings():
    """Load ratings from u.data into database."""
    

if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_movies()
    # load_ratings()
