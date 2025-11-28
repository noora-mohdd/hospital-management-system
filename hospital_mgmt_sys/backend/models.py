from backend.database import db

#departments table
class Departments(db.model):
    id=db.column(db.Integer, primary_key=True)
    name=db.column(db.String(100), unique=True, nullable=False)
    description=db.column(db.Text)

    doctors=db.relationship("Doctor",backref="department", lazy=True)



#patient table
class Patient(db.model):
    id=db.column(db.Integer, primary_key=True)
    full_name=db.column(db.String(100), nullable=False)
    username=db.column(db.String(50), unique=True, nullable=False)
    email=db.column(db.String(100), unique=True)
    password=db.column(db.String(100), nullable=False)
    age=db.column(db.Integer)
    is_blacklisted= db.column(db.Boolean, default=False)
    is_admin= db.column(db.Boolean, default=False)

    appointments=db.relationship("Appointment", backref="patient", lazy=True)

#doctors table
class Doctor(db.model):
    id=db.column(db.Integer, primary_key=True)
    full_name=db.column(db.String(100), nullable=False)
    username=db.column(db.String(50), unique=True, nullable=False)
    email=db.column(db.String(100), unique=True)
    password=db.column(db.String(100), nullable=False)
    specialization=db.column(db.String(100))
    experience=db.column(db.Integer)
    is_blacklisted=db.column(db.Boolean, default=False)

    appointments=db.relationship("Appointment", backref="doctor", lazy=True)

#appointment table
class Appointment(db.model):
    id=db.column(db.Integer, primary_key=True)
    patient_id=db.column(db.Integer, db.ForeignKey("patient.id"))
    doctor_id=db.column(db.Integer, db.ForeignKey("doctor.id"))
    date=db.column(db.String(20))
    time=db.column(db.String(20))
    status=db.column(db.String(20))

    history=db.relationship("History", backref="appointment", uselist=False)

#history/treatment table
class History(db.model):
    id=db.column(db.Integer, primary_key=True)
    
    appointment_id=db.column(db.Integer, db.ForeignKey("appointment.id"), unique=True)

    visit_type=db.column(db.String(100))
    test_done=db.column(db.String(100))
    diagnosis=db.column(db.Text)
    prescription=db.column(db.Text)
    medicine=db.column(db.Text)
