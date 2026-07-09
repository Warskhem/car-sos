import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from io import BytesIO
from sqlalchemy import func

from config import Config
from models import db, User, QRCode, Vehicle, EmergencyContact, SOSLog
from utils.qr_generator import generate_unique_code, generate_qr_image, qr_to_base64
from utils.beep_generator import generate_beep_wav, generate_sos_pattern
from services.plivo_service import PlivoService

app = Flask(__name__)
app.config.from_object(Config)
app.config['TEMPLATES_AUTO_RELOAD'] = True

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()
    if not User.query.filter_by(is_admin=True).first():
        admin = User(email='admin@carsos.com', name='Admin', phone='+0000000000', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    beep_data = generate_beep_wav(duration=0.5, frequency=880, volume=0.8)
    beep_path = os.path.join(app.static_folder, 'beep.wav')
    os.makedirs(app.static_folder, exist_ok=True)
    if not os.path.exists(beep_path):
        with open(beep_path, 'wb') as f:
            f.write(beep_data)

twilio_service = PlivoService(
    auth_id=app.config['PLIVO_AUTH_ID'],
    auth_token=app.config['PLIVO_AUTH_TOKEN'],
    from_number=app.config['PLIVO_PHONE_NUMBER']
)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.context_processor
def inject_globals():
    return {'site_url': app.config['SITE_URL']}

def admin_required(f):
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')

        user = User(email=email, name=name, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('user_dashboard'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin_dashboard'))
            return redirect(next_page or url_for('user_dashboard'))
        flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def user_dashboard():
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).order_by(EmergencyContact.priority).all()
    return render_template('user_dashboard.html', vehicles=vehicles, contacts=contacts)

@app.route('/dashboard/vehicle/<int:vehicle_id>/edit', methods=['POST'])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = db.session.get(Vehicle, vehicle_id)
    if not vehicle or vehicle.user_id != current_user.id:
        abort(403)

    vehicle.make = request.form.get('make')
    vehicle.model = request.form.get('model')
    vehicle.year = int(request.form.get('year'))
    vehicle.plate = request.form.get('plate')
    vehicle.color = request.form.get('color', '')
    db.session.commit()
    flash('Vehicle updated!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/dashboard/contact/add', methods=['POST'])
@login_required
def add_contact():
    name = request.form.get('name')
    phone = request.form.get('phone')
    priority = int(request.form.get('priority'))

    existing = EmergencyContact.query.filter_by(user_id=current_user.id, priority=priority).first()
    if existing:
        existing.name = name
        existing.phone = phone
    else:
        contact = EmergencyContact(
            user_id=current_user.id,
            name=name,
            phone=phone,
            priority=priority
        )
        db.session.add(contact)
    db.session.commit()
    flash('Emergency contact saved!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/dashboard/contact/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact = db.session.get(EmergencyContact, contact_id)
    if not contact or contact.user_id != current_user.id:
        abort(403)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact removed', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/dashboard/history')
@login_required
def sos_history():
    vehicle_ids = [v.id for v in Vehicle.query.filter_by(user_id=current_user.id).all()]
    logs = SOSLog.query.filter(SOSLog.vehicle_id.in_(vehicle_ids)).order_by(SOSLog.contacted_at.desc()).all() if vehicle_ids else []
    return render_template('sos_history.html', logs=logs)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, is_admin=True).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials', 'danger')

    return render_template('admin_login.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_qrs = QRCode.query.count()
    claimed_qrs = QRCode.query.filter_by(is_claimed=True).count()
    unclaimed_qrs = total_qrs - claimed_qrs
    total_users = User.query.filter_by(is_admin=False).count()
    total_vehicles = Vehicle.query.count()
    total_sos = SOSLog.query.count()
    today_sos = SOSLog.query.filter(SOSLog.contacted_at >= datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)).count()

    qr_codes = QRCode.query.order_by(QRCode.created_at.desc()).limit(50).all()
    recent_logs = SOSLog.query.order_by(SOSLog.contacted_at.desc()).limit(10).all()

    return render_template('admin_dashboard.html',
        total_qrs=total_qrs, claimed_qrs=claimed_qrs, unclaimed_qrs=unclaimed_qrs,
        total_users=total_users, total_vehicles=total_vehicles,
        total_sos=total_sos, today_sos=today_sos,
        qr_codes=qr_codes, recent_logs=recent_logs)

@app.route('/admin/qr/generate', methods=['GET', 'POST'])
@admin_required
def admin_generate_qr():
    if request.method == 'POST':
        count = int(request.form.get('count', 1))
        new_codes = []
        for _ in range(count):
            code = generate_unique_code()
            qr = QRCode(code=code)
            db.session.add(qr)
            new_codes.append(code)
        db.session.commit()
        flash(f'{count} QR codes generated!', 'success')
        return redirect(url_for('admin_generate_qr'))

    qr_codes = QRCode.query.order_by(QRCode.created_at.desc()).limit(50).all()
    return render_template('admin_qr.html', qr_codes=qr_codes)

@app.route('/admin/qr/<int:qr_id>/delete', methods=['POST'])
@admin_required
def admin_delete_qr(qr_id):
    qr = db.session.get(QRCode, qr_id)
    if not qr:
        abort(404)
    if qr.is_claimed:
        flash('Cannot delete a claimed QR code', 'danger')
    else:
        db.session.delete(qr)
        db.session.commit()
        flash('QR code deleted', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/sos-logs')
@admin_required
def admin_sos_logs():
    logs = SOSLog.query.order_by(SOSLog.contacted_at.desc()).all()
    return render_template('admin_sos_logs.html', logs=logs)

@app.route('/admin/export/qr-codes')
@admin_required
def admin_export_qr():
    import csv, io
    qrs = QRCode.query.order_by(QRCode.created_at.desc()).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Code', 'Claimed', 'Claimed By', 'Claimed At', 'Created At'])
    for q in qrs:
        cw.writerow([q.code, q.is_claimed, q.user.email if q.user else '', q.claimed_at or '', q.created_at])
    output = BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='qr-codes-export.csv')

@app.route('/sos/<code>', methods=['GET'])
def sos_landing(code):
    qr = QRCode.query.filter_by(code=code.upper()).first()
    if not qr:
        abort(404)

    if not qr.is_claimed:
        return redirect(url_for('sos_register', code=code.upper()))

    vehicle = Vehicle.query.filter_by(qr_code_id=qr.id).first()
    if not vehicle:
        abort(404)

    return render_template('sos_page.html', code=code.upper(), vehicle=vehicle)

@app.route('/sos/<code>/register', methods=['GET', 'POST'])
def sos_register(code):
    qr = QRCode.query.filter_by(code=code.upper()).first()
    if not qr:
        abort(404)

    if qr.is_claimed:
        return redirect(url_for('sos_landing', code=code.upper()))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        plate = request.form.get('plate')
        color = request.form.get('color', '')

        contact1_name = request.form.get('contact1_name')
        contact1_phone = request.form.get('contact1_phone')
        contact2_name = request.form.get('contact2_name')
        contact2_phone = request.form.get('contact2_phone')
        contact3_name = request.form.get('contact3_name')
        contact3_phone = request.form.get('contact3_phone')

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=name, phone=phone)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
        else:
            if not user.check_password(password):
                flash('Invalid password for this email', 'danger')
                return render_template('sos_register.html', code=code.upper())

        qr.is_claimed = True
        qr.claimed_at = datetime.utcnow()
        qr.user_id = user.id

        vehicle = Vehicle(
            user_id=user.id,
            qr_code_id=qr.id,
            make=make,
            model=model,
            year=int(year),
            plate=plate,
            color=color
        )
        db.session.add(vehicle)
        db.session.flush()

        contacts_data = [
            (1, contact1_name, contact1_phone),
            (2, contact2_name, contact2_phone),
            (3, contact3_name, contact3_phone),
        ]
        for priority, cname, cphone in contacts_data:
            if cname and cphone:
                existing = EmergencyContact.query.filter_by(user_id=user.id, priority=priority).first()
                if existing:
                    existing.name = cname
                    existing.phone = cphone
                else:
                    contact = EmergencyContact(user_id=user.id, name=cname, phone=cphone, priority=priority)
                    db.session.add(contact)

        db.session.commit()

        login_user(user)
        flash('Vehicle registered successfully! QR code is now active for SOS.', 'success')
        return redirect(url_for('user_dashboard'))

    return render_template('sos_register.html', code=code.upper())

