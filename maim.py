import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField

app = Flask(__name__)

conn = psycopg2.connect(
        host="localhost",
        dbname="py3",
        user='postgres',
        password='admin',
        port=5432)

def insertquery(sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()

def getquery(sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    return rows

class Form(FlaskForm):
    engine_displacement = FloatField('Engine displacement')
    max_speed = FloatField('Max speed')
    type_of_fuel = SelectField(['diesel', 'gasoline', 'electric', 'hydrogen', 'LPG', 'hybrid', 'biodiesel'])
    submit = SubmitField('Submit')


def validate_and_add(engine_displacement, max_speed, type_of_fuel):
    if type(engine_displacement) != 'number' or type(max_speed) != 'number':
        print("One of values is not number")
        return False
    if type_of_fuel not in ['diesel', 'gasoline', 'electric', 'hydrogen', 'LPG', 'hybrid', 'biodiesel']:
        return False
    insertquery(
        'INSERT INTO test_table VALUES(DEFAULT, {}, {}, {})'.format(engine_displacement, max_speed, type_of_fuel))
    return True


@app.route('/add')
def index():
    form = Form()

    if form.validate_on_submit():
        # Access form data using form.name.data and form.age.data
        engine_displacement = form.engine_displacement.data
        max_speed = form.max_speed.data
        type_of_fuel = form.type_of_fuel.data

        result = validate_and_add(engine_displacement, max_speed, type_of_fuel)

        # You can process the form data here (e.g., save to a database)

        # return redirect(url_for('success', name=name, age=age))

    return render_template('add.html', form=form)

@app.route('/api/data')
def get_data():
    results = getquery('SELECT * FROM test_table;')
    data_list = []
    for result in results:
        id_, engine_displacement, max_speed, type_of_fuel = result
        data_list.append(
            {
                "id": id_,
                "engine_displacement": float(engine_displacement),
                "max_speed": float(max_speed),
                "type_of_fuel": type_of_fuel
             }
        )
    return data_list

@app.route('/api/data', methods=['POST'])
def post_data():
    data_json = request.get_json()
    engine_displacement, max_speed, type_of_fuel = data_json
    result = validate_and_add(engine_displacement, max_speed, type_of_fuel)
    if result is False:
        pass # error
    else:
        pass # cos tam ze sie udalo

@app.route('/api/data/<string:id>', methods=['DELETE'])
def delete_row(item_id):
    available_rows = getquery('SELECT id FROM test_table')
    if item_id not in available_rows:
        pass # ERROR MESSAGE 404
    else:
        insertquery('DELETE FROM test_table WHERE id = {}'.format(item_id))

@app.route('/')
def show_table():
    data = get_data()
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)