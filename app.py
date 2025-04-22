from flask import Flask, request, session, redirect, url_for, render_template, jsonify, send_file, Response
from flask import request, redirect, url_for, flash, session
from datetime import timedelta, date, datetime
from report import report_bp
from db import get_db  

import mysql.connector
import os
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.permanent_session_lifetime = timedelta(minutes=30)

# ------------------- AUTH ROUTES -------------------

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        db.commit()
        cursor.close()
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (request.form['username'],))
    user = cursor.fetchone()
    if user and user['password'] == request.form['password']:
        session['user_id'] = user['id']
        session['role'] = user['role']
        session.permanent = True
        cursor.close()
        return redirect('/dashboard')
    cursor.close()
    return render_template('login.html', error="Invalid credentials")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ------------------- DASHBOARD REDIRECT -------------------

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    role = session['role']
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'faculty':
        return redirect(url_for('faculty_dashboard'))
    elif role == 'student':
        return redirect(url_for('student_dashboard'))
    return "Unknown role", 400

# ------------------- ADMIN ROUTES -------------------

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'faculty'")
    total_faculty = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'student'")
    total_students = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) AS count FROM subjects")
    total_subjects = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) AS count FROM classes")
    total_classes = cursor.fetchone()['count']
    cursor.close()
    stats = {
        'total_faculty': total_faculty,
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_classes': total_classes
    }
    return render_template('admin/admin_dashboard.html', stats=stats)

@app.route('/admin/manage_faculty')
def manage_faculty():
    return render_template('admin/manage_faculty.html')

@app.route('/admin/manage_students')
def manage_students():
    return render_template('admin/manage_students.html')

@app.route('/admin/manage_subjects')
def manage_subjects():
    return render_template('admin/manage_subjects.html')

@app.route('/admin/manage_classes')
def manage_classes():
    return render_template('admin/manage_classes.html')

@app.route('/admin/reports')
def admin_reports():
    return render_template('admin/admin_reports.html', reports=[])


# Admin POST actions for forms
@app.route('/admin/add_faculty', methods=['POST'])
def add_faculty():
    db = get_db()
    cursor = db.cursor()
    email = request.form['email']
    password = request.form['password']
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'faculty')", (email, password))
    db.commit()
    cursor.close()
    return redirect(url_for('manage_faculty'))
@app.route('/admin/edit_faculty', methods=['POST'])
def edit_faculty():
    db = get_db()
    cursor = db.cursor()

    faculty_id = request.form['faculty_id']
    new_email = request.form.get('new_email')

    if new_email:
        cursor.execute("UPDATE users SET username = %s WHERE id = %s AND role = 'faculty'", (new_email, faculty_id))

    db.commit()
    cursor.close()
    return redirect(url_for('admin/manage_faculty'))

@app.route('/admin/delete_faculty', methods=['POST'])
def deleccite_faculty():
    db = get_db()
    cursor = db.cursor()

    faculty_id = request.form['faculty_id']
    cursor.execute("DELETE FROM classes WHERE faculty_id = %s", (faculty_id,))
    cursor.execute("DELETE FROM users WHERE id = %s AND role = 'faculty'", (faculty_id,))

    db.commit()
    cursor.close()
    return redirect(url_for('admin/manage_faculty'))

@app.route('/admin/enroll_student', methods=['POST'])
def enroll_student_admin():
    db = get_db()
    cursor = db.cursor()
    email = request.form['email']
    password = request.form['password']
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'student')", (email, password))
    db.commit()
    cursor.close()
    return redirect(url_for('admin/manage_students'))

@app.route('/admin/edit_student', methods=['POST'])
def edit_student():
    db = get_db()
    cursor = db.cursor()

    student_id = request.form['student_id']
    new_email = request.form.get('new_email')
    new_class = request.form.get('new_class')

    if new_email:
        cursor.execute("UPDATE users SET username = %s WHERE id = %s", (new_email, student_id))

    if new_class:
        cursor.execute("UPDATE enrollments SET class_id = %s WHERE student_id = %s", (new_class, student_id))

    db.commit()
    cursor.close()
    return redirect(url_for('admin/manage_students'))

@app.route('/admin/delete_student', methods=['POST'])
def delete_student():
    db = get_db()
    cursor = db.cursor()

    student_id = request.form['student_id']
    cursor.execute("DELETE FROM enrollments WHERE student_id = %s", (student_id,))
    cursor.execute("DELETE FROM users WHERE id = %s AND role = 'student'", (student_id,))

    db.commit()
    cursor.close()
    return redirect(url_for('admin/manage_students'))


