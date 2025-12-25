# Hospital Management System

A role-based Hospital Management System built using **Flask**, **SQLAlchemy**, **SQLite**, **HTML**, **boostratp**, **CSS**, and **Jinja2**.

This project allows admins, doctors, and patients to interact with the system through clearly defined roles and functionalities, simulating a real-world hospital workflow.

---

## 📌 What This Project Does

This application helps manage:
- Doctors and their availability
- Patient registrations and profiles
- Appointment booking and cancellation
- Treatment history and medical records

The focus of the project is on **clean CRUD operations**, role-based access, and a functional full-stack Flask application.

---

## 👥 User Roles & Features

### Admin
- Login as admin
- Add, edit, delete doctors
- Blacklist / unblacklist doctors and patients
- View all doctors and patients
- View upcoming and past appointments
- Search doctors and patients
- View patient appointment history

---

### Doctor
- Login as doctor
- Add availability slots
- View upcoming appointments
- Complete appointments
- Add patient treatment history
- Cancel appointments
- View assigned patient history

---

### Patient
- Register and login
- Edit profile
- Browse doctors by department
- View doctor availability
- Book appointments
- Cancel appointments
- View past appointments
- View medical history

---

## Tech Stack

### Backend
- Flask
- Flask SQLAlchemy (ORM)
- SQLite

### Frontend
- HTML
- CSS
- Jinja2 Templates

---

##  How to Run This Project Locally
```bash
git clone <your-repo-url>
cd hospital-mgmt-sys
python -m venv venv
venv\Scripts\activate
source venv/bin/activate
pip install flask flask_sqlalchemy
python app.py
```

## Project structure
hospital-mgmt-sys/
│
├── backend/
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│
├── templates/
├── static/
│
├── instance/          # runtime DB (ignored in git)
├── app.py
├── README.md
├── .gitignore


This project helped me understand full-stack web development concepts deeply and was awarded an S Grade for clean design, functionality, and implementation 😋
