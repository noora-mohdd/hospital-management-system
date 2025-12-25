from backend.database import db


#patient table
class Patient(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    full_name=db.Column(db.String(100), nullable=False)
    username=db.Column(db.String(50), unique=True, nullable=False)
    email=db.Column(db.String(100), unique=True)
    password=db.Column(db.String(100), nullable=False)
    age=db.Column(db.Integer)
    is_blacklisted= db.Column(db.Boolean, default=False)
    is_admin= db.Column(db.Boolean, default=False)

    appointments=db.relationship("Appointment", backref="patient", lazy=True)

#doctors table
class Doctor(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    full_name=db.Column(db.String(100), nullable=False)
    username=db.Column(db.String(50), unique=True, nullable=False)
    email=db.Column(db.String(100), unique=True)
    password=db.Column(db.String(100), nullable=False)
    specialization=db.Column(db.String(100))
    experience=db.Column(db.Integer)
    is_blacklisted=db.Column(db.Boolean, default=False)

    appointments=db.relationship("Appointment", backref="doctor", lazy=True, cascase="all, delete")

#appointment table
class Appointment(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    patient_id=db.Column(db.Integer, db.ForeignKey("patient.id"))
    doctor_id=db.Column(db.Integer, db.ForeignKey("doctor.id"))
    date=db.Column(db.String(20))
    time=db.Column(db.String(20))
    status=db.Column(db.String(20))

    history=db.relationship("History", backref="appointment", uselist=False, cascase="all, delete")

#history/treatment table
class History(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    
    appointment_id=db.Column(db.Integer, db.ForeignKey("appointment.id"), unique=True, nullable=False)

    visit_type=db.Column(db.String(100))
    test_done=db.Column(db.String(100))
    diagnosis=db.Column(db.Text)
    prescription=db.Column(db.Text)
    medicine=db.Column(db.Text)

    

#availability table
class Availability(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    doctor_id=db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)

    date=db.Column(db.String(20), nullable=False)
    time=db.Column(db.String(10), nullable=False)
    is_booked=db.Column(db.Boolean, default=False)

    doctor=db.relationship('Doctor', backref=db.backref('availabilities', lazy=True))