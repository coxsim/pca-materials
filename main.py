__author__ = 'simon'

import os
import sys
import markdown
from flask import Flask
from flask import render_template
from flask import Markup

app = Flask(__name__)
app.debug = True

script_dir = os.path.dirname(sys.argv[0])
markdown_dir = os.path.join(script_dir, "markdown")

@app.route("/")
def index():
    return render_template("index.html")

def markdown_page(markdown_file, title):
    with open(os.path.join(markdown_dir, markdown_file)) as f:
        content = Markup(markdown.markdown(f.read()))

    return render_template("markdown.html", title=title, content=content)

@app.route("/news-and-bio")
def news_and_bio():
    return markdown_page("news_bio.md", "News & Bio")

@app.route("/multilayer-polymer-constructs")
def multilayer_polymer_constructs():
    return markdown_page("multipc.md", "Multilayer Polymer Constructs")

@app.route("/multilayer-dies")
def multilayer_dies():
    return markdown_page("multidd.md", "Multilayer Dieheads")

@app.route("/monolayer-dies")
def monolayer_dies():
    return markdown_page("monodd.md", "Monolayer Dieheads")

@app.route("/commissioning")
def commissioning():
    return markdown_page("commission.md", "Commissioning")

@app.route("/expert-witness")
def expert_witness():
    return markdown_page("expert_witness.md", "Expert Witness")

@app.route("/contact")
def contact():
    return markdown_page("contact.md", "Contact Details")

if __name__ == "__main__":
    app.run()