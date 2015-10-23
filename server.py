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
    movie = Movie.query.get(movie_id)
    
    user_id = session.get("user_id")

    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    # Get average rating of movie

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    # Prediction code: only predict if the user hasn't rated it.

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)


    # query for movie's ratings, return list of tuples [(user.email, ratings.score), ...]
    # add user_id
    QUERY = """
            SELECT Users.email, Users.user_id, Ratings.score
            FROM Ratings 
            JOIN Movies ON Movies.movie_id = Ratings.movie_id 
            JOIN Users ON Users.user_id = Ratings.user_id 
            WHERE Movies.movie_id = :movie_id
            ORDER BY Users.user_id;
            """
    cursor = db.session.execute(QUERY, {'movie_id': movie_id})
    ratings = cursor.fetchall()
    
    # movies = Movie.query.order_by(Movie.movie_title).all()
    # return render_template("movie-details.html", movie=movie, ratings=ratings) 


    return render_template(
        "movie-details.html",
        movie=movie,
        user_rating=user_rating,
        average=avg_rating,
        prediction=prediction,
        ratings=ratings
        )


@app.route('/movies/add-rating', methods=['POST'])
def update_movie_rating():
    # this route is only accessed by a logged-in user

    # get the movie_id (hidden submit)
    movie_id = int(request.form.get('movie-id'))
    # print "This is movie_id at line 62: %s" % movie_id #ok
    # get user's rating
    user_rating = request.form.get('user-rating')
    # print "This is user_rating at line 65: %s" % user_rating #ok

    user_id = session['user_id']
    # print "this is user_id at line 68: %s" % user_id #ok

    # query Rating to see if user has already rated
    # if rating = None, add rating to database
    rating = Rating.query.filter(Rating.user_id == user_id, Rating.movie_id == movie_id).first() ### SOMETHING IS GOING WRONG HERE ... 
    # print "rating: %s" % rating
    
    if rating == None:
        # add value in ratings database
        rating = Rating(movie_id=movie_id, user_id=user_id, score=user_rating)
        print "This is rating: movie_id %s user_id %s score %s" % (rating.movie_id, rating.user_id, rating.score)
        db.session.add(rating)
        db.session.commit()
        flash("Your rating has been sucessfully added!")
    else: # update rating
        QUERY = """
        UPDATE Ratings
        SET score=:score
        WHERE user_id=:user_id AND movie_id=:movie_id;
        """
        cursor = db.session.execute(QUERY, {'user_id': user_id, 'movie_id': movie_id, 'score': user_rating})
        db.session.commit()
        flash("Your rating has been sucessfully updated!")

    return redirect("/movies/" + str(movie_id))


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
    
    # if user = None, add user to database
    user = User.query.filter(User.email == username).first()
    # print "This is user after line 74: %s" % user
    if user == None:
        age = ''
        zipcode = ''
        user = User(email=username, password=password, age=age, zipcode=zipcode)
        # print "This is user after line 79: %s" % user
        db.session.add(user)
        db.session.commit()

        # User.query.filter(User.email == username)
        user = User.query.filter(User.email == username).all()
        # user = user[0]
        # print "This is the user after line 85: %s" % user
        # print "This is password: %s" % password
        # print "This is user.password: %s" % user.password

        # # TODO: ways to get fancy: add modal window, registration page, etc.

    # user exists, check pw
    # log in user if password matches user pw
    if user.password == password:
        # add user id to session
        session['user_id'] = user.user_id
        # create flash message 'logged in'
        flash("Login successful.")
        print "I made it to line 99"
    else:
        # display alert for incorrect login information
        flash("Incorrect login information. Please try again.")
        # good place to use AJAX in the future!
        return redirect('/login-form')  
        
    # redirect to homepage
    # return redirect('/users/<user_id>')
    return redirect('/users/'+str(user.user_id))

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
    
    # TODO: Allow user to edit information on profile page if logged in
    
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