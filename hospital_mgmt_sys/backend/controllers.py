from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.database import db
from backend.models import Patient, Doctor, Appointment, History, Availability


#blueprints
admin_bp=Blueprint("admin", __name__, url_prefix="/admin")
doctor_bp=Blueprint("doctor", __name__, url_prefix="/doctor")
patient_bp=Blueprint("patient", __name__, url_prefix="/patient")

#--------------------
#patient routes
#-------------------

#patient registration
@patient_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="POST":
        full_name=request.form.get("full_name")
        username=request.form.get("username")
        email=request.form.get("email")
        password=request.form.get("password")
        age=request.form.get("age")

        #checks duplicates
        if Patient.query.filter_by(username=username).first():
            flash("Username already taken", "danger")
            return redirect(url_for("patient.register"))

        if Patient.query.filter_by(email=email).first():
            flash("email already taken", "danger")
            return redirect(url_for("patient.register"))       

        new_user= Patient(
            full_name=full_name,
            username=username,
            email=email,
            password=password,
            age=int(age),
            is_admin=False
        )     
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("patient.login"))
    
    return render_template("register.html")

#patient/admin/doctor login
@patient_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username")   
        password=request.form.get("password")

        #check patient table
        user=Patient.query.filter_by(username=username).first()

        if user:

            if user.password!= password:
                flash("incorrect password", "danger")
                return redirect(url_for("patient.login"))
            
            if user.is_blacklisted:
                flash("you are blacklisted by admin", "danger")
                return redirect(url_for("patient.login"))
            
            #store user in session 
            session["user_id"]=user.id
            session["role"]="admin" if user.is_admin else "patient"

            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            else:
                return redirect(url_for("patient.dashboard"))
            
        #check doctor table
        doctor=Doctor.query.filter_by(username=username).first()

        if doctor:

            if doctor.password!= password:
                flash("incorrect password", "danger")
                return redirect(url_for("patient.login"))
            
            if doctor.is_blacklisted:
                flash("you are blacklisted by admin", "danger")
                return redirect(url_for("patient.login"))
            
            #store user in session 
            session["user_id"]=doctor.id
            session["role"]="doctor"
            return redirect(url_for("doctor.dashboard"))

        # if no match found
        flash("user not found", "danger")
        return redirect(url_for("patient.login"))
    return render_template("login.html")

#patient dashboard
@patient_bp.route("/dashboard")
def dashboard():
    if session.get("role")!="patient":
        return redirect(url_for("patient.login"))
    patient=Patient.query.get(session["user_id"])
    upcoming=Appointment.query.filter_by(
        patient_id=patient.id, status="Booked"
    ).order_by(Appointment.date, Appointment.time).all()

    past=Appointment.query.filter(
        Appointment.patient_id==patient.id,
        Appointment.status!="Booked"
    ).order_by(Appointment.date.desc()).all()

    departments=(
        db.session.query(Doctor.specialization)
        .distinct()
        .all()
    )

    departments=[d[0] for d in departments]
    
    return render_template("patient-dash.html", 
                           patient=patient, 
                           upcoming=upcoming, 
                           past=past,
                           departments=departments)

#view doctor
@patient_bp.route("/doctor/<int:id>")
def about_doctor(id):
    doctor=Doctor.query.get_or_404(id)
    return render_template("about-doc.html", doctor=doctor)

#view availability (patient view)
@patient_bp.route("/doctor/<int:id>/availability")
def doctor_availability(id):
    doctor=Doctor.query.get_or_404(id)

    #fetch all unbooked slots for the doc
    slots=Availability.query.filter_by(doctor_id=id, is_booked=False).all()

    #grp slots by date
    grouped={}
    for s in slots:
        grouped.setdefault(s.date, []).append(s)

    return render_template("doc-availability.html", doctor=doctor, grouped_slots=grouped)   

