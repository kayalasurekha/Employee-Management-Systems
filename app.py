from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from config import Config
from models import db, Employee

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.secret_key = "employee_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Temporary User
class User(UserMixin):
    def __init__(self, username):
        self.id = username


users = {
    "admin": {
        "password": "admin123"
    }
}


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            login_user(User(username))
            return redirect(url_for("home"))

        return "Invalid Username or Password"

    return render_template("login.html")


# Home
@app.route("/")
@login_required
def home():
    employees = Employee.query.all()
    return render_template("index.html", employees=employees)


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Add Employee
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_employee():
    if request.method == "POST":
        employee = Employee(
            name=request.form["name"],
            email=request.form["email"],
            department=request.form["department"],
            salary=float(request.form["salary"])
        )

        db.session.add(employee)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add_employee.html")


# Edit Employee
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)

    if request.method == "POST":
        employee.name = request.form["name"]
        employee.email = request.form["email"]
        employee.department = request.form["department"]
        employee.salary = float(request.form["salary"])

        db.session.commit()

        return redirect(url_for("home"))

    return render_template("edit_employee.html", employee=employee)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