@app.route('/sos/<code>/trigger', methods=['POST'])
def sos_trigger(code):
    qr = QRCode.query.filter_by(code=code.upper()).first()
    if not qr or not qr.is_claimed:
        return jsonify({'status': 'error', 'message': 'Invalid or unclaimed QR code'}), 404

    vehicle = Vehicle.query.filter_by(qr_code_id=qr.id).first()
    if not vehicle:
        return jsonify({'status': 'error', 'message': 'No vehicle found'}), 404

    data = request.get_json(silent=True) or {}
    lat = data.get('lat')
    lng = data.get('lng')

    user = db.session.get(User, qr.user_id)
    contacts = EmergencyContact.query.filter_by(user_id=qr.user_id).order_by(EmergencyContact.priority).all()

    log = SOSLog(
        qr_code_id=qr.id,
        vehicle_id=vehicle.id,
        rescuer_lat=lat,
        rescuer_lng=lng,
    )
    db.session.add(log)
    db.session.flush()

    location_url = f"https://maps.google.com/?q={lat},{lng}" if lat and lng else "Location not available"
    vehicle_info = {
        'make': vehicle.make,
        'model': vehicle.model,
        'year': vehicle.year,
        'plate': vehicle.plate,
        'color': vehicle.color or 'unknown'
    }

    calls_initiated = 0
    if twilio_service.is_configured():
        for contact in contacts:
            result = twilio_service.make_sos_call(
                to_number=contact.phone,
                vehicle_info=vehicle_info,
                location_url=location_url,
                site_url=app.config['SITE_URL']
            )
            if result.get('status') == 'initiated':
                calls_initiated += 1
        log.call_status = 'completed' if calls_initiated > 0 else 'failed'
    else:
        log.call_status = 'service_not_configured'

    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'SOS alert sent to all emergency contacts',
        'vehicle': f"{vehicle.make} {vehicle.model} ({vehicle.plate})",
        'location': location_url,
        'calls_sent': calls_initiated if twilio_service.is_configured() else 0,
        'log_id': log.id
    })

