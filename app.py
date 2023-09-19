from flask import Flask, flash, redirect, render_template, request, abort, session, url_for
import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from werkzeug.user_agent import UserAgent
from gpt.recommendation import get_recommendation

load_dotenv()

def create_app():
    app = Flask(__name__)    

    mongo_uri = os.getenv("MONGO_DB_URI")
    db_client = MongoClient(mongo_uri)
    app.db = db_client.weekend
    app.secret_key = "thisisasecretx"

    def is_logged_in():
        return session.get('username')

    def get_all_interests(username):
        all_interests = list(app.db.interests.find({'user':username}))
        return all_interests


    @app.route("/create",  methods=['GET','POST'])
    def create_interest():
        username = is_logged_in()
        if not username:
           return render_template("unauthorized.html") 

        if request.method == 'POST':
            interest_data = request.form.get("interest_input")
            if interest_data is not None:
                date = datetime.datetime.today()
                formatted_date = date.strftime("%Y-%m-%d")
                app.db.interests.insert_one({"text": interest_data, "date": formatted_date, "user": username})
            else:
                return {"message": "could not find data"}, 401
        all_interests = get_all_interests(username) 
        return render_template("create.html", interest_list=all_interests)

    @app.route("/")
    def recommend():
        username = is_logged_in()
        if not username:
           return render_template("unauthorized.html") 

        all_interests = get_all_interests(username) 
        all_interests = [interest['text'] for interest in all_interests]
        recommendation = get_recommendation(all_interests)
        recommendation = recommendation.strip()
        return render_template("recommend.html", recommendation=recommendation)

    @app.route("/about")
    def info(): 
        return render_template("about.html")

    @app.route("/profile")
    def profile():
        username = is_logged_in()
        if not username:
           return render_template("unauthorized.html") 
        return render_template("profile.html", username=username)


    @app.route("/register", methods=['GET','POST'])
    def sign_up():
        user_already_exists = False
        if request.method == 'POST':
            username = request.form["username"] 
            all_usernames = [user["username"] for user in app.db.users.find({})]
            if username in all_usernames:
                user_already_exists = True
            else:
                app.db.users.insert_one({"username": username})
                flash("You are successfully signed up.")
                return redirect(url_for("info"))
        return render_template("sign_up.html", user_already_exists=user_already_exists)


    @app.route("/login", methods=['GET','POST'])
    def login():
        user_not_found = False
        if request.method == 'POST':
            username = request.form["username"] 
            all_usernames = [user["username"] for user in app.db.users.find({})]
            if username in all_usernames:
                session["username"] = username
                flash("You are successfully logged in.")
                return redirect(url_for("create_interest"))
            else:
                user_not_found = True
        return render_template("login.html", user_not_found=user_not_found)

    @app.route('/logout')
    def logout():
        # Clear the session
        session.clear() 
        # Redirect to another page, maybe the homepage or the login page
        flash("Log out successful!")
        return redirect(url_for('login'))

    return app