@app.route('/admin/add_subject', methods=['POST'])
def add_subject():
    db = get_db()
    cursor = db.cursor()
    name = request.form['name']
    code = request.form['code']
    cursor.execute("INSERT INTO subjects (name, code, description) VALUES (%s, %s, '')", (name, code))
    db.commit()
    cursor.close()
    return redirect(url_for('admin/manage_subjects'))

@app.route('/admin/delete_subject', methods=['POST'])
def delete_subject():
    db = get_db()
    cursor = db.cursor()

    subject_id = request.form['subject_id']
    cursor.execute("DELETE FROM classes WHERE subject_id = %s", (subject_id,))
    cursor.execute("DELETE FROM subjects WHERE id = %s", (subject_id,))

    db.commit()
    cursor.close()
    return redirect(url_for('admin/manage_subjects'))


@app.route('/admin/create_class', methods=['POST'])
def create_class():
    db = get_db()
    cursor = db.cursor()
    subject_id = request.form['subject_id']
    faculty_id = request.form['faculty_id']
    room = request.form['room']
    schedule = request.form['schedule']
    cursor.execute("INSERT INTO classes (subject_id, faculty_id, room_number, schedule) VALUES (%s, %s, %s, %s)", (subject_id, faculty_id, room, schedule))
    db.commit()
    cursor.close()
    return redirect(url_for('admin/manage_classes'))

@app.route('/admin/delete_class', methods=['POST'])
def delete_class():
    db = get_db()
    cursor = db.cursor()

    class_id = request.form['class_id']
    cursor.execute("DELETE FROM enrollments WHERE class_id = %s", (class_id,))
    cursor.execute("DELETE FROM classes WHERE id = %s", (class_id,))

    db.commit()
    cursor.close()
    return redirect(url_for('admin/manage_classes'))

@app.route('/admin/review_requests')
def review_requests():
    if session.get('role') != 'admin':
        return redirect('/')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT ar.*, u.username 
        FROM absence_requests ar
        JOIN users u ON ar.student_id = u.id
        WHERE ar.status = 'pending'
        ORDER BY ar.date DESC
    """)
    requests = cursor.fetchall()
    cursor.close()
    return render_template('admin/review_requests.html', requests=requests)


@app.route('/admin/request/<int:request_id>/approve', methods=['POST'])
def approve_request(request_id):
    if session.get('role') != 'admin':
        return redirect('/')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE absence_requests SET status = 'approved' WHERE id = %s", (request_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('review_requests'))

@app.route('/admin/request/<int:request_id>/reject', methods=['POST'])
def reject_request(request_id):
    if session.get('role') != 'admin':
        return redirect('/')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE absence_requests SET status = 'rejected' WHERE id = %s", (request_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('review_requests'))

# ------------------- FACULTY ROUTES -------------------

@app.route('/faculty/dashboard', methods=['GET', 'POST'])
def faculty_dashboard():
    if session.get('role') != 'faculty':
        return redirect('/')

    faculty_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.id, s.name AS subject_name,
               ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)/COUNT(a.id)*100, 2) AS attendance_percent
        FROM subjects s
        JOIN classes c ON s.id = c.subject_id
        LEFT JOIN attendance a ON c.id = a.class_id
        WHERE c.faculty_id = %s
        GROUP BY s.id, s.name
    """, (faculty_id,))
    subjects = cursor.fetchall()

    today = date.today().strftime('%A')
    cursor.execute("""
        SELECT s.name AS subject_name, c.room_number, c.schedule
        FROM classes c
        JOIN subjects s ON c.subject_id = s.id
        WHERE c.faculty_id = %s AND c.schedule LIKE %s
    """, (faculty_id, f"%{today}%"))
    todays_classes = cursor.fetchall()

    cursor.execute("""
        SELECT c.id, s.name AS subject_name, c.room_number, c.schedule
        FROM classes c
        JOIN subjects s ON c.subject_id = s.id
        WHERE c.faculty_id = %s
    """, (faculty_id,))
    available_classes = cursor.fetchall()

    cursor.close()
    return render_template("faculty/faculty_dashboard.html",
                           subjects=subjects,
                           todays_classes=todays_classes,
                           available_classes=available_classes)