@app.route('/sos/<code>/auto-trigger-primary', methods=['POST'])
def sos_auto_trigger_primary(code):
    qr = QRCode.query.filter_by(code=code.upper()).first()
    if not qr or not qr.is_claimed:
        return jsonify({'status': 'error', 'message': 'Invalid QR code'}), 404

    vehicle = Vehicle.query.filter_by(qr_code_id=qr.id).first()
    if not vehicle:
        return jsonify({'status': 'error', 'message': 'No vehicle found'}), 404

    data = request.get_json(silent=True) or {}
    lat = data.get('lat')
    lng = data.get('lng')

    primary = EmergencyContact.query.filter_by(user_id=qr.user_id, priority=1).first()
    if not primary:
        return jsonify({'status': 'error', 'message': 'No primary contact found'}), 404

    location_url = f"https://maps.google.com/?q={lat},{lng}" if lat and lng else "Location not available"
    vehicle_info = {
        'make': vehicle.make, 'model': vehicle.model,
        'year': vehicle.year, 'plate': vehicle.plate,
        'color': vehicle.color or 'unknown'
    }

    call_result = {'status': 'skipped'}
    sms_result = {'status': 'skipped'}
    if twilio_service.is_configured():
        call_result = twilio_service.make_sos_call(
            to_number=primary.phone,
            vehicle_info=vehicle_info,
            location_url=location_url,
            site_url=app.config['SITE_URL']
        )
        sms_result = twilio_service.send_location_sms(
            to_number=primary.phone,
            vehicle_info=vehicle_info,
            location_url=location_url
        )

    log = SOSLog(
        qr_code_id=qr.id, vehicle_id=vehicle.id,
        rescuer_lat=lat, rescuer_lng=lng,
        call_status='auto_primary'
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Primary contact alerted',
        'vehicle': f"{vehicle.make} {vehicle.model} ({vehicle.plate})",
        'location': location_url,
        'call': call_result.get('status'),
        'sms': sms_result.get('status'),
        'primary_name': primary.name
    })

