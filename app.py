from flask import Flask, flash, json, jsonify, redirect, render_template, request, abort, session, url_for
import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from werkzeug.user_agent import UserAgent
from gpt.recommendation import get_recommendation
from gpt.util import get_reply, get_reply_multiple_messages

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
            flash("Unauthorized")
            return redirect(url_for('login'))

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


    @app.route("/get-recommendation/")
    def create_recommendation():
        username = is_logged_in()
        if not username: 
            flash("Unauthorized")
            return redirect(url_for('login')) 
        return render_template("get_recommendation.html")  

    @app.route("/show-recommendation/", methods=['POST'])
    def show_recommendation():
        username = is_logged_in()
        if not username: 
            flash("Unauthorized")
            return redirect(url_for('login'))

        city = request.form["city"]
        additional = request.form["additional-info"]

        all_interests = get_all_interests(username) 
        all_interests = [interest['text'] for interest in all_interests]

        recommendation = get_recommendation(all_interests, city=city, additional=additional)
        recommendation = recommendation.strip()
        return render_template("show_recommendation.html", recommendation=recommendation)

    @app.route("/about")
    def info(): 
        return render_template("about.html")

    @app.route("/profile")
    def profile():
        username = is_logged_in()
        if not username: 
            flash("Unauthorized")
            return redirect(url_for('login'))
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
    
    @app.route('/chat', methods=['POST'])
    def chat():
        if request.is_json:
            data: dict = request.json
            if "query" in data:
                chat_gpt_query = data["query"]
                chatgpt_reply = get_reply(query=chat_gpt_query)
                return jsonify({"reply": chatgpt_reply}), 200
            else:
                return jsonify({"error", "JSON doesn't have message"}), 400
        else:
            return jsonify({"error", "Invalid JSON"}), 400


    def check_chat_messages(messages: list[dict]):
        print(messages)
        assert len(messages)%2 == 1
        for i, message in enumerate(messages):
            if (i%2) == 0:
                assert message["type"] == "request"
            else:
                assert message["type"] == "response"


    @app.route('/chat-multiple-messages', methods=['POST'])
    def chat_multiple_messages():
        if request.is_json:
            messages: list[dict] = request.json
            check_chat_messages(messages)
            chatgpt_reply = get_reply_multiple_messages(messages=messages)
            return jsonify({"reply": chatgpt_reply}), 200
        else:
            return jsonify({"error", "Invalid JSON"}), 400

    return app