#booking
@patient_bp.route("/book/<int:slot_id>", methods=["POST"])
def book(slot_id):
    if session.get("role")!="patient":
        return redirect(url_for("patient.login"))
    
    slot=Availability.query.get_or_404(slot_id)

    if slot.is_booked:
        flash("slot already booked", "danger")
        return redirect(url_for("patient.dashboard"))
    
    #create appointment
    doctor_id=slot.doctor_id

    appt=Appointment(
        patient_id=session["user_id"],
        doctor_id=doctor_id,
        date=slot.date,
        time=slot.time,
        status="Booked"
    )

    #mark slot as used
    slot.is_booked=True

    db.session.add(appt)
    db.session.commit()

    flash("appointment booked", "success")
    return redirect(url_for("patient.dashboard"))

#cancel appointment
@patient_bp.route("/cancel/<int:appt_id>", methods=["POST"])
def cancel_appointment(appt_id):
    if session.get("role")!="patient":
        return redirect(url_for("patient.login"))
    
    appt=Appointment.query.get_or_404(appt_id)

    if appt.patient_id!=session["user_id"]:
        flash("not your appointment", "danger")
        return redirect(url_for("patient.dashboard"))
    
    #reset appt status to cancelled
    appt.status="Cancelled"

    #free the slot again
    slot=Availability.query.filter_by(
        doctor_id=appt.doctor_id,
        date=appt.date,
        time=appt.time
    ).first()

    if slot:
        slot.is_booked=False

    db.session.commit()

    flash("appointment cancelled", "success")
    return redirect(url_for("patient.dashboard"))

#edit profile
@patient_bp.route("/edit", methods=["GET","POST"])
def edit_profile():
    if session.get("role")!="patient":
        return redirect(url_for("patient.login"))
    
    patient=Patient.query.get(session["user_id"])

    if request.method=="POST":
        patient.full_name=request.form.get("full_name")
        patient.email=request.form.get("email")
        patient.age=request.form.get("age")

        db.session.commit()
        flash("profile updated", "success")
        return redirect(url_for("patient.dashboard"))
    
    return render_template("edit-patient.html", patient=patient)

#patient history
@patient_bp.route("/history")
def patient_history():
    if session.get("role")!="patient":
        return redirect(url_for("patient.login"))
    
    patient_id=session["user_id"]
    patient= Patient.query.get_or_404(patient_id)

    #all completed appts
    completed_appts=Appointment.query.filter_by(
        patient_id=patient_id,
        status="Completed"
    ).all()

    #extract history items
    history_items=[]
    for appt in completed_appts:
        if appt.history:
            history_items.append(appt.history)

    return render_template("patient-history.html", completed=history_items, patient=patient)


#view department 
@patient_bp.route("/department/<string:name>")
def department_details(name):
    doctors=Doctor.query.filter_by(specialization=name).all()
    return render_template("dept-details.html", dept_name=name, doctors=doctors )

#--------------------
#admin routes
#--------------------
#admin dashboard
@admin_bp.route("/dashboard")
def dashboard():
    if session.get("role")!="admin":
        return redirect(url_for("patient.login"))
    
    doctor_list=Doctor.query.all()
    patient_list=Patient.query.filter_by(is_admin=False).all() #admin not counted

    upcoming=Appointment.query.filter_by(status="Booked").all()
    past=Appointment.query.filter(Appointment.status!="Booked").all()

    return render_template("admin-dash.html",
                           doctors=doctor_list,
                           patients=patient_list,
                           upcoming=upcoming,
                           past=past,
                           total_doctors=len(doctor_list),
                           total_patients=len(patient_list),
                           total_upcoming=len(upcoming))

#admin creates doc
@admin_bp.route("/doctors/create", methods=["GET", "POST"])
def create_doctor():
    if session.get("role")!="admin":
        return redirect(url_for("patient.login"))
    
    if request.method=="POST":
        new_doc=Doctor(
            full_name=request.form["full_name"],
            email=request.form["email"],
            password=request.form["password"],
            specialization=request.form["specialization"],
            experience=request.form["experience"],
            username=request.form["username"]
        )

        db.session.add(new_doc)
        db.session.commit()

        flash("doctor added", "success")
        return redirect(url_for("admin.dashboard"))
    
    return render_template("add-doc.html")

