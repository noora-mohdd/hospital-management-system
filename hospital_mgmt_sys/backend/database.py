from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

def init_db(app):

    db.init_app(app)

    with app.app_context():
        from backend.models import Patient, Department

        db.create_all() #create tables if not exist

        #admin creation
        admin=Patient.query.filter_by(username="admin").first()

        if not admin:
            admin=Patient(
                full_name="Admin",
                username="admin",
                email="admin@hospital.com",
                password="54321",
                age=0,
                is_admin=True,
                is_blacklisted=False
            )
            db.session.add(admin)
            db.session.commit()
            print("admin created")

        if Department.query.count()==0:
            dept_name=[
                ("cardiology", "heart related treatments"),
                ("oncology", "cancer and tumor specialization"),
                ("general", "general medicine and checkup")
            ]
            for name, desc in dept_name:
                db.session.add(Department(name=name, description=desc))
            db.session.commit()
            print("depts added")

        print("database initialized successfully")