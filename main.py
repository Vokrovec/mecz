#!python3
#TODO vizualizace logu
#TODO databaze tymu (asi done)
#TODO build/runscripty

import os
from flask import Flask


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
LOG_FOLDER = "./mecz/logs"
RESULTS_DIR = "./mecz/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"py", "c", "cpp", "java"}


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

from router import *
from api_router import *
from login import *


if __name__ == "__main__":

    init_db()
    init_admin()
    app.run(debug=True)
