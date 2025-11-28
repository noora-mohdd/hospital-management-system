from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.database import db
from backend.models import Patient, Doctor, Appointment, History

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

        if Patient.query.filter_by(username=username).first():
            flash("username already taken", "error")
            return redirect(url_for("patient.register"))
        
        if Patient.query.filter_by(email=email).first():
            flash("email already taken", "error")
            return redirect(url_for("patient.register"))       

        new_user= Patient(
            full_name=full_name,
            username=username,
            email=email,
            password=password,
            is_admin=False
        )     
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("patient.login"))
    
    return render_template("register.html")

#patient login
@patient_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username")   
        password=request.form.get("password")

        user=Patient.query.filter_by(username=username).first()

        if not user:
            flash("user not found", "danger")
            return redirect(url_for("patient.login"))
        if user.password!= password:
            flash("incorrect password", "danger")
            return redirect(url_for("patient.login"))
        
        if user.is_blacklisted:
            flash("you are blacklisted", "danger")
            return redirect(url_for("patient.login"))
        
        #store user in session 
        session["user_id"]=user.id
        session["role"]="admin" if user.is_admin else "patient"

        if user.is_admin:
            return redirect(url_for("admin.dashboard"))
        else:
            return redirect(url_for("patient.login"))
    return render_template("login.html")

#patient dashboard
@patient_bp.route("/dashboard")
def dashboard():
    if session.get("role")!="patient":
        return redirect(url_for("patient.login"))
    
    return render_template("patient-dash.html")

#--------------------
#admin routes
#--------------------

@admin_bp.route("/dashboard")
def dashboard():
    if session.get("role")!="admin":
        return redirect(url_for("patient.login"))
    return render_template("admin-dash.html")

#--------------------
#doctor routes
#--------------------
@doctor_bp.route("/login", methods=["GET", "POST"])
def doctor_login():
    if request.method=="POST":
        username=request.form.get("username")   
        password=request.form.get("password")

        doc=Doctor.query.filter_by(username=username).first()

        if not doc:
            flash("doctor not found", "danger")
            return redirect(url_for("doctor.doctor_login"))
        if doc.password!= password:
            flash("incorrect password", "danger")
            return redirect(url_for("doctor.doctor_login"))
        
        if doc.is_blacklisted:
            flash("you are blacklisted by admin", "danger")
            return redirect(url_for("doctor.doctor_login"))
        
        #store doc in session 
        session["user_id"]=doc.id
        session["role"]="doctor"

        return redirect(url_for("doctor.dashboard"))
    return render_template("doctor_login.html")

@doctor_bp.route("/dashboard")
def dashboard():
    if session.get("role")!="doctor":
        return redirect(url_for("doctor.doctor_login"))
    return render_template("doctor-dash.html")

#------------------
#logout
#------------------
@patient_bp.route("/logout")
@doctor_bp.route("/logout")
@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("patient.login"))



