import pandas as pd
from flask import Flask, Response
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# -------------------------------
# LOAD DATA
# -------------------------------
employees = pd.read_csv("Zenvy_employees_new.csv")
attendance = pd.read_csv("Zenvy_attendance_new.csv")

# -------------------------------
# MERGE DATA
# -------------------------------
data = pd.merge(employees, attendance, on="employee_id")

# -------------------------------
# SALARY MAPPING
# -------------------------------
salary_map = {
    101: 30000,
    102: 25000,
    103: 27500,
    104: 28000,
    105: 35000
}

data["salary"] = data["employee_id"].map(salary_map)

# -------------------------------
# SALARY STRUCTURE
# -------------------------------
data["basic"] = data["salary"]
data["hra"] = data["basic"] * 0.2
data["bonus"] = 1500

# -------------------------------
# DEDUCTIONS
# -------------------------------
data["pf"] = data["basic"] * 0.1
data["tax"] = data["basic"] * 0.05

# -------------------------------
# FINAL CALCULATIONS
# -------------------------------
data["gross_salary"] = data["basic"] + data["hra"] + data["bonus"]
data["total_deductions"] = data["pf"] + data["tax"]
data["net_salary"] = data["gross_salary"] - data["total_deductions"]

# -------------------------------
# SELECT REQUIRED COLUMNS
# -------------------------------
data = data[[
    "name", "role", "employee_id",
    "basic", "hra", "bonus",
    "pf", "tax",
    "gross_salary", "total_deductions", "net_salary"
]]

# -------------------------------
# SAVE OUTPUT CSV
# -------------------------------
data.to_csv("week-4_salary_output.csv", index=False)

print("✅ WEEK-4 SALARY CALCULATED SUCCESSFULLY\n")
print(data[["employee_id", "net_salary"]])

# -------------------------------
# PDF PAYSLIP FUNCTION
# -------------------------------
def generate_payslip(emp):
    pdf = SimpleDocTemplate(f"{emp['name']}_payslip.pdf")
    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # Custom styling
    title_style.textColor = colors.blue
    title_style.alignment = 1  # Center

    content = []

    # Company Title
    content.append(Paragraph("NEO ZENO TALENT", title_style))
    content.append(Spacer(1, 10))

    # Employee Details
    content.append(Paragraph(f"Name: {emp['name']}", normal_style))
    content.append(Paragraph(f"Role: {emp['role']}", normal_style))
    content.append(Spacer(1, 10))

    # Salary Breakdown
    content.append(Paragraph(f"Basic: {emp['basic']}", normal_style))
    content.append(Paragraph(f"HRA: {emp['hra']}", normal_style))
    content.append(Paragraph(f"Bonus: {emp['bonus']}", normal_style))
    content.append(Paragraph(f"PF: {emp['pf']}", normal_style))
    content.append(Paragraph(f"Tax: {emp['tax']}", normal_style))
    content.append(Spacer(1, 10))

    # Final Salary
    content.append(Paragraph(f"Net Salary: {emp['net_salary']}", title_style))

    pdf.build(content)


# -------------------------------
# GENERATE PAYSLIPS
# -------------------------------
for _, row in data.iterrows():
    generate_payslip(row)

print("✅ Payslips generated successfully")

# -------------------------------
# FLASK API
# -------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Week-4 Payroll API Running"

@app.route("/salary")
def salary():
    json_data = json.dumps(data.to_dict(orient="records"), indent=4)
    return Response(json_data, mimetype='application/json')

# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)