# report.py
from flask import Blueprint, request, session, send_file
from datetime import datetime
import pandas as pd  
import io
from fpdf import FPDF
from db import get_db


report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/faculty/download_attendance_report')
def download_attendance_report():
    if 'user_id' not in session or session.get('role') != 'faculty':
        return "Unauthorized", 403

    faculty_id = session.get('user_id')
    format = request.args.get('format', 'csv')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    if not from_date or not to_date:
        return "Missing date range", 400

    try:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format", 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.name AS subject, c.room_number, a.date,
               st.roll_number, st.name, a.status
        FROM attendance a
        JOIN classes c ON a.class_id = c.id
        JOIN subjects s ON c.subject_id = s.id
        JOIN students st ON a.student_id = st.id
        WHERE c.faculty_id = %s AND a.date BETWEEN %s AND %s
        ORDER BY a.date DESC
    """, (faculty_id, from_dt.date(), to_dt.date()))

    rows = cursor.fetchall()
    df = pd.DataFrame(rows)

    # Export to CSV
    if format == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name='attendance.csv')

    # Export to Excel
    elif format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance')
        output.seek(0)
        return send_file(output,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True,
                         download_name='attendance.xlsx')

    # Export to PDF
    elif format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Attendance Report", ln=True, align="C")
        pdf.ln(10)

        for _, row in df.iterrows():
            line = f"{row['date']} | {row['subject']} | {row['room_number']} | {row['roll_number']} - {row['name']} - {row['status'].capitalize()}"
            pdf.multi_cell(0, 10, line)

        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        return send_file(pdf_output,
                         mimetype='application/pdf',
                         as_attachment=True,
                         download_name='attendance.pdf')

    return "Unsupported format", 400