#edit/ delete/ blacklist doctors
@admin_bp.route("/doctor/<int:id>/edit", methods=["GET", "POST"])
def edit_doctor(id):
    doctor= Doctor.query.get_or_404(id)

    if request.method=="POST":
        doctor.full_name=request.form["full_name"]
        doctor.email=request.form["email"]
        doctor.specialization=request.form["specialization"]
        doctor.experience=request.form["experience"]
        db.session.commit()
        flash("updated", "success")
        return redirect(url_for("admin.dashboard"))
    
    return render_template("edit-doc.html", doctor=doctor)

@admin_bp.route("/doctor/<int:id>/delete", methods=["POST"])
def delete_doctor(id):
    doctor=Doctor.query.get_or_404(id)
    Availability.query.filter_by(doctor_id=id).delete()
    Appointment.query.filter_by(doctor_id=id).delete()
    db.session.delete(doctor)
    db.session.commit()
    flash("doctor deleted", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/doctor/<int:id>/blacklist", methods=["POST"])
def blacklist_doctor(id):
    doctor=Doctor.query.get_or_404(id)
    #toggle blacklist doctor
    doctor.is_blacklisted=not doctor.is_blacklisted
    db.session.commit()
    flash("blacklist toggled", "success")
    return redirect(url_for("admin.dashboard"))

#edit/ delete/ blacklist patients
@admin_bp.route("/patient/<int:id>/edit", methods=["GET", "POST"])
def edit_patient(id):
    pat= Patient.query.get_or_404(id)

    if request.method=="POST":
        pat.full_name=request.form["full_name"]
        pat.email=request.form["email"]
        pat.age=request.form["age"]

        db.session.commit()
        flash("updated", "success")
        return redirect(url_for("admin.dashboard"))
    
    return render_template("edit-patient.html", patient=pat)

@admin_bp.route("/patient/<int:id>/delete", methods=["POST"])
def delete_patient(id):
    pat=Patient.query.get_or_404(id)
    db.session.delete(pat)
    db.session.commit()
    flash("deleted", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/patient/<int:id>/blacklist", methods=["POST"])
def blacklist_patient(id):
    pat=Patient.query.get_or_404(id)
    pat.is_blacklisted=not pat.is_blacklisted
    db.session.commit()
    flash("blacklist toggled", "success")
    return redirect(url_for("admin.dashboard"))

#admin search
@admin_bp.route("/search")
def search():
    if session.get("role")!="admin":
        return redirect(url_for("patient.login"))
    
    q=request.args.get("q", "").strip()

    #if search is empty then return to dashboard
    if q=="":
        return redirect(url_for("admin.dashboard"))
    
    doctors=Doctor.query.filter(Doctor.full_name.ilike(f"%{q}%")).all()
    patients=Patient.query.filter(Patient.full_name.ilike(f"%{q}%"), Patient.is_admin==False).all()

    return render_template(
        "admin-dash.html",
        doctors=doctors,
        patients=patients,
        appointments=[],
        total_doctors=len(doctors),
        total_patients=len(patients),
        total_appointments=0,
        search_query=q
    )

#admin view history
@admin_bp.route("/appointment/<int:appt_id>/history")
def view_appointment_history(appt_id):
    if session.get("role")!="admin":
        return redirect(url_for("patient.login"))
    
    appt=Appointment.query.get_or_404(appt_id)

    if not appt.history:
        flash("This patient does not have any history yet", "warning")
        return redirect(url_for("admin.dashboard"))

    return render_template(
        "patient-history.html", 
        patient=appt.patient,
        doctor=appt.doctor,
        completed=[appt.history])

#--------------------
#doctor routes
#--------------------

@doctor_bp.route("/dashboard")
def dashboard():
    if session.get("role")!="doctor":
        return redirect(url_for("patient.login"))
    
    doc_id=session["user_id"]

    upcoming=Appointment.query.filter_by(
        doctor_id=doc_id, status="Booked"
    ).order_by(Appointment.date, Appointment.time).all()

    patient_ids={appt.patient_id for appt in upcoming}
    assigned_patients=Patient.query.filter(Patient.id.in_(patient_ids)).all()


    from datetime import date

    availabilities = Availability.query.filter_by(
        doctor_id=doc_id,
        is_booked=False
    ).filter(
        Availability.date >= date.today()
    ).order_by(Availability.date, Availability.time).all()


    return render_template("doctor-dash.html", upcoming=upcoming, assigned_patients=assigned_patients, availabilities=availabilities)

#provides availability 
@doctor_bp.route("/availability", methods=["GET", "POST"])
def provide_availability():
    if session.get("role")!="doctor":
        return redirect(url_for("patient.login"))
    
    if request.method=="POST":
        date=request.form.get("date")
        time=request.form.get("time")

        if not date or not time:
            flash("provide both date and time", "danger")
            return redirect(url_for("doctor.provide_availability"))
        
        #prevent duplicates
        existing=Availability.query.filter_by(
            doctor_id=session["user_id"],
            date=date,
            time=time
        ).first()

        if existing:
            flash("This slot already exists!", "warning")
            return redirect(url_for("doctor.provide_availability"))
        
        slot=Availability(
            doctor_id=session["user_id"],
            date=date,
            time=time
        )

        db.session.add(slot)
        db.session.commit()

        flash("availability added", "success")
        return redirect(url_for("doctor.dashboard"))
    
    return render_template("provide-availability.html")

#completes appointment+ saves history
@doctor_bp.route("/complete/<int:appt_id>", methods=["GET", "POST"])
def complete_appointment(appt_id):
    if session.get("role")!="doctor":
        return redirect(url_for("patient.login"))
    
    appt=Appointment.query.get_or_404(appt_id)

    if appt.doctor_id!=session["user_id"]:
        flash("not your appointment", "danger")
        return redirect(url_for("doctor.dashboard"))
    
    if request.method=="POST":
        visit_type=request.form.get("visit_type")
        test_done=request.form.get("test_done")
        diagnosis=request.form.get("diagnosis")
        prescription=request.form.get("prescription")
        medicine=request.form.get("medicine")

        appt.status="Completed"
        slot = Availability.query.filter_by(
            doctor_id=appt.doctor_id,
            date=appt.date,
            time=appt.time
        ).first()

        if slot:
            slot.is_booked = False

        hist=History(
            appointment_id=appt.id,
            visit_type=visit_type,
            test_done=test_done,
            diagnosis=diagnosis,
            prescription=prescription,
            medicine=medicine
        )
        db.session.add(hist)
        db.session.commit()

        flash("saved", "success")
        return redirect(url_for("doctor.dashboard"))
    
    return render_template("update-patient-history.html", appointment=appt)

#cancel appointment
@doctor_bp.route("/cancel/<int:appt_id>", methods=["POST"])
def doctor_cancel(appt_id):
    if session.get("role")!="doctor":
        return redirect(url_for("patient.login"))
    
    appt=Appointment.query.get_or_404(appt_id)

    if appt.doctor_id != session["user_id"]:
        flash("not your appointment", "danger")
        return redirect(url_for("doctor.dashboard"))
    
    appt.status="Cancelled"

    slot=Availability.query.filter_by(
        doctor_id=appt.doctor_id,
        date=appt.date,
        time=appt.time
    ).first()

    if slot:
        slot.is_booked = False #slot becomes free

    db.session.commit()
    flash("Appointment cancelled", "success")
    return redirect(url_for("doctor.dashboard"))

#view patient history
@doctor_bp.route("/patient/<int:patient_id>/history")
def patient_history(patient_id):
    if session.get("role")!="doctor":
        return redirect(url_for("patient.login"))
    
    patient=Patient.query.get_or_404(patient_id)

    #doctors should view only their patients
    completed=Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=session["user_id"],
        status="Completed"
    ).all()
    
    if not completed:
        flash("no history available for this appointment", "warning")
        return redirect(url_for("doctor.dashboard"))
    
    history_items=[appt.history for appt in completed if appt.history]    
    return render_template(
        "patient-history.html",
        completed=history_items,
        patient=patient
    )



#------------------
#logout
#------------------
@patient_bp.route("/logout")
@doctor_bp.route("/logout")
@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("patient.login"))



