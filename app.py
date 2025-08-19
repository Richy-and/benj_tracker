import os
import io
import base64
import qrcode
import logging
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db, Worker, Attendance

# === CONFIGURATION LOGGING ===
logging.basicConfig(level=logging.DEBUG)

# === FLASK SETUP ===
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# === BASE DE DONNÉES SUPABASE ===
database_url = os.environ.get("SUPABASE_DB_URL")  # ✅ clé d’environnement à créer sur Render
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}



# === FILTRE POUR AFFICHAGE DES DATES ===
@app.template_filter('dateformat')
def dateformat(value, format='%Y-%m-%d'):
    if value is None:
        return "Date inconnue"
    if isinstance(value, str):
        return value[:10]
    return value.strftime(format)

# === ROUTES ===

@app.route('/')
def index():
    worker_count = Worker.query.count()
    today = date.today()
    attendance_today = Attendance.query.filter_by(date=today).count()
    return render_template('index.html', worker_count=worker_count, attendance_today=attendance_today)

@app.route('/add_worker', methods=['GET', 'POST'])
def add_worker():
    if request.method == 'POST':
        matricule = request.form.get('matricule', '').strip()
        name = request.form.get('name', '').strip()
        if not matricule or not name:
            flash('Matricule et nom sont requis', 'error')
            return render_template('add_worker.html')

        if Worker.query.filter_by(matricule=matricule).first():
            flash('Un ouvrier avec ce matricule existe déjà', 'error')
            return render_template('add_worker.html')

        new_worker = Worker(matricule=matricule, name=name)
        db.session.add(new_worker)
        db.session.commit()
        flash(f'Ouvrier {name} ajouté avec succès', 'success')
        return redirect(url_for('worker_qr', matricule=matricule))
    return render_template('add_worker.html')

@app.route('/view_workers')
def view_workers():
    workers = Worker.query.all()
    workers_dict = {worker.matricule: worker for worker in workers}
    return render_template('view_workers.html', workers=workers_dict)

@app.route('/worker_qr/<matricule>')
def worker_qr(matricule):
    worker = Worker.query.filter_by(matricule=matricule).first()
    if not worker:
        flash('Ouvrier non trouvé', 'error')
        return redirect(url_for('view_workers'))

    presence_url = request.url_root + f"presence/{matricule}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(presence_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    qr_code_b64 = base64.b64encode(img_buffer.getvalue()).decode()

    return render_template('worker_qr.html', worker=worker, qr_code=qr_code_b64, presence_url=presence_url)

@app.route('/presence/<matricule>')
def mark_presence(matricule):
    worker = Worker.query.filter_by(matricule=matricule).first()
    if not worker:
        return render_template('presence_confirmation.html', success=False, message="Matricule non trouvé")

    now = datetime.now()
    today = now.date()
    current_time = now.time()

    if Attendance.query.filter_by(worker_id=worker.id, date=today).first():
        return render_template('presence_confirmation.html', success=False, worker=worker, message="Déjà marqué présent aujourd'hui")

    new_attendance = Attendance(worker_id=worker.id, date=today, time=current_time)
    db.session.add(new_attendance)
    db.session.commit()

    return render_template('presence_confirmation.html', success=True, worker=worker, time=current_time.strftime("%H:%M:%S"), date=today.strftime("%Y-%m-%d"), message="Présence enregistrée avec succès!")

@app.route('/attendance_log')
def attendance_log():
    date_filter = request.args.get('date', date.today().strftime("%Y-%m-%d"))
    filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
    workers = Worker.query.all()
    attendance_data = []

    for worker in workers:
        record = Attendance.query.filter_by(worker_id=worker.id, date=filter_date).first()
        attendance_data.append({
            'matricule': worker.matricule,
            'name': worker.name,
            'present': record is not None,
            'time': record.time.strftime("%H:%M:%S") if record else None
        })

    attendance_data.sort(key=lambda x: x['name'])
    present_count = sum(1 for r in attendance_data if r['present'])

    return render_template('attendance_log.html', attendance_data=attendance_data, selected_date=date_filter, total_workers=len(workers), present_count=present_count)

@app.route('/delete_worker/<matricule>')
def delete_worker(matricule):
    worker = Worker.query.filter_by(matricule=matricule).first()
    if worker:
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
# === LIER SQLAlchemy À L'APPLICATION ===
db.init_app(app)

# === CRÉER LES TABLES SI INEXISTANTES ===
with app.app_context():
    db.create_all()
