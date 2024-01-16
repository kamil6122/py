import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField, RadioField, IntegerField
from wtforms.validators import InputRequired

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
    engine_displacement = FloatField('Engine displacement')
    max_speed = FloatField('Max speed')
    type_of_fuel = IntegerField('Type of fuel')
    # type_of_fuel = SelectField('Type', choices=[(1, '1: diesel'), (2, '2: gasoline'), (3, '3: electric'),
    #                             (4, '4: hydrogen'), (5, '5: LPG'), (6, '6: hybrid')])
    submit = SubmitField('Add')


class DeleteCarForm(FlaskForm):
    car_id = IntegerField('Delete id')
    submit = SubmitField('Delete')


def validate_and_add(engine_displacement, max_speed, type_of_fuel):
    # if type(engine_displacement) is not float or type(max_speed) is not float:
    #     print("One of values is not number")
    #     return False
    # if type(type_of_fuel) is not int:
    #     return False
    insertquery(
        '''INSERT INTO test_table VALUES(DEFAULT, {}, {}, '{}')'''.format(engine_displacement, max_speed, type_of_fuel))
    return True

# APIS

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
        pass  # error
    else:
        pass  # cos tam ze sie udalo


@app.route('/api/data/<string:id>', methods=['DELETE'])
def delete_row(item_id):
    available_rows = getquery('SELECT id FROM test_table')
    if int(item_id) not in available_rows:
        pass  # ERROR MESSAGE 404
    else:
        insertquery('DELETE FROM test_table WHERE id = {}'.format(item_id))


# ROUTES

@app.route('/')
def index():
    data = get_data()
    form = DeleteCarForm()
    print(form.car_id.data)
    print(form.validate_on_submit())
    if form.validate_on_submit():
        car_id = form.car_id.data
        delete_row(car_id)
        print('wee?')
        return redirect(url_for('delete/' + str(car_id)))

    return render_template('index.html', data=data, form=form)

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddCarForm()
    if form.validate_on_submit():
        engine_displacement = form.engine_displacement.data
        max_speed = form.max_speed.data
        type_of_fuel = form.type_of_fuel.data
        print(engine_displacement, max_speed, type_of_fuel)
        result = validate_and_add(engine_displacement, max_speed, type_of_fuel)

        return redirect(url_for('index'))

    return render_template('add.html', form=form)


@app.route('/delete/<car_id>', methods=["POST"])
def delete_id(car_id):
    print('widzisz mnie?')
    delete_row(car_id)
    # return redirect(url_for('index'))
    return render_template('delete.html')


if __name__ == '__main__':
    app.run(debug=True)
