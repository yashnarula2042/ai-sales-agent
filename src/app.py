import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from .lead_manager import LeadManager, LeadStatus, get_session, Lead
from .main import SalesAgentOrchestrator
import os
import threading

# Ensure data directory exists for database and uploads
if not os.path.exists('data'):
    os.makedirs('data')

app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)

lead_manager = LeadManager()
orchestrator = SalesAgentOrchestrator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/leads', methods=['GET'])
def get_leads():
    session = get_session()
    leads = session.query(Lead).all()
    leads_data = [
        {
            "id": l.id,
            "name": l.name,
            "email": l.email,
            "company": l.company,
            "status": l.status.value,
            "website": l.website,
            "error": l.error_message,
            "email_content": l.personalized_email
        } for l in leads
    ]
    session.close()
    return jsonify(leads_data)

@app.route('/api/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        try:
            file_path = os.path.join('data', file.filename)
            file.save(file_path)
            message = lead_manager.import_from_csv(file_path)
            return jsonify({"message": message})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/leads/add', methods=['POST'])
def add_lead():
    data = request.json
    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400
    
    try:
        success, message = lead_manager.add_single_lead(
            name=data.get('name'),
            email=data.get('email'),
            company=data.get('company'),
            website=data.get('website')
        )
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"error": message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/run', methods=['POST'])
def run_automation():
    if orchestrator.is_running:
        return jsonify({"message": "Automation is already running"}), 400
        
    thread = threading.Thread(target=orchestrator.run_automation_cycle)
    thread.daemon = True # Ensure thread doesn't block shutdown
    thread.start()
    return jsonify({"message": "Automation cycle started in background"})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "is_running": orchestrator.is_running,
        "is_paused": orchestrator.is_paused
    })

@app.route('/api/pause', methods=['POST'])
def pause_automation():
    orchestrator.pause()
    return jsonify({"message": "Automation paused"})

@app.route('/api/resume', methods=['POST'])
def resume_automation():
    orchestrator.resume()
    return jsonify({"message": "Automation resumed"})

@app.route('/api/clear', methods=['POST'])
def clear_leads():
    lead_manager.clear_all_leads()
    return jsonify({"message": "All leads cleared successfully"})

@app.route('/api/sample-csv', methods=['GET'])
def download_sample():
    content = "name,email,company,website\nJohn Doe,john@example.com,Example Corp,https://example.com"
    return content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=sample_leads.csv'
    }

@app.route('/api/stop', methods=['POST'])
def stop_automation():
    orchestrator.stop()
    return jsonify({"message": "Stop signal sent to automation."})

@app.route('/api/reset', methods=['POST'])
def reset_leads():
    try:
        count = lead_manager.reset_lead_statuses()
        return jsonify({"message": f"Successfully reset {count} leads back to pending."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    session = get_session()
    total = session.query(Lead).count()
    sent = session.query(Lead).filter_by(status=LeadStatus.SENT).count()
    pending = session.query(Lead).filter_by(status=LeadStatus.PENDING).count()
    failed = session.query(Lead).filter_by(status=LeadStatus.FAILED).count()
    session.close()
    return jsonify({
        "total": total,
        "sent": sent,
        "pending": pending,
        "failed": failed
    })

@app.route('/api/test-email', methods=['POST'])
def test_email():
    data = request.json
    target_email = data.get('email')
    if not target_email:
        return jsonify({"error": "Target email is required"}), 400
    
    try:
        # Generate a test email using the AI
        content = orchestrator.ai_agent.generate_email("Test User", "Test Company", "https://example.com")
        
        # Clean and extract
        clean_output = content.replace("```text", "").replace("```markdown", "").replace("```", "").strip()
        
        subject = "Test Email from Sales Agent"
        body = clean_output
        
        if "[SUBJECT]" in clean_output and "[BODY]" in clean_output:
            subject = clean_output.split("[SUBJECT]")[1].split("[BODY]")[0].strip()
            body = clean_output.split("[BODY]")[1].strip()

        # Final cleaning
        sender_name = os.getenv("SENDER_NAME", "Yash Narula")
        body = body.replace("[Your Name]", sender_name).replace("[BODY]", "").strip()
        subject = subject.replace("Subject:", "").replace("[SUBJECT]", "").strip()

        success, message = orchestrator.email_sender.send_email(target_email, subject, body)
        if success:
            return jsonify({"message": f"Test email sent to {target_email}!", "content": body})
        else:
            return jsonify({"error": message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use the port assigned by the cloud provider or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
