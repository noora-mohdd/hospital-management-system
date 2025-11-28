from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

def init_db(app):

    with app.app_context():
        from backend.models import Patient

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

        print("database initialized successfully")