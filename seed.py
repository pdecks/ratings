"""Utility file to seed ratings database from MovieLens data in seed_data/"""


from model import User, Movie, Rating
# from model import Rating
# from model import Movie

from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        # not all of this data is stored in database
        user_id, age, gender, occupation, zipcode = row.split("|")

        # when do we add email and pw?
        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""
    from datetime import datetime

    print "Movies"

    Movie.query.delete()

    for row in open("seed_data/u.item"):
        row = row.rstrip()
        movie_entry = row.split("|")
        movie_id = movie_entry[0]
        movie_title = movie_entry[1] #TODO: need a way to remove YEAR 
        print movie_title
        # remove year frome title formated as "Title Name (YYYY)"
        # look up index of (, take title from [0:index-1]
        paren_index = movie_title.find('(')
        if paren_index != -1:
            # slice off the year and proceeding single space
            movie_title = movie_title[:(paren_index-1)]
            
        release_date = movie_entry[2]
        
        # else: # no year in title
        #     release_date = None
        
        #parse string into datetime object
        if release_date:
            rel_date_obj = datetime.strptime(release_date, '%d-%b-%Y')
        else:
            rel_date_obj = None

        imdb_url = movie_entry[3]

        movie = Movie(movie_id=movie_id,
                      movie_title=movie_title, 
                      release_date=rel_date_obj,
                      imdb_url=imdb_url)

        db.session.add(movie)

    db.session.commit()



def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    Rating.query.delete()

    for row in open("seed_data/u.data"):
        row = row.rstrip()
        # rating_entry = row.split('\t')
        user_id, movie_id, score, epoch_time = row.split('\t')

        rating = Rating(user_id=user_id,
                        movie_id=movie_id,
                        score=score)

        db.session.add(rating)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