@app.route('/faculty/subjects')
def get_faculty_subjects():
    if session.get('role') != 'faculty':
        return redirect('/')
        
    faculty_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
    SELECT s.id, s.name, s.code 
    FROM subjects s
    JOIN classes c ON s.id = c.subject_id
    WHERE c.faculty_id = %s
    GROUP BY s.id, s.name, s.code
    """, (faculty_id,))
    
    subjects = cursor.fetchall()
    cursor.close()
    
    return jsonify(subjects)

@app.route('/faculty/class/<int:class_id>')
def get_class_details(class_id):
    if session.get('role') != 'faculty':
        return redirect('/')
        
    faculty_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
    SELECT c.id, s.name as subject_name, c.room_number, c.schedule 
    FROM classes c
    JOIN subjects s ON c.subject_id = s.id
    WHERE c.id = %s AND c.faculty_id = %s
    """, (class_id, faculty_id))
    
    class_details = cursor.fetchone()
    cursor.close()
    
    if not class_details:
        return jsonify({"error": "Class not found or not authorized"}), 404
        
    return jsonify(class_details)

@app.route('/faculty/class/<int:class_id>/students')
def get_class_students(class_id):
    if session.get('role') != 'faculty':
        return redirect('/')
        
    faculty_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # First verify the faculty has access to this class
    cursor.execute("SELECT id FROM classes WHERE id = %s AND faculty_id = %s", 
                  (class_id, faculty_id))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Unauthorized access"}), 403
    
    cursor.execute("""
    SELECT s.id, s.roll_number, s.name
    FROM students s
    JOIN class_students cs ON s.id = cs.student_id
    WHERE cs.class_id = %s
    ORDER BY s.roll_number
    """, (class_id,))
    
    students = cursor.fetchall()
    cursor.close()
    
    return jsonify(students)

@app.route('/faculty/attendance/<int:class_id>/<date>')
def get_attendance(class_id, date):
    if session.get('role') != 'faculty':
        return redirect('/')
        
    faculty_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # First verify the faculty has access to this class
    cursor.execute("SELECT id FROM classes WHERE id = %s AND faculty_id = %s", 
                  (class_id, faculty_id))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Unauthorized access"}), 403
    
    cursor.execute("""
    SELECT a.id, s.id as student_id, s.roll_number, s.name, a.status
    FROM students s
    JOIN class_students cs ON s.id = cs.student_id
    LEFT JOIN attendance a ON s.id = a.student_id AND a.class_id = %s AND a.date = %s
    WHERE cs.class_id = %s
    ORDER BY s.roll_number
    """, (class_id, date, class_id))
    
    attendance_data = cursor.fetchall()
    cursor.close()
    
    return jsonify(attendance_data)

@app.route('/faculty/add_subject', methods=['POST'])
def add_subject_faculty():
    if session.get('role') != 'faculty':
        return redirect('/')
    
    faculty_id = session['user_id']
    
    try:
        # Get form data
        subject_name = request.form.get('subject_name')
        code = request.form.get('code')
        branch = request.form.get('branch')
        room_number = request.form.get('class_number')
        schedule = request.form.get('schedule')
        
        # Validate required fields
        if not all([subject_name, code, branch, room_number, schedule]):
            flash('All fields are required', 'error')
            return redirect(url_for('faculty_dashboard'))
        
        # Connect to database
        db = get_db()
        cursor = db.cursor()
        
        # First, insert the subject
        cursor.execute(
            """INSERT INTO subjects (name) VALUES (%s)""",
            (subject_name,)
        )
        subject_id = cursor.lastrowid
        
        # Then, insert the class with this subject
        cursor.execute(
            """INSERT INTO classes 
               (subject_id, faculty_id, room_number, schedule) 
               VALUES (%s, %s, %s, %s)""", 
            (subject_id, faculty_id, room_number, schedule)
        )
        
        # Save changes
        db.commit()
        cursor.close()
        
        flash('Subject added successfully', 'success')
    except Exception as e:
        print(f"Error adding subject: {str(e)}")
        flash('Error adding subject. Please try again.', 'error')
    
    return redirect(url_for('faculty_dashboard'))

