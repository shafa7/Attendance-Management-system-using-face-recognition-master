import tkinter as tk
from tkinter import *
import os
import cv2
import time
import datetime
import pandas as pd
import tkinter.ttk as tkk
import tkinter.font as font
from PIL import Image, ImageTk


# Define paths
base_path = os.path.dirname(os.path.abspath(__file__))
haarcasecade_path = os.path.join(base_path, "haarcascade_frontalface_default.xml")
trainimagelabel_path = os.path.join(base_path, "TrainingImageLabel", "Trainner.yml")
trainimage_path = os.path.join(base_path, "TrainingImage")
studentdetail_path = os.path.join(base_path, "StudentDetails", "studentdetails.csv")
attendance_path = os.path.join(base_path, "Attendance")

# Ensure Attendance directory exists
os.makedirs(attendance_path, exist_ok=True)


# Function for subject selection and attendance filling
def subjectChoose(text_to_speech):
    def fillAttendance():
        sub = tx.get().strip()
        if not sub:
            t = "Please enter the subject name!"
            text_to_speech(t)
            return

        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            if not os.path.exists(trainimagelabel_path):
                error_message = "Model not found. Please train the model first."
                Notifica.configure(
                    text=error_message,
                    bg="black",
                    fg="yellow",
                    width=33,
                    font=("times", 15, "bold"),
                )
                Notifica.place(x=20, y=250)
                text_to_speech(error_message)
                return

            recognizer.read(trainimagelabel_path)
            face_cascade = cv2.CascadeClassifier(haarcasecade_path)
            if not os.path.exists(studentdetail_path):
                raise FileNotFoundError("Student details file not found!")

            df = pd.read_csv(studentdetail_path)
            cam = cv2.VideoCapture(0)
            font = cv2.FONT_HERSHEY_SIMPLEX
            col_names = ["Enrollment", "Name"]
            attendance = pd.DataFrame(columns=col_names)
            timeout = time.time() + 20  # 20-second timeout

            while True:
                ret, im = cam.read()
                if not ret:
                    raise Exception("Camera could not capture the image.")

                gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.2, 5)
                for (x, y, w, h) in faces:
                    Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                    if conf < 70:
                        ts = time.time()
                        aa = df.loc[df["Enrollment"] == Id]["Name"].values
                        tt = f"{Id}-{aa[0] if len(aa) > 0 else 'Unknown'}"
                        attendance.loc[len(attendance)] = [Id, aa[0] if len(aa) > 0 else "Unknown"]
                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(im, str(tt), (x, y - 10), font, 0.75, (255, 255, 255), 2)
                    else:
                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(im, "Unknown", (x, y - 10), font, 0.75, (0, 0, 255), 2)

                if time.time() > timeout:
                    break

                attendance = attendance.drop_duplicates(subset=["Enrollment"], keep="first")
                cv2.imshow("Filling Attendance...", im)
                if cv2.waitKey(30) & 0xFF == 27:
                    break

            cam.release()
            cv2.destroyAllWindows()

            # Save attendance to file
            subject_path = os.path.join(attendance_path, sub)
            os.makedirs(subject_path, exist_ok=True)
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            timestamp = datetime.datetime.now().strftime("%H-%M-%S")
            file_name = os.path.join(subject_path, f"{sub}_{date}_{timestamp}.csv")
            attendance.to_csv(file_name, index=False)

            message = f"Attendance filled successfully for {sub}."
            Notifica.configure(
                text=message,
                bg="black",
                fg="yellow",
                width=33,
                relief=RIDGE,
                bd=5,
                font=("times", 15, "bold"),
            )
            Notifica.place(x=20, y=250)
            text_to_speech(message)

        except Exception as e:
            error_message = f"Error: {e}"
            print(error_message)
            text_to_speech(error_message)
            cv2.destroyAllWindows()

    def openAttendanceFolder():
        sub = tx.get().strip()
        if not sub:
            t = "Please enter the subject name!"
            text_to_speech(t)
            return

        subject_path = os.path.join(attendance_path, sub)
        if os.path.exists(subject_path):
            os.startfile(subject_path)
        else:
            t = f"No attendance folder found for subject '{sub}'!"
            text_to_speech(t)

    # Subject chooser UI
    subject = Tk()
    subject.title("Subject Selection")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    titl = tk.Label(subject, text="Enter the Subject Name", bg="black", fg="green", font=("arial", 25))
    titl.pack(pady=10)

    Notifica = tk.Label(
        subject, text="", bg="yellow", fg="black", width=33, height=2, font=("times", 15, "bold")
    )

    sub_label = tk.Label(
        subject,
        text="Enter Subject",
        width=10,
        height=2,
        bg="black",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 15),
    )
    sub_label.place(x=50, y=100)

    tx = tk.Entry(
        subject,
        width=15,
        bd=5,
        bg="black",
        fg="yellow",
        relief=RIDGE,
        font=("times", 30, "bold"),
    )
    tx.place(x=190, y=100)

    fill_button = tk.Button(
        subject,
        text="Fill Attendance",
        command=fillAttendance,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    fill_button.place(x=195, y=170)

    check_button = tk.Button(
        subject,
        text="Check Sheets",
        command=openAttendanceFolder,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=10,
        relief=RIDGE,
    )
    check_button.place(x=360, y=170)

    subject.mainloop()
