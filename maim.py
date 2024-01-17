import psycopg2
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, IntegerField
from wtforms.validators import InputRequired, NumberRange

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

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

# FORM CLASSES


class AddCarForm(FlaskForm):
    engine_displacement = FloatField('Engine displacement', validators=[InputRequired(), NumberRange(min=0.1)])
    max_speed = FloatField('Max speed', validators=[InputRequired(), NumberRange(min=0.1)])
    type_of_fuel = IntegerField('Type of fuel', validators=[InputRequired(), NumberRange(min=1, max=6)])
    submit = SubmitField('Add')


class DeleteCarForm(FlaskForm):
    car_id = IntegerField('Delete id', validators=[NumberRange(min=1)])
    submit = SubmitField('Delete')


class ConfirmForm(FlaskForm):
    submit = SubmitField('Confirm')


def add_to_db(engine_displacement, max_speed, type_of_fuel):
    insertquery(
        '''INSERT INTO test_table VALUES(DEFAULT, {}, {}, '{}')'''.format(engine_displacement, max_speed, type_of_fuel))

# ERRORS


@app.errorhandler(404)
def resource_not_found(e):
    # if page:
    #     return render_template('error400.html'), 404
    # else:
    return jsonify(error=str(e)), 404


@app.errorhandler(400)
def invalid_data(e):
    # if page:
    #     return render_template('error400.html'), 400
    # else:
    return jsonify(error=str(e)), 400
# APIS


@app.route('/api/data', methods=["GET"])
def get_data():
    results = getquery('SELECT * FROM test_table;')
    data_list = []
    for result in results:
        id_, engine_displacement, max_speed, type_of_fuel = result
        data_list.append(
            {
                "id": id_,
                "engine_displacement": engine_displacement,
                "max_speed": max_speed,
                "type_of_fuel": type_of_fuel
            }
        )
    return data_list


@app.route('/api/data', methods=['POST'])
def post_data():
    data_json = request.get_json()
    if (isinstance(data_json['engine_displacement'], (int, float)) and isinstance(data_json['max_speed'], (int, float))
            and type(data_json['type_of_fuel']) is int):
        add_to_db(data_json['engine_displacement'], data_json['max_speed'], data_json['type_of_fuel'])
        last_id_query = getquery('SELECT LASTVAL()')
        return_json = {'new_primary_key': last_id_query[0][0]}
        return jsonify(return_json)
    else:
        response = jsonify({'message': 'Invalid data'})
        response.status_code = 400
        return response


@app.route('/api/data/<string:car_id>', methods=['DELETE'])
def delete_row(car_id):
    q = getquery('SELECT id FROM test_table')
    available_rows = [item[0] for item in q]
    if int(car_id) not in available_rows:
        response = jsonify({'message': 'Record not found'})
        response.status_code = 404
        return response
    else:
        insertquery('DELETE FROM test_table WHERE id = {}'.format(car_id))
        return jsonify({'deleted_record_primary_key': car_id})


# ROUTES

@app.route('/')
def index():
    data = get_data()
    return render_template('index.html', data=data)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddCarForm()

    if request.method == "POST":
        if form.validate_on_submit():
            engine_displacement = form.engine_displacement.data
            max_speed = form.max_speed.data
            type_of_fuel = form.type_of_fuel.data
            add_to_db(engine_displacement, max_speed, type_of_fuel)
            return redirect(url_for('index'))
        else:
            return render_template('error400.html'), 400

    return render_template('add.html', form=form)


@app.route('/delete/<car_id>', methods=["POST"])
def delete_id(car_id):
    q = getquery('SELECT id FROM test_table')
    available_rows = [item[0] for item in q]
    if int(car_id) not in available_rows:
        return render_template('error404.html'), 404
    return render_template('delete.html', car_id=car_id)


@app.route('/deleting/<car_id>', methods=["POST"])
def deleting(car_id):
    delete_row(car_id)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
