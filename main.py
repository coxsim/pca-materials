__author__ = 'simon'

from flask import Flask
from flask import render_template


app = Flask(__name__)
app.debug = True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/news-and-bio")
def news_and_bio():
    return render_template("news_bio.html")

@app.route("/multilayer-polymer-constructs")
def multilayer_polymer_constructs():
    return render_template("multipc.html")

@app.route("/multilayer-dies")
def multilayer_dies():
    return render_template("multipc.html")

@app.route("/monolayer-dies")
def monolayer_dies():
    return render_template("multipc.html")

@app.route("/commissioning")
def commissioning():
    return render_template("commissioning.html")

@app.route("/expert-witness")
def expert_witness():
    return render_template("expert_witness.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run()