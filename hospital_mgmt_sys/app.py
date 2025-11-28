from flask import Flask, render_template
from backend.database import db, init_db
from backend.controllers import admin_bp, doctor_bp, patient_bp

def create_app():
    app=Flask(__name__)

#configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hospital.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
    app.config["SECRET_KEY"]="secrettt"

    #initialise database
    db.init_app(app)
    init_db(app)

    #blueprints/ routes
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)

    #home route
    @app.route("/") 
    def home(): 
        return render_template("landing.html")
    
    return app

if __name__=="__main__":
    app=create_app()
    app.run(debug=True)