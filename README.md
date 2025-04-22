# AttendanceMarkingSystem
This web-based  System is designed for schools and colleges to streamline the process of recording and managing student attendance. It includes role-based dashboards. The system is built using Flask, MySQL, HTML/CSS, and Alpine.js for interactivity.

Features
Admin dashboard for managing students, faculty, subjects, classes, and reviewing absence requests
Faculty dashboard for creating subjects/classes, marking attendance, and downloading reports
Student dashboard to view attendance history and submit absence requests
Attendance reports downloadable in CSV and PDF formats
Responsive interface with Alpine.js and sidebar navigation

Prerequisites
Before running the project, ensure the following tools are installed:
Python 3.8 or higher
Flask
XAMPP or MySQL server
MySQL Connector for Python

To install the connector:
pip install mysql-connector-python

Setup Instructions:
1. Clone the Repository
git clone https://github.com/yourusername/attendance-management-system.git
cd attendance-management-system

3. Start MySQL Server
Open XAMPP Control Panel
Start Apache and MySQL

4. Create the Database
Open phpMyAdmin (http://localhost/phpmyadmin)
Create a new database named: attendance_db
Import the provided SQL file or manually create the necessary tables:
students, faculty, admin, subjects, classes, class_students, attendance, absence_requests, etc.
If needed, you can request the full SQL schema.

5. Configure Database in app.py
Edit the configuration inside app.py:
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Default for XAMPP is empty
    'database': 'attendance_db'
}

6. Run the Application
python app.py
Open your browser and go to:
http://localhost:5000
Project Structure: 
/static
    /alpine.min.js
    /style.css
/templates
    /admin/
    /faculty/
    /student/
app.py
README.md
Output:

![Screenshot 2025-04-22 143040](https://github.com/user-attachments/assets/888c215d-d465-4e49-9d32-5216bd4f53cc)
![Screenshot 2025-04-22 145015](https://github.com/user-attachments/assets/af869730-1975-4208-9038-d8893bba1583)
![Screenshot 2025-04-22 145006](https://github.com/user-attachments/assets/058eecef-b341-4989-821e-c191e5ea9587)
![Screenshot 2025-04-22 145000](https://github.com/user-attachments/assets/912898db-0cdd-4a04-97ab-190eadd25259)
![Screenshot 2025-04-22 144955](https://github.com/user-attachments/assets/0d2f72da-6b61-48c9-a081-8efabaad5467)
![Screenshot 2025-04-22 144941](https://github.com/user-attachments/assets/31fac80b-fbd8-426a-9ee2-4398d19affbe)
![Screenshot 2025-04-22 144933](https://github.com/user-attachments/assets/66d0baac-6c96-4a25-bcd7-d52a91b54cd4)
![Screenshot 2025-04-22 143232](https://github.com/user-attachments/assets/e8271139-d96b-44ca-ac68-0d5df7d0ae8b)
![Screenshot 2025-04-22 143225](https://github.com/user-attachments/assets/a29b150c-1c00-4b7f-92aa-f3c789d420d0)
![Screenshot 2025-04-22 143212](https://github.com/user-attachments/assets/22f732e8-e54d-48ef-bacc-24f79112dc6a)
![Screenshot 2025-04-22 143156](https://github.com/user-attachments/assets/dab4901d-13b7-4d66-98c6-8a1d2c2af09a)
![Screenshot 2025-04-22 143133](https://github.com/user-attachments/assets/398a6c6c-adae-4436-84ff-a677c10a2a64)
![Screenshot 2025-04-22 143123](https://github.com/user-attachments/assets/697d49fa-cd96-4034-a711-936fb7326a42)
![Screenshot 2025-04-22 143115](https://github.com/user-attachments/assets/e25125e3-4dac-44c6-ae2c-9c2c60627abe)
![Screenshot 2025-04-22 143109](https://github.com/user-attachments/assets/f6cd878f-ef4b-4f7e-a70a-d6c0e31e6732)
![Screenshot 2025-04-22 143048](https://github.com/user-attachments/assets/ffccda2e-937b-488d-9635-48447b3e378e)
![Screenshot 2025-04-22 145125](https://github.com/user-attachments/assets/9c877c13-383b-470a-ac75-eace825a9216)
![Screenshot 2025-04-22 145102](https://github.com/user-attachments/assets/872117c2-6e6a-4a24-951f-4c0b068e339b)
![Screenshot 2025-04-22 145055](https://github.com/user-attachments/assets/20651c11-f5ce-4515-8a9f-d9ea957cefa8)
