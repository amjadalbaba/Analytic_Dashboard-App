import pyrebase
import pandas as pd
import functions
from flask import Flask, render_template, jsonify

config = {
    "apiKey": "AIzaSyDdIHQ5iT4qZAxa_Y6Gci6lcHPnz5RQXHo",
    "authDomain": "connectingfirebasepython.firebaseapp.com",
    "projectId": "connectingfirebasepython",
    "databaseURL": "https://connectingfirebasepython-default-rtdb.firebaseio.com/",
    "storageBucket": "connectingfirebasepython.appspot.com",
    "messagingSenderId": "392960110265",
    "appId": "1:392960110265:web:451982a7d9313b7a0ab568",
    "measurementId": "G-K9V4RK9V8Q"
}

firebase = pyrebase.initialize_app(config)
database = firebase.database()

data = database.child("database").child("data").get()
df = pd.json_normalize(list(data.val()))

app = Flask(__name__)


@app.route('/')
def data_sending():
    data_for_top_5_jobs    = top_five_job_titles_posting()
    seniority_level        = seniority_level_need()
    cities_posting         = top_ten_cities_in_job_posting()
    avg_salary_rating      = avg_salary_vs_rating()

    return render_template('index.html', jobs=data_for_top_5_jobs, seniority=seniority_level, cities=cities_posting, salrating=avg_salary_rating)


def top_five_job_titles_posting():
    output = {'Task': 'Frequency'}
    output.update(dict(df["Job Title"].value_counts().head()))

    return output


def top_ten_cities_in_job_posting():
    output = {'Task': 'Frequency'}
    output.update(dict(df["Headquarters"].apply(lambda x: x.split(",")[0]).value_counts().head(10)))

    return output


def avg_salary_vs_rating():
    output = {'Task': 'Frequency'}
    output.update(dict(df[['Rating', 'avg_salary']].sort_values('Rating').values))
    del output[-1] # to remove outlier

    return output


def seniority_level_need():
    df['seniority'] = df['Job Title'].apply(functions.seniority)
    seniority_levels = {'Task': 'Experience Needed'}
    seniority_levels.update(dict(df['seniority'].value_counts()))
    del seniority_levels['na'] # to remove null values count

    return seniority_levels

# APIs

@app.route('/api/all', methods=['GET'])
def get_all_items():
    return jsonify(list(data.val()))


@app.route('/api/item/<int:item_id>', methods=['GET'])
def get_item_by_id(item_id):
    item_data = database.child("database").child("data").child(item_id).get()

    return jsonify(dict(item_data.val()))


@app.route('/api/items/<int:first_id>/<int:second_id>', methods=['GET'])
def get_items(first_id, second_id):
    all_data = []
    for i in range(first_id, second_id + 1):
        item_data = database.child("database").child("data").child(i).get()
        all_data.append(dict(item_data.val()))

    return jsonify(all_data)


if __name__ == "__main__":
    app.run()

