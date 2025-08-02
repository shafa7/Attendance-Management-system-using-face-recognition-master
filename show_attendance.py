import pandas as pd
import os
import tkinter as tk
from tkinter import *
from glob import glob
import csv

def subjectchoose(text_to_speech):
    def calculate_attendance():
        Subject = tx.get().strip()
        
        if Subject == "":
            message = 'Please enter the subject name.'
            text_to_speech(message)
            return
        
        subject_path = os.path.join("Attendance", Subject)
        
        if not os.path.exists(subject_path):
            message = f"No attendance folder found for subject: {Subject}"
            text_to_speech(message)
            return
        
        os.chdir(subject_path)
        print(f"Looking for files with pattern: {Subject}*.csv")
        filenames = glob(f"{Subject}*.csv") 
        print(f"Found files: {filenames}")


        if not filenames:
            message = f"No attendance files found for subject: {Subject}"
            text_to_speech(message)
            return

        print(f"Found files: {filenames}")  # Debug print
        
        # Merge all attendance CSVs into one DataFrame
        df_list = [pd.read_csv(f) for f in filenames]
        newdf = df_list[0]

        # Debug: print first few rows to ensure data is loaded properly
        print("Initial DataFrame:")
        print(newdf.head())

        for i in range(1, len(df_list)):
            newdf = pd.merge(newdf, df_list[i], how="outer", on=["Enrollment", "Name"])

        # Debug: print column types to check if they're numeric
        print("Column types after merge:")
        print(newdf.dtypes)

        newdf.fillna(0, inplace=True)

        # Select numeric columns for attendance calculation
        attendance_columns = newdf.columns[2:]  # Exclude 'Enrollment' and 'Name'

        # Convert the attendance columns to numeric, forcing errors to NaN
        newdf[attendance_columns] = newdf[attendance_columns].apply(pd.to_numeric, errors='coerce')

        # Calculate attendance as the mean of the numeric columns
        newdf["Attendance"] = newdf[attendance_columns].mean(axis=1).round(2) * 100

        # Debug: print the final DataFrame before saving
        print("Final DataFrame with Attendance:")
        print(newdf.head())

        # Save combined attendance data to a new CSV
        newdf.to_csv("attendance.csv", index=False)

        # Display attendance in a new window
        root = tk.Tk()
        root.title(f"Attendance of {Subject}")
        root.configure(background="black")

        with open("attendance.csv") as file:
            reader = csv.reader(file)
            r = 0
            for col in reader:
                c = 0
                for row in col:
                    label = tk.Label(root, width=20, height=1, fg="yellow", font=("times", 15, "bold"), bg="black", text=row, relief=RIDGE)
                    label.grid(row=r, column=c)
                    c += 1
                r += 1

        root.mainloop()

    def Attf():
        sub = tx.get().strip()
        if sub == "":
            message = "Please enter the subject name!"
            text_to_speech(message)
        else:
            subject_path = os.path.join("Attendance", sub)
            if os.path.exists(subject_path):
                os.startfile(subject_path)
            else:
                message = f"No folder found for subject '{sub}'!"
                text_to_speech(message)

    # Subject selection window
    subject = Tk()
    subject.title("Subject Attendance")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)

    titl = tk.Label(subject, text="Which Subject of Attendance?", bg="black", fg="green", font=("arial", 25))
    titl.place(x=100, y=12)

    sub = tk.Label(subject, text="Enter Subject", width=10, height=2, bg="black", fg="yellow", bd=5, relief=RIDGE, font=("times new roman", 15))
    sub.place(x=50, y=100)

    tx = tk.Entry(subject, width=15, bd=5, bg="black", fg="yellow", relief=RIDGE, font=("times", 30, "bold"))
    tx.place(x=190, y=100)

    fill_a = tk.Button(subject, text="View Attendance", command=calculate_attendance, bd=7, font=("times new roman", 15), bg="black", fg="yellow", height=2, width=12, relief=RIDGE)
    fill_a.place(x=195, y=170)

    attf = tk.Button(subject, text="Check Sheets", command=Attf, bd=7, font=("times new roman", 15), bg="black", fg="yellow", height=2, width=10, relief=RIDGE)
    attf.place(x=360, y=170)

    subject.mainloop()
