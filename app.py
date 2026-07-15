from flask import Flask, render_template, request, redirect
from config import Config
from models import db, Employee

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():
    employees = Employee.query.all()
    return render_template("index.html", employees=employees)


@app.route("/add", methods=["GET", "POST"])
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

        return redirect("/")

    return render_template("add_employee.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)

    if request.method == "POST":
        employee.name = request.form["name"]
        employee.email = request.form["email"]
        employee.department = request.form["department"]
        employee.salary = float(request.form["salary"])

        db.session.commit()

        return redirect("/")

    return render_template("edit_employee.html", employee=employee)


@app.route("/delete/<int:id>")
def delete_employee(id):
    employee = Employee.query.get_or_404(id)

    db.session.delete(employee)
    db.session.commit()

    return redirect("/")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
