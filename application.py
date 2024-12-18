from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
import re
import awsgi

application = Flask(__name__)
application.secret_key = 'caching_sha2_password'

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dante2024',
    'database': 'project',
}

def get_db_connection():
    """Establece una conexión a la base de datos y devuelve el objeto de conexión."""
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

@application.route('/')
@application.route('/login', methods=['GET', 'POST'])
def login():
    msg = ' '
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM `accounts` WHERE username = %s AND password = %s', (username, password,))
                account = cursor.fetchone()
                if account:
                    session['loggedin'] = True
                    session['id'] = account['id']
                    session['username'] = account['username']
                    msg = 'Logged in successfully!'
                    return render_template('index.html', msg=msg)
                else:
                    msg = 'Incorrect username / password!'
        finally:
            connection.close()
    return render_template('login.html', msg=msg)

@application.route('/output')
def output():
	msg=' '
	return render_template('output.html',msg = msg)

@application.route('/stroke', methods=['GET', 'POST'])
def stroke():
    msg = ' '
    if request.method == 'POST' and all(key in request.form for key in [
        'gender', 'age', 'hypertension', 'heart_disease', 'ever_married',
        'work_type', 'residence_type', 'avg_glucose_level', 'bmi', 'smoking_status'
    ]):
        form_data = {key: request.form[key] for key in request.form}
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO account_stroke (gender, age, hypertension, heart_disease, ever_married, work_type, residence_type, avg_glucose_level, bmi, smoking_status, stroke) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL);', 
                               (form_data['gender'], form_data['age'], form_data['hypertension'], form_data['heart_disease'], 
                                form_data['ever_married'], form_data['work_type'], form_data['residence_type'], 
                                form_data['avg_glucose_level'], form_data['bmi'], form_data['smoking_status']))
                connection.commit()
                msg = "Your data has been recorded. Please consult a specialist for more information."
        finally:
            connection.close()
        return render_template('output.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('stroke.html', msg=msg)

@application.route('/diabetes', methods=['GET', 'POST'])
def diabetes():
    msg = ''
    if request.method == 'POST' and all(key in request.form for key in ['pregnancies', 'glucose', 'bloodpressure', 'skinthickness', 'insulin', 'bmi_dia', 'diabetes_pedigree_fnc', 'age_dia']):
        form_data = {key: request.form[key] for key in request.form}
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = '''
                    INSERT INTO account_dia (pregnancies, glucose, bloodpressure, skinthickness, insulin, bmi_dia, diabetes_pedigree_fnc, age_dia, outcome) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL);
                '''
                cursor.execute(query, (form_data['pregnancies'], form_data['glucose'], form_data['bloodpressure'], form_data['skinthickness'], form_data['insulin'], form_data['bmi_dia'], form_data['diabetes_pedigree_fnc'], form_data['age_dia']))
                connection.commit()
                msg = "Your data has been recorded. Please consult a specialist for more information."
        finally:
            connection.close()
        return render_template('output.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('diabetes.html', msg=msg)

@application.route('/cardiovascular', methods=['GET', 'POST'])
def cardiovascular():
    msg = ''
    if request.method == 'POST' and all(key in request.form for key in ['age1', 'gender1', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'glu', 'smoke', 'alco', 'active']):
        form_data = {key: request.form[key] for key in request.form}
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = '''
                    INSERT INTO account_cardiovascular (age1, gender1, height, weight, ap_hi, ap_lo, cholesterol, glu, smoke, alco, active, CARDIO_DISEASE) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL);
                '''
                cursor.execute(query, (form_data['age1'], form_data['gender1'], form_data['height'], form_data['weight'], form_data['ap_hi'], form_data['ap_lo'], form_data['cholesterol'], form_data['glu'], form_data['smoke'], form_data['alco'], form_data['active']))
                connection.commit()
                msg = "Your data has been recorded. Please consult a specialist for more information."
        finally:
            connection.close()
        return render_template('output.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('cardiovascular.html', msg=msg)

@application.route('/calculate_bmi', methods=['GET', 'POST'])
def calculate_bmi():
    msg = 'BMI CALCULATOR'
    if request.method == 'POST' and 'weight' in request.form and 'height' in request.form:
        weight = request.form['weight']
        height = request.form['height']
        if not weight or not height:
            msg = 'Please fill out the form!'
        else:
            weight = float(weight)
            height = float(height)
            bmi = calculate_bmi_value(weight, height)
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute('INSERT INTO account_bmi VALUES (NULL, %s, %s, %s)', (weight, height, bmi))
                    connection.commit()
            finally:
                connection.close()
            msg = f'Your BMI is: {bmi}'
            return render_template('output.html', msg=msg)
    return render_template('calculate_bmi.html', msg=msg)

def calculate_bmi_value(weight, height):
    height_in_meters = height / 100
    bmi = weight / (height_in_meters ** 2)
    return round(bmi, 2)

@application.route('/calculate_calories', methods=['GET', 'POST'])
def calculate_calories():
	msg = 'CALORIE CALCULATOR'
	if request.method == 'POST' and 'gender' in request.form and 'weight' in request.form and 'height' in request.form and 'age' in request.form and 'activity_level' in request.form:
		gender = request.form['gender']
		weight = request.form['weight']
		height = request.form['height']
		age = request.form['age']
		activity_level = request.form['activity_level']

		if not gender or not weight or not height or not age or not activity_level:
			msg = 'Please fill out the form!'
		else:
			weight = float(weight)
			height = float(height)
			age = int(age)
			bmr = calculate_bmr(gender, weight, height, age)
			calorie_msg = calculate_calories_based_on_activity(bmr, activity_level)
			msg = f'Your BMR is: {bmr} calories. {calorie_msg}'
			return render_template('output.html', msg = msg)
	return render_template('calculate_calories.html', msg=msg)

def calculate_bmr(gender, weight, height, age):
    if gender.lower() == 'female':
        bmr = (weight * 10) + (height * 6.25) - (age * 5) - 161
    else:
        bmr = (weight * 10) + (height * 6.25) - (age * 5) + 5
    return int(bmr)

def calculate_calories_based_on_activity(bmr, activity_level):
    activity_levels = {
        'sedentary': 1.2,
        'exercise_1_3': 1.375,
        'exercise_4_5': 1.55,
        'daily_exercise': 1.725,
        'intense_exercise': 1.9,
        'very_intense_exercise': 2.095,
    }
    calorie_multiplier = activity_levels.get(activity_level, 1.2)
    calories = int(bmr * calorie_multiplier)
    return f'Based on your activity level, you need approximately {calories} calories per day.'
 
@application.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@application.route('/details')
def details():
    return render_template('details.html')


@application.route('/stroke_info')
def stroke_info():
    return render_template('stroke_info.html')

@application.route('/diabetes_info')
def diabetes_info():
    return render_template('diabetes_info.html')

@application.route('/cardiovascular_info')
def cardiovascular_info():
    return render_template('cardiovascular_info.html')

@application.route('/index')
def index():
	return render_template('index.html')




@application.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and all(key in request.form for key in ['username', 'password', 'email']):
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not all([username, password, email]):
            msg = 'Please fill out the form!'
        else:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
                    account = cursor.fetchone()
                    if account:
                        msg = 'Account already exists!'
                    else:
                        cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
                        connection.commit()
                        msg = 'You have successfully registered!'
            finally:
                connection.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

if __name__ == '__main__':
    application.run(debug=True)
    

