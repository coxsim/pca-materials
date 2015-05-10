__author__ = 'simon'

import os
import sys
import markdown
import logging
from flask import Flask
from flask import render_template
from flask import Markup
from flask import request

app = Flask(__name__)
app.debug = True


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

script_dir = os.path.dirname(sys.argv[0])
markdown_dir = os.path.join(script_dir, "markdown")

@app.route("/")
def index():
    return render_template("index.html")

def markdown_page(markdown_file, title):
    with open(os.path.join(markdown_dir, markdown_file)) as f:
        markdown_content = f.read()

    content = Markup(markdown.markdown(markdown_content))

    edit = request.args.get('edit')

    return render_template("markdown.html",
                           title=title,
                           content=content,
                           markdown_file=markdown_file,
                           markdown_content=markdown_content,
                           edit=edit)

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

@app.route("/save-draft", methods=['POST'])
def save_draft():
    markdown_file = request.form["markdown_file"]
    markdown_content = request.form["markdown_content"]
    #request.form['foo']
    app.logger.info(markdown_file)
    app.logger.info(markdown_content)

    return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0")
