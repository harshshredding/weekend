from flask import Flask, render_template, request
import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    mongo_uri = os.getenv("MONGO_DB_URI")
    db_client = MongoClient(mongo_uri)
    app.db = db_client.weekend

    @app.route("/create",  methods=['GET','POST'])
    def create_interest():
        if request.method == 'POST':
            interest_data = request.form.get("interest_input")
            if interest_data is not None:
                date = datetime.datetime.today()
                formatted_date = date.strftime("%Y-%m-%d")
                app.db.interests.insert_one({"text": interest_data, "date": formatted_date})
            else:
                return {"message": "could not find data"}, 401
        all_interests = [interest for interest in app.db.interests.find({})]
        return render_template("create.html", interest_list=all_interests)

    @app.route("/hello")
    def hello():
        return render_template("hello.html")

    return app
