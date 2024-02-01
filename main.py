from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin@localhost:5432/py3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/py3'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://GreenGame:GreenGamePassword@localhost:42069/GreenGameDB'
db = SQLAlchemy(app)


class Car(db.Model):
    __tablename__ = "cars"
    id = db.Column(db.Integer, primary_key=True)
    engine_displacement = db.Column(db.Float)
    max_speed = db.Column(db.Float)
    type_of_fuel = db.Column(db.Integer)

    def as_dict(self):
        return {
            'id': self.id,
            'engine_displacement': self.engine_displacement,
            'max_speed': self.max_speed,
            'type_of_fuel': self.type_of_fuel
            }


def validate_data(engine_displacement, max_speed, type_of_fuel):
    if not isinstance(engine_displacement, (int, float)):
        return False
    if not isinstance(max_speed, (int, float)):
        return False
    if not isinstance(type_of_fuel, int):
        return False
    if engine_displacement < 0 or max_speed < 0:
        return False
    if type_of_fuel < 1 or type_of_fuel > 6:
        return False
    return True


@app.route('/api/data', methods=["GET"])
def get_data():
    results = Car.query.all() 
    return jsonify([r.as_dict() for r in results])


@app.route('/api/data', methods=['POST'])
def post_data():
    new_json = request.get_json()
    if all(key in new_json.keys() for key in ['engine_displacement', 'max_speed', 'type_of_fuel']):
        if validate_data(new_json['engine_displacement'], new_json['max_speed'], new_json['type_of_fuel']):
            new_car = Car(
                engine_displacement=new_json['engine_displacement'],
                max_speed=new_json['max_speed'],
                type_of_fuel=new_json['type_of_fuel'])
            db.session.add(new_car)
            db.session.commit()
            return jsonify({'new_car_id': new_car.id})
        else:
            return jsonify({'message': 'Invalid data'}), 400
    else:
        return jsonify({'message': 'Invalid data'}), 400


@app.route('/api/data/<int:car_id>', methods=['DELETE'])
def delete_row(car_id):
    car = Car.query.get(car_id)
    if car is None:
        return jsonify({'message': 'Car not found'}), 404
    else:
        db.session.delete(car)
        db.session.commit()
        return jsonify({'deleted_car_id': car_id})


@app.route('/')
def index():
    results = Car.query.all()
    data = [r.as_dict() for r in results]
    return render_template('index.html', data=data)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        r_engine_displacement = request.form['engine_displacement']
        r_max_speed = request.form['max_speed']
        r_type_of_fuel = request.form['type_of_fuel']

        if r_engine_displacement and r_max_speed and r_type_of_fuel:
            # musimy zamienić na floaty i inta bo normalnie są stringami
            r_engine_displacement = float(r_engine_displacement)
            r_max_speed = float(r_max_speed)
            try:
                r_type_of_fuel = int(r_type_of_fuel)
            except ValueError:
                return render_template('error400.html'), 400
            if validate_data(r_engine_displacement, r_max_speed, r_type_of_fuel):
                new_car = Car(
                    engine_displacement=request.form['engine_displacement'],
                    max_speed=request.form['max_speed'],
                    type_of_fuel=request.form['type_of_fuel'])
                db.session.add(new_car)
                db.session.commit()
                return redirect(url_for('index'))
            else:
                return render_template('error400.html'), 400
        else:
            return render_template('error400.html'), 400

    return render_template('add.html')


@app.route('/delete/<int:car_id>', methods=["POST"])
def delete_id(car_id):
    car = Car.query.get(car_id)
    if car is None:
        return render_template('error404.html'), 404
    else:
        db.session.delete(car)
        db.session.commit()
        return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
