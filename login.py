from flask import redirect, url_for, request, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from wtforms import PasswordField
from flask_admin.contrib.sqla import ModelView
from passlib.hash import argon2
from main import app
import os

app.config["SECRET_KEY"] = "fiksjudge"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///teams.db"

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


# -------------------
# DATABASE MODEL
# -------------------

class Team(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    # virtuální pole jen pro admina
    _password = None

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = plaintext
        self.password_hash = argon2.hash(plaintext)


@login_manager.user_loader
def load_user(user_id):
    return Team.query.get(int(user_id))


# -------------------
# ADMIN PANEL
# -------------------

class AdminModelView(ModelView):
    column_exclude_list = ['password_hash']  # nechceme zobrazovat hash
    form_excluded_columns = ['password_hash']

    form_extra_fields = {
        'password': PasswordField('Password')
    }

    def on_model_change(self, form, model, is_created):
        """Při uložení modelu hashuj heslo pokud admin něco zadal"""
        if form.password.data:
            model.password = form.password.data
        if form.name.data and is_created and not form.is_admin.data:
            os.mkdir("./uploads/" + form.name.data)

    def on_model_delete(self, model):
        os.rename("./uploads/" + model.name, "./deleted/" + model.name)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login"))

# -------------------
# LOGIN
# -------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        team = Team.query.filter_by(name=name).first()

        if team and argon2.verify(password, team.password_hash):
            login_user(team)
            if(team.is_admin):
                return redirect("/admin")
            else:
                return redirect("/home")

    return render_template_string("""
    <h2>Login</h2>
    <form method="post">
        Team name:<br>
        <input name="name"><br>
        Password:<br>
        <input name="password" type="password"><br><br>
        <button type="submit">Login</button>
    </form>
    """)

def init_db():
    with app.app_context():
        db.create_all()

        if not Team.query.filter_by(name="admin").first():
            admin = Team(
                name="admin",
                password_hash = argon2.hash("fiksjudge"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

# -------------------
# LOGOUT
# -------------------

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect("/login")

def init_admin():
        # vytvoření admin panelu
    admin = Admin(app, name="Admin Panel", url='/admin')
    admin.add_view(AdminModelView(Team, db.session))


