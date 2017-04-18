from collections import namedtuple

__author__ = 'simon'

import os
import sys
import markdown
import logging
import hashlib

from flask import Flask
from flask import render_template
from flask import Markup
from flask import request
from flask import session
from flask import redirect
from flask import jsonify
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
users_file = os.path.join(script_dir, "users.csv")

import datetime

TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


class DocumentStore(object):
    def __init__(self, directory):
        self.directory = directory

    def save(self, key, value):

        key_history_dir = os.path.join(self.directory, "history", key)

        if not os.path.isdir(key_history_dir):
            os.makedirs(key_history_dir)

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


from csv import DictReader, DictWriter

User = namedtuple("User", "username,password,is_admin")

class UserStore(object):

    def __init__(self, filename):
        with open(filename, "r") as f:
            users = DictReader(f)
            self.users = {r["username"] : User(r["username"], r["password"], r["is_admin"] == "True") for r in users}

    def get(self, k, d=None):
        return self.users.get(k, d)

    def __getitem__(self, item):
        return self.users[item]



markdown_store = DocumentStore(markdown_dir)
user_store = UserStore(users_file)

@app.route("/")
def index():

    sections = [["news-and-bio", "expert-witness", "commissioning"],
                ["multilayer-polymer-constructs", "multilayer-dies", "monolayer-dies"]]

    section_contents = map(lambda row: map(lambda section: (section, __fetch_markdown_content("%s-summary" % section)), row), sections)

    return render_template("index.html", section_contents=section_contents)


@app.route("/login", methods=['GET'])
def login():
    return render_template("login.html", message_level=None, message=None)


@app.route("/login", methods=['POST'])
def login_post():
    username = request.form["username"]

    user = user_store.get(username)

    m = hashlib.md5()
    m.update(user.password)
    digest = m.hexdigest()

    if user and digest == request.form["password_md5"]:
        session["username"] = user.username
        session["is_admin"] = user.is_admin

        message = "Logged in as %s" % username
        message_level = "success"
    else:
        del session["username"]
        del session["is_admin"]

        message = "Invalid login/password"
        message_level = "error"

    return jsonify(message_level=message_level, message=message)

@app.route("/logout")
def logout():
    del session["username"]
    del session["is_admin"]
    message = "Logged out"

    return render_template("login.html", message=message)


def is_admin(user):
    return user == "coxsim"

def __fetch_markdown_content(markdown_file):
    with open(os.path.join(markdown_dir, "%s.md" % markdown_file)) as f:
        markdown_content = f.read()

    return Markup(markdown.markdown(markdown_content))

def markdown_page(markdown_file, title):
    content = __fetch_markdown_content(markdown_file)

    return render_template("markdown_render.html",
                           title=title,
                           content=content,
                           markdown_file=markdown_file,
                           edit=False,
                           history=None,
                           drafts=None)


@app.route("/news-and-bio")
def news_and_bio():
    return markdown_page("news-and-bio", "News & Bio")


@app.route("/multilayer-polymer-constructs")
def multilayer_polymer_constructs():
    return markdown_page("multilayer-polymer-constructs", "Multilayer Polymer Constructs")


@app.route("/multilayer-dies")
def multilayer_dies():
    return markdown_page("multilayer-dies", "Multilayer Dieheads")


@app.route("/monolayer-dies")
def monolayer_dies():
    return markdown_page("monolayer-dies", "Monolayer Dieheads")


@app.route("/commissioning")
def commissioning():
    return markdown_page("commissioning", "Commissioning")


@app.route("/expert-witness")
def expert_witness():
    return markdown_page("expert-witness", "Expert Witness")


@app.route("/contact")
def contact():
    return markdown_page("contact", "Contact Details")


@app.route("/<markdown_file>/markdown", methods=['GET'])
def edit(markdown_file):
    with open(os.path.join(markdown_dir, "%s.md" % markdown_file)) as f:
        markdown_content = f.read()

    history = markdown_store.list_history("%s.md" % markdown_file)
    drafts = markdown_store.list_history("%s.draft.md" % markdown_file)

    return render_template("markdown_edit.html",
                           title="Edit %s" % markdown_file,
                           content=None,
                           markdown_file=markdown_file,
                           markdown_content=markdown_content,
                           edit=True,
                           history=history,
                           drafts=drafts)


@app.route("/<markdown_file>/markdown", methods=['POST'])
def save(markdown_file):
    markdown_content = request.form["markdown_content"]
    markdown_store.save("%s.md" % markdown_file, markdown_content)

    if markdown_file.endswith("-summary"):
        target = url_for("index")
    else:
        target = "/%s" % markdown_file

    return redirect(target)


@app.route("/<markdown_file>/markdown/draft", methods=['POST'])
def save_draft(markdown_file):
    markdown_content = request.form["markdown_content"]
    markdown_store.save("%s.draft.md" % markdown_file, markdown_content)
    return ""


@app.route("/<markdown_file>/markdown/<history_key>")
def markdown_history(markdown_file, history_key):
    return __markdown_history(markdown_file, history_key, draft=False)


@app.route("/<markdown_file>/markdown/draft/<history_key>")
def markdown_draft_history(markdown_file, history_key):
    return __markdown_history(markdown_file, history_key, draft=True)


@app.route("/<markdown_file>/markdown/draft/<history_key>")
def __markdown_history(markdown_file, history_key, draft):

    (save_time, markdown_content) = markdown_store.get_history("%s%s.md" % (markdown_file, ".draft" if draft else ""), history_key)
    history = markdown_store.list_history("%s.md" % markdown_file)
    drafts = markdown_store.list_history("%s.draft.md" % markdown_file)

    return render_template("markdown_edit.html",
                           title="%s - saved - %s" % (markdown_file, save_time),
                           content=None,
                           markdown_file=markdown_file,
                           markdown_content=markdown_content,
                           edit=True,
                           history=history,
                           drafts=drafts)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
