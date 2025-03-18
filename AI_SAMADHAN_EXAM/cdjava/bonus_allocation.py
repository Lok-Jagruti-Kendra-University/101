import pandas as pd    

# Define grading criteria
GRADES = [
    (0, 34, "F", 0), (35, 39, "E", 4), (40, 44, "D", 4.5), (45, 49, "C", 5),
    (50, 54, "B", 5.5), (55, 59, "B+", 6), (60, 64, "B++", 6.5), (65, 69, "A", 7),
    (70, 74, "A+", 7.5), (75, 79, "A++", 8), (80, 84, "O", 8.5), (85, 89, "O+", 9),
    (90, 94, "O++", 9.5), (95, 100, "O+++", 10)
]

SUBJECTS = {
    "PED": {"type": "theory"},
    "MEBC": {"type": "theory"},
    "CRE": {"type": "both"},
    "AST": {"type": "both"}
}

PASSING_CRITERIA = {
    "theory": 35,
    "both": {"theory": 17.5, "practical": 17.5}  
}

def assign_grade(marks):
    """Assigns a grade and grade points based on marks."""
    for lower, upper, grade, points in GRADES:
        if lower <= marks <= upper:
            return grade, points
    return "F", 0  

def process_marks(filename):
    try:
        df = pd.read_excel(filename, sheet_name=0)
        print("✅ File read successfully.")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return pd.DataFrame()  

    df.columns = df.columns.str.strip()  

    float_columns = [
        "PED_Marks", "MEBC_Marks", "CRE_Theory", "CRE_Practical",
        "AST_Theory", "AST_Practical", "Attendance Bonus"
    ]
    
    for col in float_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("float64")

    processed_data = []  

    for index, row in df.iterrows():
        student_data = {"Student": row["Student"]}
        attendance_bonus = float(row.get("Attendance Bonus", 0))
        remaining_bonus = attendance_bonus  
        failed_parts = []  

        for subject, details in SUBJECTS.items():
            if details["type"] == "theory":
                marks_col = f"{subject}_Marks"
                current_marks = float(row.get(marks_col, 0))  

                required_bonus = max(0, PASSING_CRITERIA["theory"] - current_marks)
                allocated_bonus = min(required_bonus, remaining_bonus, 7)  
                final_marks = min(100, current_marks + allocated_bonus)  

                student_data[f"{subject}_Original_Marks"] = current_marks
                student_data[f"{subject}_Att_Bonus"] = allocated_bonus
                student_data[f"{subject}_HOD_Bonus"] = 0  # Initialize HOD bonus
                student_data[f"{subject}_Final"] = final_marks
                student_data[f"{subject}_Grade"], student_data[f"{subject}_GPoints"] = assign_grade(final_marks)
                remaining_bonus -= allocated_bonus  

                if final_marks < PASSING_CRITERIA["theory"]:
                    failed_parts.append(subject)  

            elif details["type"] == "both":
                theory_col = f"{subject}_Theory"
                practical_col = f"{subject}_Practical"
                current_theory_marks = float(row.get(theory_col, 0))
                current_practical_marks = float(row.get(practical_col, 0))  

                required_theory_bonus = max(0, PASSING_CRITERIA["both"]["theory"] - current_theory_marks)
                required_practical_bonus = max(0, PASSING_CRITERIA["both"]["practical"] - current_practical_marks)
                allocated_theory_bonus = min(required_theory_bonus, remaining_bonus, 7)
                allocated_practical_bonus = min(required_practical_bonus, remaining_bonus - allocated_theory_bonus, 7)

                final_theory_marks = min(100, current_theory_marks + allocated_theory_bonus)
                final_practical_marks = min(100, current_practical_marks + allocated_practical_bonus)

                student_data[f"{subject}_Original_Theory"] = current_theory_marks
                student_data[f"{subject}_Original_Practical"] = current_practical_marks
                student_data[f"{subject}_Att_Bonus_Theory"] = allocated_theory_bonus
                student_data[f"{subject}_Att_Bonus_Practical"] = allocated_practical_bonus
                student_data[f"{subject}_HOD_Bonus_Theory"] = 0
                student_data[f"{subject}_HOD_Bonus_Practical"] = 0
                student_data[f"{subject}_Final_Theory"] = final_theory_marks
                student_data[f"{subject}_Final_Practical"] = final_practical_marks
                student_data[f"{subject}_Total"] = final_theory_marks + final_practical_marks
                student_data[f"{subject}_Grade"], student_data[f"{subject}_GPoints"] = assign_grade(student_data[f"{subject}_Total"])
                remaining_bonus -= (allocated_theory_bonus + allocated_practical_bonus)  

                if final_theory_marks < 17.5 or final_practical_marks < 17.5:
                    failed_parts.append(subject)  

        # Apply HOD Bonus IF it makes the student pass in ALL subjects
        if len(failed_parts) == 1:  
            subject = failed_parts[0]
            if SUBJECTS[subject]["type"] == "theory":
                required_to_pass = max(0, PASSING_CRITERIA["theory"] - student_data[f"{subject}_Final"])
                if required_to_pass > 0 and required_to_pass <= 2:
                    hod_bonus = required_to_pass  
                    student_data[f"{subject}_HOD_Bonus"] = hod_bonus  
                    student_data[f"{subject}_Final"] += hod_bonus  
                    student_data[f"{subject}_Grade"], student_data[f"{subject}_GPoints"] = assign_grade(student_data[f"{subject}_Final"])
                    failed_parts.remove(subject)  
            else:
                required_theory = max(0, PASSING_CRITERIA["both"]["theory"] - student_data[f"{subject}_Final_Theory"])
                required_practical = max(0, PASSING_CRITERIA["both"]["practical"] - student_data[f"{subject}_Final_Practical"])

                if required_theory + required_practical <= 2:  
                    if required_theory > 0:
                        student_data[f"{subject}_Final_Theory"] += required_theory
                        student_data[f"{subject}_HOD_Bonus_Theory"] = required_theory
                    if required_practical > 0:
                        student_data[f"{subject}_Final_Practical"] += required_practical
                        student_data[f"{subject}_HOD_Bonus_Practical"] = required_practical
                    student_data[f"{subject}_Total"] = student_data[f"{subject}_Final_Theory"] + student_data[f"{subject}_Final_Practical"]
                    student_data[f"{subject}_Grade"], student_data[f"{subject}_GPoints"] = assign_grade(student_data[f"{subject}_Total"])
                    failed_parts.remove(subject)  

        student_data["Remaining_Bonus"] = remaining_bonus  
        processed_data.append(student_data)  

    return pd.DataFrame(processed_data)  

# Run Processing
df_processed = process_marks("student_marks.xlsx")
df_processed.to_excel("processed_student_marks.xlsx", index=False)
print("✅ Data saved to 'processed_student_marks.xlsx'.")
