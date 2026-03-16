from main import app, ALLOWED_EXTENSIONS, LOG_FOLDER, redirect
from flask import render_template, request, send_from_directory, abort
from flask_login import login_required, current_user
import os
import datetime

def allowed_file(filename):
    return "." in filename and filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS

def get_biggest_number_in_dir(dir_name):
    pass


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    message = None
    if request.method == "POST":
        file = request.files["botfile"]

        if file.filename != "":
            #TODO upload to team folder
            #TODO rename filename to biggest numer +1 in folder
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            message="✅ Soubor byl úspěšně nahrán!"
    return render_template("upload.html", message=message, team=current_user.name)


@app.route("/logs")
def logs():
    log_files = []
    for file in os.listdir(LOG_FOLDER):
        path = os.path.join(LOG_FOLDER, file)

        if os.path.isfile(path):
            size = os.path.getsize(path) / 1024
            modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(path)
            ).strftime("%Y-%m-%d %H:%M:%S")

            log_files.append({
                "name": file,
                "size": f"{size:.2f} KiB",
                "modified": modified
            })

    return render_template("logs.html", files=log_files)


@app.route("/download-log/<filename>")
def download_log(filename):
    return send_from_directory(LOG_FOLDER, filename, as_attachment=True)


@app.route("/view-log/<filename>")
def view_log(filename):
    path = os.path.join(LOG_FOLDER, filename)

    if not os.path.isfile(path):
        abort(404)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    return render_template("view_log.html", filename=filename, content=content, team=current_user.name)

@app.route("/custome_match")
@login_required
def custome_match():
    return render_template("custome_match.html", team=current_user.name)

@app.route("/docs")
def docs():
    return render_template("docs.html")
