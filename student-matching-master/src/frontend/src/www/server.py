from flask import Flask, render_template, request, send_file
from werkzeug import secure_filename
from pandas import ExcelFile
import pandas as pd
import numpy as np
import json, os, sys, math, requests
from time import sleep

app = Flask(__name__)

# matching and data cleaning-related variables
sys.path.append("./src/scripts/")
from match import match_all
from clean_data import clean_files

# neo4j
from neo4j.v1 import GraphDatabase, basic_auth

# global variables
MENTOR_FILENAME = ""
STUDENT_FILENAME = ""
SUCCESS_CODE = 1
FAILURE_CODE = -1
ALLOWED_FILE_EXTENSIONS = set(['xlsx'])
UPLOAD_FOLDER="./src/www/uploads/"
DOWNLOAD_FOLDER="./src/www/downloads/"
MATCH_OUTPUT_FILE = "matched.xlsx"

# app configurations
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def is_extension_allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_FILE_EXTENSIONS

def validate_upload_files(mentorfile, studentfile):

    required_fields = ["Student ID", "First Name", "Last Name", "E-mail", "Faculty", "Program"]
    accepted_ans_types = ["No", "Yes", "Not Applicable", "Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]

    mentorsdf = pd.read_excel(mentorfile)
    studentsdf = pd.read_excel(studentfile)

    all_mentor_answers = pd.unique(mentorsdf.iloc[:,6:].values.ravel('K'))
    all_mentor_answers = [x for x in all_mentor_answers if not pd.isnull(x)]

    all_student_answers = pd.unique(studentsdf.iloc[:,6:].values.ravel('K'))
    all_student_answers = [x for x in all_student_answers if not pd.isnull(x)]

    mentors_file_headers = mentorsdf.columns.tolist()
    students_file_headers = studentsdf.columns.tolist()

    # ignore null values - they would be filled in when cleaning the data
    if (set(all_mentor_answers) != set(accepted_ans_types)):
        return {"message": "Your mentor file contains answer types that are not supported.", "code": FAILURE_CODE}

    if (set(all_student_answers) != set(accepted_ans_types)):
        return {"message": "Your student file contains answer types that are not supported.", "code": FAILURE_CODE}

    if (set(mentorsdf['Faculty'].unique()) != set(studentsdf['Faculty'].unique())):
        return {"message": "The Faculties listed are not the same in both files.", "code": FAILURE_CODE}

    if ([h.strip().lower() for h in mentors_file_headers] != [h.strip().lower() for h in students_file_headers]):
        return {"message": "The columns in the files submitted do not match.", "code": FAILURE_CODE}

    first_n_columns = mentors_file_headers[:len(required_fields)]
    if ([h.strip().lower() for h in first_n_columns] != [h.strip().lower() for h in required_fields]):
        return {"message": "The first " + str(len(required_fields)) + " columns of some file(s) do not match the required format.", "code": FAILURE_CODE}

    if (len(mentorsdf.index) >= len(studentsdf.index)):
        return {"message": "Please make sure you have uploaded the files in the right order.", "code": FAILURE_CODE}

    return {"message": "The files were successfully validated.", "code": SUCCESS_CODE, "num_students": len(mentorsdf.index)+len(studentsdf.index)}

# define basic route
@app.route("/")
def login():
    return render_template('login.html')

@app.route("/home", methods=["POST"])
def home():
    return render_template('index.html')

@app.route("/newMatchStep1", methods=['POST'])
def new_match_s1():
    return render_template('newmatch-step1.html')

@app.route('/newMatchStep2', methods = ['POST', 'GET'])
def new_match_s2():

    default_value = 2

    htmltable = "<table id=\"questions-table\" class=\"table table-bordered table-sm\"><thead class=\"thead-light\"><tr><th>QUESTION</th><th>RELEVANCY</th></tr></thead><tbody>"
    question_headers = pd.read_excel(app.config['UPLOAD_FOLDER'] + MENTOR_FILENAME).columns.tolist()

    for header in question_headers[6:]:
        htmltable += "<tr><td class=\"qheader\">" + header + "</td><td><input style=\"max-width:80px; min-width: 60px; margin-left: 5px;\" type=\"range\" min=\"0\" max=\"3\" step=\"1\" value=\"" + str(default_value) + "\"><label style=\"margin-left: 10px; width: 60px; font-weight: 400; color: goldenrod;\">?</label></td></tr>"
    htmltable += "</tbody></table>"

    return json.dumps({"message": "Grabbed the header information successfully.", "code": SUCCESS_CODE, "html": render_template('newmatch-step2.html'), "htmltable": htmltable})

@app.route("/lastMatch", methods=['POST']) # default is GET
def last_match():
    return render_template('lastmatch.html')

@app.route("/mentorLogs", methods=['POST']) # default is GET
def mentor_logs():
    return render_template('mentorlogs.html')

@app.route("/feedback", methods=['POST']) # default is GET
def feedback():
    return render_template('feedback.html')

@app.route('/upload', methods = ['POST'])
def uploader():

    # TODO: grab this from the request
    mentor_input_name = "mentor_file" # html form field "name"
    student_input_name = "student_file" # html form field "name"

    mentor_file = request.files[mentor_input_name]
    student_file = request.files[student_input_name]

    # error if the request was submitted without a file
    if not mentor_file or not student_file or mentor_file == "" or student_file == "":
        FAILURE_DATA = {"message": "Please attach mentor and student files.", "code": FAILURE_CODE}
        return json.dumps(FAILURE_DATA)

    # if the extensions submitted are not allowed
    if not is_extension_allowed(mentor_file.filename) or not is_extension_allowed(student_file.filename):
        FAILURE_DATA = {"message": "Please only submit Excel (.xlsx) files.", "code": FAILURE_CODE}
        return json.dumps(FAILURE_DATA)

    # secure filename
    global MENTOR_FILENAME, STUDENT_FILENAME
    MENTOR_FILENAME = secure_filename(mentor_file.filename)
    STUDENT_FILENAME = secure_filename(student_file.filename)

    # save files to server
    mentor_file.save(os.path.join(app.config['UPLOAD_FOLDER'], MENTOR_FILENAME))
    student_file.save(os.path.join(app.config['UPLOAD_FOLDER'], STUDENT_FILENAME))

    # make sure both files follow the same structure, in terms of columns
    # make sure the mentor and student files were not uploaded in reverse
    result = validate_upload_files(app.config['UPLOAD_FOLDER'] + MENTOR_FILENAME, app.config['UPLOAD_FOLDER'] + STUDENT_FILENAME)
    if result['code'] == FAILURE_CODE:
        FAILURE_DATA = {"message": result['message'], "code": FAILURE_CODE}
        return json.dumps(FAILURE_DATA)

    # success!
    SUCCESS_DATA = {"message": "The files were uploaded successfully.", "code": SUCCESS_CODE, "numStudents": result['num_students']}
    return json.dumps(SUCCESS_DATA)

@app.route('/match', methods = ['POST'])
def match():

    # receive array of json objects
    req_data_questions = request.get_json()['questions']

    # convert to dictionary
    questions_weights = dict()
    for row in req_data_questions:
        questions_weights[row['header']] = row['weight']

    # clean data
    print("\nCleaning data...")
    clean_files(app.config['UPLOAD_FOLDER'] + MENTOR_FILENAME, app.config['UPLOAD_FOLDER'] + "clean_" + MENTOR_FILENAME)
    clean_files(app.config['UPLOAD_FOLDER'] + STUDENT_FILENAME, app.config['UPLOAD_FOLDER'] + "clean_" + STUDENT_FILENAME)

    # run matching algorithm
    print("\nMatching...")
    match_data, total_num_groups = match_all(app.config['UPLOAD_FOLDER'] + "clean_" + MENTOR_FILENAME,\
                                    app.config['UPLOAD_FOLDER'] + "clean_" + STUDENT_FILENAME, \
                                    app.config['DOWNLOAD_FOLDER'] + MATCH_OUTPUT_FILE, questions_weights, False)

    try:
        # store results in database
        # send put request to neo4j database
        url = 'http://graph_server:5002/groupInsertion'
        # create your header as required
        headers = {"content-type": "application/json"} #, "Authorization": "<auth-key>" }
        r = requests.put(url, data=match_data, headers=headers)
    except Exception as e:
        print(e)
        return json.dumps({"message": "Could not store the matches in the database.", "code": FAILURE_CODE, "exception": e})

    SUCCESS_DATA = {"message": "Successfully created " + str(total_num_groups) + " groups.", "code": SUCCESS_CODE, "numGroups": total_num_groups}
    return json.dumps(SUCCESS_DATA)

@app.route('/download', methods = ['GET'])
def download_match():
    return send_file("downloads/" + MATCH_OUTPUT_FILE, as_attachment=True)


@app.route('/students', methods = ['POST'])
def get_students():
	url = 'http://graph_server:5002/students'
	try:
		r = requests.get(url)
		SUCCESS_DATA = {"message": "Successfully queried all students.", "code": SUCCESS_CODE, "students": r.json()}
		return json.dumps(SUCCESS_DATA)
	except Exception as e:
		print(e)
		FAILURE_DATA = {"message": "Could not retrieve all students from the database.", "code": FAILURE_CODE, "exception": e};
		return json.dumps(FAILURE_DATA)

@app.route('/students/<int:student_id>', methods = ['POST'])
def get_student_id(student_id):
	url = 'http://graph_server:5002/students/' + str(student_id);
	try:
		r = requests.get(url)
		SUCCESS_DATA = {"message": "Successfully queried all students.", "code": SUCCESS_CODE, "student":r.json()};
		return json.dumps(SUCCESS_DATA)
	except Exception as e:
		print(e)
		FAILURE_DATA = {"message": "Could not retrieve all students from the database.", "code": FAILURE_CODE, "exception": e};
		return json.dumps(FAILURE_DATA)

@app.route('/students/mentors', methods = ['POST'])
def get_student_mentors():
	url = 'http://graph_server:5002/students/mentors'
	# faculty = request.get_json()["faculty"]
	try:
		r = requests.get(url, params=request.get_json())
		SUCCESS_DATA = {"message": "Successfully queried all students.", "code": SUCCESS_CODE, "mentors":r.json()};
		return json.dumps(SUCCESS_DATA)
	except Exception as e:
		print(e)
		FAILURE_DATA = {"message": "Could not retrieve all students from the database.", "code": FAILURE_CODE, "exception": e};
		return json.dumps(FAILURE_DATA)

@app.route("/groups", methods=["GET"])
def get_all_groups():
	url = "http://graph_server:5002/groups"
	try:
		r = requests.get(url)
		SUCCESS_DATA = {"message": "Successfully queried all the groups", "code": SUCCESS_CODE, "groups": r.json()}
		return json.dumps(SUCCESS_DATA)
	except Exception as e:
		print(e)
		FAILURE_DATA = {"message": "Could not retrieve the group for student", "code": FAILURE_CODE, "exception": e}
		return json.dumps(FAILURE_DATA)

@app.route("/get_group", methods=["POST"])
def get_group():

	student_id = request.get_json()["student_id"] # get id from request
	url = "http://graph_server:5002/groups/" + str(student_id)
	try:
		r = requests.get(url)
		SUCCESS_DATA = {"message": "Successfully queried the group for student " + str(student_id) + ".", "code": SUCCESS_CODE, "group": r.json()}
		return json.dumps(SUCCESS_DATA)
	except Exception as e:
		print(e)
		FAILURE_DATA = {"message": "Could not retrieve the group for student " + str(student_id) + ".", "code": FAILURE_CODE, "exception": e}
		return json.dumps(FAILURE_DATA)

@app.route("/facultypercent", methods=["POST"])
def get_facultypercent():
	url = "http://graph_server:5002/facultypercent"
	try:
		r = requests.get(url)
		SUCCESS_DATA = {"message": "Successfully queried the group for student", "code": SUCCESS_CODE, "percentages": r.json()}
		return json.dumps(SUCCESS_DATA)
	except Exception as e:
		print(e)
		FAILURE_DATA = {"message": "Could not retrieve the group for student", "code": FAILURE_CODE, "exception": e}
		return json.dumps(FAILURE_DATA)

@app.route("/send_email", methods=["POST"])
def send_email():

    req = request.get_json()

    num_emails = 1

    # check if an array was passed
    if isinstance(req, (list, np.ndarray)):
        num_emails = len(req)
        for email in req:
            print("> To: " + email["to"] + "\n> From: " + email["from"] + "\n> Subject: " + email["subject"] + "\n> Content: " + email["content"])
            print()

    SUCCESS_DATA = {"message": "Successfully sent " + str(num_emails) + " e-mails.", "code": SUCCESS_CODE}
    return json.dumps(SUCCESS_DATA)

@app.route("/sleeper", methods=["GET"])
def sleeper():
    sleep(1.5)
    return "OK"

# check if the executed file is the main program
if __name__ == "__main__":
    # app.run(port=5000) # run the app
    app.run(host="0.0.0.0", debug=True)

    
