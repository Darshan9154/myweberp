from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
import json
import pandas as pd
from huggingface_hub import InferenceClient

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Define the available prompts
prompts = {
    "Basic Information": [
        "Tell me about Alice Smith.",
        "What is the position of Bob Johnson?",
        "How much does Grace Lee earn?"
    ],
    "Department Queries": [
        "List all employees in the IT department.",
        "Who are the employees in the Engineering department?"
    ],
    "Gender and Position Specific": [
        "How many female employees work in the Sales department?",
        "List all male Software Engineers."
    ],
    "Performance and Salary Queries": {
        "Performance Rating": [
            "Who has the highest performance rating among employees?",
            "List all employees with a performance rating of 4.5 or above."
        ],
        "Salary Information": [
            "Give me a list of employees who earn more than 90,000.",
            "Who are the employees with a salary below 80,000?"
        ]
    },
    "Hire Date Queries": {
        "Recent Hires": [
            "List all employees hired in 2023.",
            "Who were the new hires in May 2020?"
        ],
        "Longest Tenured Employees": [
            "Who has been with the company the longest?",
            "List employees hired before 2021."
        ]
    },
    "Reporting and Summarizing": {
        "Generate Reports": [
            "Generate a report of all employees with their names and departments.",
            "Create an Excel report of employees earning over 100,000."
        ],
        "Custom Reports": [
            "Provide a summary of all employees with salaries above 80,000 and their positions.",
            "List all employees and their performance ratings, highlighting those above 4.0."
        ]
    },
    "Advanced Filtering": {
        "Filtered Queries": [
            "Show me female employees with salaries over 85,000.",
            "Give me a list of all employees in the Data Science department with a rating above 4.0."
        ]
    },
    "Miscellaneous": {
        "Contact Information": [
            "What is the email address of David Williams?",
            "How can I contact Olivia Baker?"
        ],
        "Department Performance": [
            "Which department has the highest average salary?",
            "List the performance ratings of employees in the Finance department."
        ]
    },
    "Interactivity": {
        "Interactive Reports": [
            "Generate a report for all employees hired in the last year.",
            "Do you want to see a list of all employees with their emails?"
        ]
    }
}

# Replace with your actual Hugging Face API key
HUGGINGFACE_API_KEY = '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'

def generate_report(prompt, employees):
    client = InferenceClient(api_key=HUGGINGFACE_API_KEY)

    messages = [
        {"role": "user", "content": f"{prompt}\n\nContext: {json.dumps(employees)}"}
    ]

    response = client.chat_completion(
        model="mistralai/Mistral-Nemo-Instruct-2407",
        messages=messages,
        max_tokens=500,
        stream=False
    )

    report = response['choices'][0]['message']['content']
    return report

def save_report_as_excel(report, output_file):
    df = pd.DataFrame({"Report": [report]})
    df.to_excel(output_file, index=False)

@app.route('/')
def index():
    return render_template('index.html', prompts=prompts)

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        file = request.files['file']

        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            with open(file_path, 'r') as f:
                data = f.read()
                formatted_data = data.strip().replace("}\n{", "}, {")
                employees = json.loads(f'[{formatted_data}]')

            report = generate_report(prompt, employees)
            output_file = "employee_report.xlsx"
            save_report_as_excel(report, output_file)

            return render_template('result.html', report=report, output_file=output_file)
        else:
            flash('Please upload a valid employee data file.')
            return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