@app.route('/faculty/classes/<int:subject_id>')
def get_classes_for_subject(subject_id):
    faculty_id = session.get('user_id')
    if session.get('role') != 'faculty':
        return redirect('/')
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, room_number, schedule 
        FROM classes 
        WHERE subject_id = %s AND faculty_id = %s
    """, (subject_id, faculty_id))
    classes = cursor.fetchall()
    cursor.close()
    return jsonify(classes)

# Mark attendance route
@app.route('/faculty/mark_attendance')
def mark_attendance():
    class_id = request.args.get('class_id')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get subject information
    if class_id:
        cursor.execute("""
            SELECT s.name, s.branch, c.schedule 
            FROM classes c
            JOIN subjects s ON c.subject_id = s.id
            WHERE c.id = %s
        """, (class_id,))
        subject = cursor.fetchone()
    else:
        subject = None
    
    # Get students for this class if the class is selected
    students = []
    if class_id:
        cursor.execute("""
            SELECT s.id, s.name, s.roll_number
            FROM students s
            JOIN class_students cs ON s.id = cs.student_id
            WHERE cs.class_id = %s
            ORDER BY s.roll_number
        """, (class_id,))
        students = cursor.fetchall()
    
    cursor.close()
    return render_template('faculty/mark_attendance.html', subject=subject, students=students, class_id=class_id)

# API endpoints for attendance operations
@app.route('/api/faculty/class/add_student', methods=['POST'])
def add_student_to_class():
    if session.get('role') != 'faculty':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        student_name = request.form.get('student_name')
        roll_number = request.form.get('roll_number')
        class_id = request.form.get('class_id')
        
        if not all([student_name, roll_number, class_id]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        db = get_db()
        cursor = db.cursor()
        
        # First, add or get the student
        cursor.execute("SELECT id FROM students WHERE roll_number = %s", (roll_number,))
        student = cursor.fetchone()
        
        if student:
            student_id = student[0]
        else:
            # Insert new student
            cursor.execute("INSERT INTO students (name, roll_number) VALUES (%s, %s)", 
                          (student_name, roll_number))
            student_id = cursor.lastrowid
        
        # Then, link the student to the class if not already linked
        cursor.execute("SELECT id FROM class_students WHERE student_id = %s AND class_id = %s",
                      (student_id, class_id))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO class_students (student_id, class_id) VALUES (%s, %s)", 
                          (student_id, class_id))
        
        db.commit()
        cursor.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error adding student: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/faculty/attendance/save', methods=['POST'])
def save_attendance():
    if session.get('role') != 'faculty':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        class_id = request.form.get('class_id')
        attendance_date = request.form.get('attendance_date')
        student_ids = request.form.getlist('student_ids[]')
        
        db = get_db()
        cursor = db.cursor()
        
        # Delete existing attendance records for this class and date
        cursor.execute("""
            DELETE FROM attendance 
            WHERE class_id = %s AND date = %s
        """, (class_id, attendance_date))
        
        # Insert new attendance records
        for student_id in student_ids:
            status = 'present' if request.form.get(f'student_{student_id}') == 'present' else 'absent'
            cursor.execute("""
                INSERT INTO attendance (student_id, class_id, date, status)
                VALUES (%s, %s, %s, %s)
            """, (student_id, class_id, attendance_date, status))
        
        db.commit()
        cursor.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error saving attendance: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/faculty/save_attendance', methods=['POST'])
def save_bulk_attendance():
    if session.get('role') != 'faculty':
        return redirect('/')

    subject_id = request.form['subject_id']
    attendance_date = request.form.get('attendance_date', date.today().strftime('%Y-%m-%d'))
    present_ids = request.form.getlist('present_ids[]')
    faculty_id = session['user_id']

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get class ID for this subject
    cursor.execute("SELECT id FROM classes WHERE subject_id = %s AND faculty_id = %s LIMIT 1", 
                   (subject_id, faculty_id))
    class_row = cursor.fetchone()
    
    if not class_row:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Invalid class selected'})
        return redirect(url_for('faculty_dashboard'))
        
    class_id = class_row['id']
    
    try:
        # Get all students for this class
        cursor.execute("""
            SELECT s.id
            FROM students s
            JOIN class_students cs ON s.id = cs.student_id
            WHERE cs.class_id = %s
        """, (class_id,))
        all_students = [row['id'] for row in cursor.fetchall()]
        
        # First, remove any existing attendance records for this date and subject
        cursor.execute("""
            DELETE FROM attendance 
            WHERE subject_id = %s AND date = %s
        """, (subject_id, attendance_date))
        
        # Insert present records
        for student_id in present_ids:
            if student_id and int(student_id) in all_students:
                cursor.execute("""
                    INSERT INTO attendance 
                    (class_id, subject_id, student_id, date, status, marked_by)
                    VALUES (%s, %s, %s, %s, 'present', %s)
                """, (class_id, subject_id, student_id, attendance_date, faculty_id))
        
        # Insert absent records
        for student_id in all_students:
            if str(student_id) not in present_ids:
                cursor.execute("""
                    INSERT INTO attendance 
                    (class_id, subject_id, student_id, date, status, marked_by)
                    VALUES (%s, %s, %s, %s, 'absent', %s)
                """, (class_id, subject_id, student_id, attendance_date, faculty_id))

        db.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        return redirect(url_for('mark_attendance', subject_id=subject_id, date=attendance_date))
    
    except Exception as e:
        db.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)})
        return f"Error saving attendance: {str(e)}", 500
    finally:
        db.close()



@app.route('/faculty/add_student_to_subject', methods=['POST'])
def add_student_to_subject():
    if session.get('role') != 'faculty':
        return redirect('/')
        
    subject_id = request.form['subject_id']
    name = request.form['student_name']
    roll_number = request.form['roll_number']
    attendance_date = request.form.get('attendance_date', date.today().strftime('%Y-%m-%d'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get class ID for this subject
    cursor.execute("SELECT id FROM classes WHERE subject_id = %s AND faculty_id = %s LIMIT 1", 
                   (subject_id, session['user_id']))
    class_row = cursor.fetchone()
    
    if not class_row:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Invalid class selected'})
        return redirect(url_for('faculty_dashboard'))
        
    class_id = class_row['id']
    
    try:
        # Check if student already exists
        cursor.execute("SELECT id FROM students WHERE roll_number = %s", (roll_number,))
        student_row = cursor.fetchone()
        
        if student_row:
            student_id = student_row['id']
        else:
            # Create new student
            cursor.execute("INSERT INTO students (name, roll_number) VALUES (%s, %s)", (name, roll_number))
            db.commit()
            student_id = cursor.lastrowid
        
        # Add student to class if not already added
        cursor.execute("INSERT IGNORE INTO class_students (class_id, student_id) VALUES (%s, %s)", 
                       (class_id, student_id))
        db.commit()
        
        # Get all students for this subject including the new one
        cursor.execute("""
            SELECT s.id, s.name, s.roll_number 
            FROM students s
            JOIN class_students cs ON s.id = cs.student_id
            JOIN classes c ON cs.class_id = c.id
            WHERE c.subject_id = %s AND c.faculty_id = %s
        """, (subject_id, session['user_id']))
        all_students = cursor.fetchall()
        
        # Get students marked present for selected date
        cursor.execute("""
            SELECT student_id
            FROM attendance
            WHERE subject_id = %s AND date = %s AND status = 'present'
        """, (subject_id, attendance_date))
        present_students = [row['student_id'] for row in cursor.fetchall()]
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_template('faculty/partials/student_list.html', 
                                  students=all_students, 
                                  present_students=present_students)
            return jsonify({'success': True, 'html': html})
        
        return redirect(url_for('mark_attendance', subject_id=subject_id, date=attendance_date))
    
    except Exception as e:
        db.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)})
        return f"Error adding student: {str(e)}", 500
    finally:
        db.close()

@app.route('/faculty/download_report')
def download_report():
    if session.get('role') != 'faculty':
        return redirect('/')
        
    subject_id = request.args.get('subject_id')
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    format_type = request.args.get('format', 'csv')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get subject name
    cursor.execute("SELECT name FROM subjects WHERE id = %s", (subject_id,))
    subject_row = cursor.fetchone()
    if not subject_row:
        return "Subject not found", 404
    
    subject_name = subject_row['name']
    
    # Get attendance data
    cursor.execute("""
        SELECT s.name, s.roll_number, a.status
        FROM students s
        JOIN attendance a ON s.id = a.student_id
        WHERE a.subject_id = %s AND a.date = %s
        ORDER BY s.roll_number
    """, (subject_id, selected_date))
    attendance_data = cursor.fetchall()
    cursor.close()
    
    if format_type == 'csv':
        # Create CSV in memory
        output = io.StringIO()
        output.write(f"Attendance Report - {subject_name} - {selected_date}\n")
        output.write("Roll Number,Student Name,Status\n")
        
        for row in attendance_data:
            output.write(f"{row['roll_number']},{row['name']},{row['status']}\n")
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=attendance_{subject_name}_{selected_date}.csv"}
        )
    
    elif format_type == 'pdf':
        # This would require a PDF library, but we'll return a placeholder for now
        return "PDF generation functionality will be implemented", 501
    
    return "Invalid format specified", 400

@app.route('/faculty/reports')
def faculty_reports():
    if session.get('role') != 'faculty':
        return redirect('/')

    faculty_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT DISTINCT s.name 
        FROM subjects s
        JOIN classes c ON s.id = c.subject_id
        WHERE c.faculty_id = %s
    """, (faculty_id,))
    subjects = [row['name'] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT MONTHNAME(date) AS month FROM attendance ORDER BY date DESC")
    months = [row['month'] for row in cursor.fetchall()]

    selected_subject = request.args.get('subject')
    selected_month = request.args.get('month')

    attendance_summary = []
    if selected_subject and selected_month:
        query = """
            SELECT a.date, COUNT(*) AS total_marked,
                   SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_count
            FROM attendance a
            JOIN classes c ON a.class_id = c.id
            JOIN subjects s ON c.subject_id = s.id
            WHERE s.name = %s AND MONTHNAME(a.date) = %s AND c.faculty_id = %s
            GROUP BY a.date
            ORDER BY a.date
        """
        cursor.execute(query, (selected_subject, selected_month, faculty_id))
        attendance_summary = cursor.fetchall()

    cursor.close()
    return render_template('faculty/reports.html',
                           subjects=subjects,
                           months=months,
                           selected_subject=selected_subject,
                           selected_month=selected_month,
                           attendance_summary=attendance_summary)

# ------------------- STUDENT ROUTES -------------------

@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect('/')

    student_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get subjects and attendance information
    cursor.execute("""
        SELECT s.id, s.name AS subject_name, s.code, s.branch, c.schedule,
               ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS attendance_percent
        FROM enrollments e
        JOIN classes c ON e.class_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        LEFT JOIN attendance a ON a.class_id = c.id AND a.student_id = e.student_id
        WHERE e.student_id = %s
        GROUP BY s.name, s.id, s.code, s.branch, c.schedule
    """, (student_id,))
    subjects = cursor.fetchall()
    
    # Calculate average attendance
    avg_attendance = 0
    if subjects:
        total_percent = sum(subject['attendance_percent'] or 0 for subject in subjects)
        avg_attendance = total_percent / len(subjects)
    
    # Get total classes
    cursor.execute("""
        SELECT COUNT(DISTINCT c.id) as total
        FROM enrollments e
        JOIN classes c ON e.class_id = c.id
        WHERE e.student_id = %s
    """, (student_id,))
    result = cursor.fetchone()
    total_classes = result['total'] if result else 0
    
    # Get recent absences
    cursor.execute("""
        SELECT date, reason, status
        FROM absence_requests
        WHERE student_id = %s
        ORDER BY date DESC
        LIMIT 5
    """, (student_id,))
    recent_absences = cursor.fetchall()
    
    cursor.close()

    return render_template('student_dashboard.html', 
                          subjects=subjects, 
                          avg_attendance=avg_attendance,
                          total_classes=total_classes,
                          recent_absences=recent_absences)

@app.route('/student/absence_requests', methods=['GET', 'POST'])
def absence_requests():
    if session.get('role') != 'student':
        return redirect('/')

    student_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor

    if request.method == 'POST':
        reason = request.form['reason']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        if not reason or not start_date or not end_date:
            return "Missing required fields", 400

        # Insert one row per day of absence
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        while current <= end:
            cursor.execute("""
                INSERT INTO absence_requests (student_id, reason, date, status)
                VALUES (%s, %s, %s, 'pending')
            """, (student_id, reason, current.date()))
            current += timedelta(days=1)

        db.commit()
        
        # Redirect with success parameter
        return redirect(url_for('absence_requests', success=True))
    
    # Get all absence requests
    cursor.execute("""
        SELECT date, reason, status
        FROM absence_requests
        WHERE student_id = %s
        ORDER BY date DESC
    """, (student_id,))
    absence_requests = cursor.fetchall()
    
    cursor.close()
    return render_template('absence_requests.html', absence_requests=absence_requests)


# ------------------- MAIN -------------------
app.register_blueprint(report_bp, url_prefix='/reports')

if __name__ == '__main__':
    app.run(debug=True)