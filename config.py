import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sam@130201",
    database="hospital_management"
)

cursor = db.cursor()
