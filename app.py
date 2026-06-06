# let's import the flask
from collections import Counter
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import pymongo
from datetime import datetime
from urllib.parse import quote_plus

app = Flask(__name__)


raw_password = 'pyer123__'
safe_password = quote_plus(raw_password)
MONGODB_URI = f"mongodb+srv://jlpampilonpacs_db_user:{safe_password}@python.80huf7o.mongodb.net/?appName=PYTHON"
client = pymongo.MongoClient(MONGODB_URI)
db = client['STUDENTS']

@app.route('/')
def home ():
    techs = ['HTML', 'CSS', 'Flask', 'Python']
    name = 'LV'
    return render_template('home.html', techs=techs, name = name, title = 'Home')

@app.route('/about')
def about():
    name = 'LV'
    return render_template('about.html', name = name, title = 'About Us')

#RESULT--------------------------------------------------------------------------------------------------------------------------

@app.route('/result', methods = ['GET', 'POST'])
def result():
    here = request.form.get('content')
    if not here:
        return redirect(url_for('post'))

    raw_split = here.split()
    counter = Counter(raw_split)

    freq = counter.most_common(1)[0][0]

    placeholder = []
    for item, count in counter.items():
        elements_dct = {
            "word": item,
            "word_count": len(item),
            "total_words": len(raw_split),
            "total_characters": len(here),
            "word_repeats": count,
        }
        placeholder.append(elements_dct)

    return render_template('result.html', placeholder=placeholder, freq=freq)


#POST--------------------------------------------------------------------------------------------------------------------------

@app.route('/post', methods= ['GET','POST'])
def post():
    name = 'Text Analyzer'
    return render_template('post.html', name = name, title = name)

#STUDENTS--------------------------------------------------------------------------------------------------------------------------
@app.route('/students', methods = ['GET'])
def students():
    student = list(db.students.find({}, {"_id": 0}))
    return render_template('students.html', students = student)





@app.route('/API', methods = ['GET'])
def API():
    all_students = list(db["students"].find({}, {"_id": 0}))

    all_feedbacks = list(db["feedbacks"].find({}, {"_id": 0}))

    database_dump = {
        "students": all_students,
        "feedbacks": all_feedbacks
    }
    return jsonify(database_dump)



#JOIN--------------------------------------------------------------------------------------------------------------------------
@app.route('/join', methods = ['GET', 'POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html')
    if request.method == 'POST':
        name = request.form.get('name')
        bday = request.form.get('bday')
        country = request.form.get('country')
        bio = request.form.get('bio')
        raw_skills = request.form.get('skills')
        skills = [skill.strip().title() for skill in raw_skills.split(',') if skill.strip()]

        student = {
            'name': name,
            'bday': bday,
            'country': country,
            'skills': skills,
            "bio": bio,
        }
        db.students.insert_one(student)
        return redirect(url_for('join'))
    return render_template('join.html')


#FEEDBACK--------------------------------------------------------------------------------------------------------------------------
@app.route('/feedback', methods = ['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        comments = list(db.feedbacks.find({}, {"_id": 0}))
        return render_template('feedback.html', comments = comments)
    if request.method == 'POST':
        feedback = request.form.get('feedback', " ").strip()
        if not feedback:
            return redirect(url_for('feedback'))
        feedback_dict = {"feedback": feedback,
                         "datetime": datetime.now().strftime("%B %d, %Y at %I:%M%p")}
        db.feedbacks.insert_one(feedback_dict)
        return redirect(url_for('feedback'))
    return render_template('feedback.html')



if __name__ == '__main__':
    # for deployment
    # to make it work for both production and development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)