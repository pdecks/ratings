"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')
    # "<html><body>Placeholder for the homepage.</body></html>"

@app.route('/movies')
def movies():
    """Movies page."""

    movies = Movie.query.order_by(Movie.movie_title).all()
    return render_template("movies.html", movies=movies) 


@app.route('/movies/<int:movie_id>')
def show_movie_details(movie_id):
    """Displays details for individual movie."""
    # use movie_id to query movie object
    movie = Movie.query.filter(Movie.movie_id == movie_id).one()
    
    # query for movie's ratings, return list of tuples [(user.email, ratings.score), ...]
    # add user_id
    QUERY = """
            SELECT Users.email, Users.user_id, Ratings.score
            FROM Ratings 
            JOIN Movies ON Movies.movie_id = Ratings.movie_id 
            JOIN Users ON Users.user_id = Ratings.user_id 
            WHERE Movies.movie_id = :movie_id;
            """
    cursor = db.session.execute(QUERY, {'movie_id': movie_id})
    ratings = cursor.fetchall()
    
    # movies = Movie.query.order_by(Movie.movie_title).all()
    return render_template("movie-details.html", movie=movie, ratings=ratings) 

@app.route('/users')
def users():
    """Show list of users."""

    users = User.query.all()
    return render_template("user-list.html", users=users)

@app.route('/login-form')
def show_login_form():
    return render_template("sign-in.html")

@app.route('/login-process')
def process_login():
    username = request.args.get('username')
    password = request.args.get('password')
    # query for username in database
    user = User.query.filter(User.email == username).one()
    print "this is user: %s" % user
    # log in user if password matches user pw
    if user.password == password:
        # add user id to session
        session['user_id'] = user.user_id
        # create flash message 'logged in'
        flash("Login successful.")
    else:
        # display alert for incorrect login information
        flash("Incorrect login information. Please try again.")
        # good place to use AJAX in the future!
        return redirect('/login-form')  
        
    # redirect to homepage
    return redirect('/users/<user_id>')

@app.route('/users/<user_id>')
def show_user_page(user_id):
    # user_id = session['user_id']
    # user_id = user_id #pdecks@me.com
    QUERY = """
            SELECT Movies.movie_title, Ratings.score 
            FROM Ratings 
            JOIN Movies ON Movies.movie_id = Ratings.movie_id 
            JOIN Users ON Users.user_id = Ratings.user_id 
            WHERE Users.user_id = :user_id;
            """
    cursor = db.session.execute(QUERY, {'user_id': user_id})
    movies = cursor.fetchall()
    user = User.query.filter(User.user_id == user_id).one()
    # query database to return a LIST of MOVIES user rated and score for each rating
    # user_ratings = Rating.query.filter(User.user_id == 944).all()
    # print "This is user_ratings:"
    # print user_ratings
    # for rating in user_ratings:
    #     print rating
    # user_movies_rated = user_ratings.movie
    # movies = user_movies_rated.all()
    # for movie in movies:
    #     print movie.movie_title
    # movies=[{'movie_title': 'Batman', 'score': 5}]
    
    return render_template('user.html', user=user, movies=movies)




@app.route('/logout')
def process_logout():
    # remove user id from the session
    del session['user_id']

    # create flash message "logged out"
    flash("Successfully logged out.")
    
    # redirect to homepage
    return redirect('/')


# @app.route('/users/<int:user-id>')
# def show_user():
#     return

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()