from flask import Flask, render_template, request, redirect, url_for, session
from config import db, cursor
import random
from datetime import datetime
from groq import Groq

app = Flask(__name__)
app.secret_key = 'your_secret_key'

f = open("sammyai.txt",'r')
context = f.read()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM doctors WHERE email=%s AND password=%s", (email, password))
        doctor = cursor.fetchone()
        if doctor:
            session['doctor_id'] = doctor[0]
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'doctor_id' in session:
        doctor_id = session['doctor_id']
        cursor.execute("SELECT * FROM appointments WHERE doctor_id=%s", (doctor_id,))
        appointments = cursor.fetchall()
        return render_template('dashboard.html', appointments=appointments)
    return redirect(url_for('login'))

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        dob = request.form['dob']
        gender = request.form['gender']
        mobile = request.form['mobile']
        whatsapp = request.form['whatsapp']
        email = request.form['email']
        appointment_time = datetime.strptime(request.form['appointment_time'], '%Y-%m-%dT%H:%M')

        cursor.execute("SELECT id FROM doctors ORDER BY RAND() LIMIT 1")
        doctor_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO appointments (patient_name, dob, gender, mobile, whatsapp, email, doctor_id, appointment_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (patient_name, dob, gender, mobile, whatsapp, email, doctor_id, appointment_time))
        db.commit()
        return redirect(url_for('index'))
    return render_template('appointment.html')

@app.route('/logout')
def logout():
    session.pop('doctor_id', None)
    return redirect(url_for('index'))
@app.route('/aboutus')
def aboutus():
    return render_template('AboutUS.html')

@app.route('/sammyai', methods=['GET', 'POST'])
def chatbot():
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST' and 'query' in request.form:
        query = request.form.get('query')
        user= f"User Query: {query}, Relevant Information: {context}\n\nPlease answer the user's query based only on the relevant information provided above."
        
        # Initialize the client with the API key
        client = Groq(api_key="YOUR API KEY")

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Respond intelligently by analyzing the provided data. If the information is unrelated to the prompt, tactfully mention that it falls outside the scope of your training."},
                {"role": "user", "content": user}
            ],
            model="llama3-8b-8192",
            max_tokens=100
        )
        result = chat_completion.choices[0].message.content
        
        # Append the query and result to the session history
        session['history'].append({'query': query, 'response': result})
        session.modified = True
        
    return render_template('chatbot.html', history=session['history'])

@app.route('/clear', methods=['POST'])
def clear_history():
    session.pop('history', None)
    return redirect(url_for('chatbot'))

if __name__ == '__main__':
    app.run(debug=True)