@app.route('/plivo/answer-sos', methods=['GET'])
def plivo_answer_sos():
    make = request.args.get('make', 'Unknown')
    model = request.args.get('model', 'Unknown')
    year = request.args.get('year', '')
    plate = request.args.get('plate', '')
    color = request.args.get('color', '')
    location = request.args.get('location', 'Location not available')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak voice="WOMAN">EMERGENCY SOS ALERT. Vehicle {make} {model}, year {year}, plate number {plate}, color {color}. Location: {location}. An accident or breakdown has been reported. Please respond immediately.</Speak>
    <Play>{app.config["SITE_URL"]}/static/beep.wav</Play>
    <Play>{app.config["SITE_URL"]}/static/beep.wav</Play>
    <Play>{app.config["SITE_URL"]}/static/beep.wav</Play>
</Response>'''
    return xml, 200, {'Content-Type': 'application/xml'}

@app.route('/sticker/<code>')
def sticker_view(code):
    qr = QRCode.query.filter_by(code=code.upper()).first()
    if not qr:
        abort(404)

    qr_url = f"{app.config['SITE_URL']}/sos/{code.upper()}"
    qr_b64 = qr_to_base64(qr_url, box_size=12, border=2)
    vehicle = Vehicle.query.filter_by(qr_code_id=qr.id).first()
    return render_template('sticker.html', code=code.upper(), qr_b64=qr_b64, vehicle=vehicle, claimed=qr.is_claimed)

@app.route('/sticker/<code>/download')
def sticker_download(code):
    qr = QRCode.query.filter_by(code=code.upper()).first()
    if not qr:
        abort(404)

    qr_url = f"{app.config['SITE_URL']}/sos/{code.upper()}"
    img = generate_qr_image(qr_url, box_size=20, border=2)

    vehicle = Vehicle.query.filter_by(qr_code_id=qr.id).first()

    from PIL import Image, ImageDraw, ImageFont
    sticker_w = 600
    sticker_h = 700
    sticker = Image.new('RGB', (sticker_w, sticker_h), 'white')
    draw = ImageDraw.Draw(sticker)

    qr_size = 400
    qr_resized = img.resize((qr_size, qr_size), Image.LANCZOS)
    sticker.paste(qr_resized, ((sticker_w - qr_size) // 2, 40))

    try:
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 20)
        font_tiny = ImageFont.truetype("arial.ttf", 16)
    except (IOError, OSError):
        font_large = ImageFont.load_default()
        font_small = font_large
        font_tiny = font_large

    draw.text((sticker_w // 2, 470), "SOS EMERGENCY", fill='red', anchor='mt', font=font_large)
    url_text = f"{app.config['SITE_URL'].replace('http://', '').replace('https://', '')}/{code.upper()}"
    draw.text((sticker_w // 2, 520), url_text, fill='black', anchor='mt', font=font_small)
    draw.text((sticker_w // 2, 555), "Scan to alert emergency contacts", fill='#555', anchor='mt', font=font_tiny)
    draw.text((sticker_w // 2, 580), "in case of accident or breakdown", fill='#555', anchor='mt', font=font_tiny)

    if vehicle:
        draw.text((sticker_w // 2, 630), f"{vehicle.make} {vehicle.model} - {vehicle.plate}", fill='#333', anchor='mt', font=font_tiny)

    img_buffer = BytesIO()
    sticker.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name=f'sos-sticker-{code.upper()}.png')

@app.route('/static/beep.wav')
def serve_beep():
    beep_path = os.path.join(app.static_folder, 'beep.wav')
    if os.path.exists(beep_path):
        return send_file(beep_path, mimetype='audio/wav')
    beep_data = generate_beep_wav(0.5, 880, 0.8)
    return send_file(BytesIO(beep_data), mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
