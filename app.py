import os
import io
import base64
import qrcode
import logging
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db, Worker, Attendance

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# configure the database, relative to the app instance folder
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

with app.app_context():
    db.create_all()

# Template filter for date formatting
@app.template_filter('dateformat')
def dateformat(value, format='%Y-%m-%d'):
    if value is None:
        return "Date inconnue"
    if isinstance(value, str):
        return value[:10]  # For string dates
    return value.strftime(format)

@app.route('/')
def index():
    """Home page with navigation options"""
    worker_count = Worker.query.count()
    
    # Get today's attendance count
    today = date.today()
    attendance_today = Attendance.query.filter_by(date=today).count()
    
    return render_template('index.html', 
                         worker_count=worker_count, 
                         attendance_today=attendance_today)

@app.route('/add_worker', methods=['GET', 'POST'])
def add_worker():
    """Add a new worker to the system"""
    if request.method == 'POST':
        matricule = request.form.get('matricule', '').strip()
        name = request.form.get('name', '').strip()
        
        if not matricule or not name:
            flash('Matricule et nom sont requis', 'error')
            return render_template('add_worker.html')
        
        # Check if worker already exists
        existing_worker = Worker.query.filter_by(matricule=matricule).first()
        if existing_worker:
            flash('Un ouvrier avec ce matricule existe déjà', 'error')
            return render_template('add_worker.html')
        
        # Add worker to database
        new_worker = Worker(matricule=matricule, name=name)
        db.session.add(new_worker)
        db.session.commit()
        
        flash(f'Ouvrier {name} ajouté avec succès', 'success')
        return redirect(url_for('worker_qr', matricule=matricule))
    
    return render_template('add_worker.html')

@app.route('/view_workers')
def view_workers():
    """View all workers in the system"""
    workers = Worker.query.all()
    # Convert to dictionary format for template compatibility
    workers_dict = {worker.matricule: worker for worker in workers}
    return render_template('view_workers.html', workers=workers_dict)

@app.route('/worker_qr/<matricule>')
def worker_qr(matricule):
    """Generate and display QR code for a worker"""
    worker = Worker.query.filter_by(matricule=matricule).first()
    
    if not worker:
        flash('Ouvrier non trouvé', 'error')
        return redirect(url_for('view_workers'))
    
    # Generate QR code
    presence_url = request.url_root + f"presence/{matricule}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(presence_url)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    qr_code_b64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return render_template('worker_qr.html', 
                         worker=worker, 
                         qr_code=qr_code_b64,
                         presence_url=presence_url)

@app.route('/presence/<matricule>')
def mark_presence(matricule):
    """Mark worker presence when QR code is scanned"""
    worker = Worker.query.filter_by(matricule=matricule).first()
    
    if not worker:
        return render_template('presence_confirmation.html', 
                             success=False, 
                             message="Matricule non trouvé dans le système")
    
    now = datetime.now()
    today = now.date()
    current_time = now.time()
    
    # Check if already marked today
    existing_attendance = Attendance.query.filter_by(
        worker_id=worker.id, 
        date=today
    ).first()
    
    if existing_attendance:
        return render_template('presence_confirmation.html',
                             success=False,
                             worker=worker,
                             message=f"Présence déjà enregistrée pour aujourd'hui")
    
    # Record attendance
    attendance_record = Attendance(
        worker_id=worker.id,
        date=today,
        time=current_time
    )
    
    db.session.add(attendance_record)
    db.session.commit()
    
    return render_template('presence_confirmation.html',
                         success=True,
                         worker=worker,
                         time=current_time.strftime("%H:%M:%S"),
                         date=today.strftime("%Y-%m-%d"),
                         message="Présence enregistrée avec succès!")

@app.route('/attendance_log')
def attendance_log():
    """View attendance log for all workers"""
    # Get date filter from query params
    date_filter = request.args.get('date', date.today().strftime("%Y-%m-%d"))
    filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
    
    # Get all workers with their attendance for the specified date
    workers = Worker.query.all()
    attendance_data = []
    
    for worker in workers:
        # Find attendance record for this worker on the specified date
        attendance_record = Attendance.query.filter_by(
            worker_id=worker.id,
            date=filter_date
        ).first()
        
        attendance_data.append({
            'matricule': worker.matricule,
            'name': worker.name,
            'present': attendance_record is not None,
            'time': attendance_record.time.strftime("%H:%M:%S") if attendance_record else None
        })
    
    # Sort by name
    attendance_data.sort(key=lambda x: x['name'])
    
    present_count = sum(1 for record in attendance_data if record['present'])
    
    return render_template('attendance_log.html', 
                         attendance_data=attendance_data,
                         selected_date=date_filter,
                         total_workers=len(workers),
                         present_count=present_count)

@app.route('/delete_worker/<matricule>')
def delete_worker(matricule):
    """Delete a worker from the system"""
    worker = Worker.query.filter_by(matricule=matricule).first()
    
    if worker:
        # Delete worker (cascade will handle attendance records)
        db.session.delete(worker)
        db.session.commit()
        flash('Ouvrier supprimé avec succès', 'success')
    else:
        flash('Ouvrier non trouvé', 'error')
    
    return redirect(url_for('view_workers'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
