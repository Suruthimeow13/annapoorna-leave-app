from flask import Flask, render_template, request
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# 🟢 Twilio Setup
import os

account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = 'whatsapp:+14155238886'  # Twilio Sandbox Number
manager_number = 'whatsapp:+919444882821'  # Replace with manager's number

client = Client(account_sid, auth_token)

# 🔵 Store leave requests in memory for now
leave_requests = []

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    # 🔹 Get form data
    data = {
        'name': request.form['name'],
        'employee_id': request.form['employee_id'],
        'phone': request.form['phone'],
        'start_date': request.form['start_date'],
        'end_date': request.form['end_date'],
        'reason': request.form['reason'],
        'status': 'Pending'
    }

    # 🔹 Store data
    leave_requests.append(data)

    # 🔹 WhatsApp message to manager

    dashboard_url = 'https://opposed-ul-submissions-logistics.trycloudflare.com/manager'

    message = f"""📩 *Leave Request from {data['name']}*
🆔 ID: {data['employee_id']}
📱 Phone: {data['phone']}
🗓️ {data['start_date']} to {data['end_date']}
📝 Reason: {data['reason']}
Status: {data['status']}

🔗 Approve/Reject: {dashboard_url}
"""

    client.messages.create(
        from_=twilio_number,
        to=manager_number,
        body=message
    )

    return "Leave request submitted. Manager notified via WhatsApp!"

from flask import redirect

@app.route('/manager')
def manager():
    return render_template('manager.html', requests=leave_requests)

@app.route('/action', methods=['POST'])
def action():
    idx = int(request.form['id'])
    decision = request.form['decision']
    comment = request.form['comment']

    # ✅ Update the leave request
    leave_requests[idx]['status'] = decision
    leave_requests[idx]['manager_comment'] = comment

    # ✅ Send WhatsApp to employee
    emp_name = leave_requests[idx]['name']
    start = leave_requests[idx]['start_date']
    end = leave_requests[idx]['end_date']
    phone = leave_requests[idx]['phone']  # Already stored as +91xxxxxxx

    msg = f"""Hi {emp_name},
Your leave request from {start} to {end} has been *{decision}*.
Manager Comment: {comment if comment else 'No comment.'}"""

    print("Sending to employee:", phone)

    try:
        client.messages.create(
            from_=twilio_number,
            to='whatsapp:' + phone,
            body=msg
        )
        print("Message sent successfully.")
    except Exception as e:
        print("Failed to send message:", e)

    return redirect('/manager')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
