from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from config import Config
from models import db, Employee, User

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "employee_secret_key"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    employees = Employee.query.all()
    return render_template("index.html", employees=employees)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_employee():

    if current_user.role != "admin":
        return "Access Denied", 403

    if request.method == "POST":
        employee = Employee(
            name=request.form["name"],
            email=request.form["email"],
            department=request.form["department"],
            position=request.form["position"],
            salary=float(request.form["salary"])
        )

        db.session.add(employee)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add_employee.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_employee(id):

    if current_user.role != "admin":
        return "Access Denied", 403

    employee = Employee.query.get_or_404(id)

    if request.method == "POST":
        employee.name = request.form["name"]
        employee.email = request.form["email"]
        employee.department = request.form["department"]
        employee.position = request.form["position"]
        employee.salary = float(request.form["salary"])

        db.session.commit()

        return redirect(url_for("home"))

    return render_template("edit_employee.html", employee=employee)


@app.route("/delete/<int:id>")
@login_required
def delete_employee(id):

    if current_user.role != "admin":
        return "Access Denied", 403

    employee = Employee.query.get_or_404(id)

    db.session.delete(employee)
    db.session.commit()

    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
