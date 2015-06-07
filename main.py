__author__ = 'simon'

import os
import sys
import markdown
import logging
from flask import Flask
from flask import render_template
from flask import Markup
from flask import request
from flask import session
from flask import redirect
from flask.helpers import url_for

app = Flask(__name__)
app.secret_key = "12345"  # for session cookies
app.debug = True


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


script_dir = os.path.dirname(sys.argv[0])
markdown_dir = os.path.join(script_dir, "markdown")

import datetime

TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


class DocumentStore(object):
    def __init__(self, directory):
        self.directory = directory

    def save(self, key, value):

        key_history_dir = os.path.join(self.directory, "history", key)

        if not os.path.isdir(key_history_dir):
            os.mkdir(key_history_dir)

        with open(os.path.join(key_history_dir, datetime.datetime.now().strftime(TIMESTAMP_FORMAT)), "w") as f:
            f.write(value)
        with open(os.path.join(self.directory, key), "w") as f:
            f.write(value)

    def list_history(self, key):
        key_history_dir = os.path.join(self.directory, "history", key)
        if not os.path.isdir(key_history_dir):
            raise StopIteration()

        for filename in os.listdir(key_history_dir):
            yield (filename, datetime.datetime.strptime(filename, TIMESTAMP_FORMAT))

    def get_history(self, key, history_key):
        filename = os.path.join(self.directory, "history", key, history_key)
        save_time = datetime.datetime.strptime(history_key, TIMESTAMP_FORMAT)

        with open(filename, "r") as f:
            return (save_time, f.read())


markdown_store = DocumentStore(markdown_dir)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.form:
        username = request.form["username"]
        session["username"] = username
        session["is_admin"] = is_admin(username)
        message = "Logged in as %s" % username
    else:
        message = None

    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    del session["username"]
    del session["is_admin"]
    message = "Logged out"

    return render_template("login.html", message=message)


def is_admin(user):
    return user == "coxsim"


def markdown_page(markdown_file, title):
    edit = request.args.get('edit')

    if edit:
        return redirect(url_for("edit", markdown_file=markdown_file))

    with open(os.path.join(markdown_dir, markdown_file)) as f:
        markdown_content = f.read()

    content = Markup(markdown.markdown(markdown_content))

    return render_template("markdown.html",
                           title=title,
                           content=content,
                           markdown_file=markdown_file,
                           markdown_content=markdown_content,
                           edit=edit,
                           history=None,
                           drafts=None)


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


@app.route("/markdown/<markdown_file>", methods=['GET'])
def edit(markdown_file):
    with open(os.path.join(markdown_dir, markdown_file)) as f:
        markdown_content = f.read()

    history = markdown_store.list_history(markdown_file)
    drafts = markdown_store.list_history("%s.draft" % markdown_file)

    return render_template("markdown.html",
                           title="Edit %s" % markdown_file,
                           content=None,
                           markdown_file=markdown_file,
                           markdown_content=markdown_content,
                           edit=True,
                           history=history,
                           drafts=drafts)


@app.route("/markdown/<markdown_file>", methods=['POST'])
def save(markdown_file):
    markdown_content = request.form["markdown_content"]
    markdown_store.save(markdown_file, markdown_content)
    return redirect(url_for("edit", markdown_file=markdown_file))


@app.route("/markdown/<markdown_file>/draft", methods=['POST'])
def save_draft(markdown_file):
    markdown_content = request.form["markdown_content"]
    markdown_store.save("%s.draft" % markdown_file, markdown_content)
    return ""


@app.route("/markdown/<markdown_file>/<history_key>")
def markdown_history(markdown_file, history_key):
    (save_time, markdown_content) = markdown_store.get_history(markdown_file, history_key)
    history = markdown_store.list_history(markdown_file)
    drafts = markdown_store.list_history("%s.draft" % markdown_file)

    return render_template("markdown.html",
                           title="%s - saved - %s" % (markdown_file, save_time),
                           content=None,
                           markdown_file=markdown_file,
                           markdown_content=markdown_content,
                           edit=True,
                           history=history,
                           drafts=drafts)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
