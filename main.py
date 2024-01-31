import psycopg2
import sqlalchemy
from dataclasses import dataclass
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import Column, Integer, Float, exists
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from sqlalchemy.orm import sessionmaker
from wtforms import FloatField, SubmitField, IntegerField
from wtforms.validators import InputRequired, NumberRange

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:admin@localhost:5432/py3")
base = declarative_base()


@dataclass
class Car(base):
    __tablename__ = "cars"
    id: int = Column(Integer, primary_key=True)
    engine_displacement: float = Column(Float)
    max_speed: float = Column(Float)
    type_of_fuel: int = Column(Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


base.metadata.create_all(engine)
Session = sessionmaker(engine)


class AddCarForm(FlaskForm):
    engine_displacement = FloatField('Engine displacement', validators=[InputRequired(), NumberRange(min=0.1)])
    max_speed = FloatField('Max speed', validators=[InputRequired(), NumberRange(min=0.1)])
    type_of_fuel = IntegerField('Type of fuel (1-6)', validators=[InputRequired(), NumberRange(min=1, max=6)])
    submit = SubmitField('Add')


class DeleteCarForm(FlaskForm):
    car_id = IntegerField('Delete id', validators=[NumberRange(min=1)])
    submit = SubmitField('Delete')


class ConfirmForm(FlaskForm):
    submit = SubmitField('Confirm')


@app.route('/api/data', methods=["GET"])
def get_data():
    with Session(bind=engine) as session:
        results = session.query(Car).all()
    return jsonify([r.as_dict() for r in results])


@app.route('/api/data', methods=['POST'])
def post_data():
    new_json = request.get_json()
    if (isinstance(new_json['engine_displacement'], (int, float)) and isinstance(new_json['max_speed'], (int, float))
            and type(new_json['type_of_fuel']) is int):
        new_object = Car(**new_json)
        with Session(bind=engine) as session:
            session.add(new_object)
            session.commit()
            return jsonify({'new_record_primary_key': new_object.id})
    else:
        response = jsonify({'message': 'Invalid data'})
        response.status_code = 400
        return response


@app.route('/api/data/<string:car_id>', methods=['DELETE'])
def delete_row(car_id):
    with Session(bind=engine) as session:
        exists_bool = session.query(exists().where(Car.id == car_id)).scalar()
        if not exists_bool:
            response = jsonify({'message': 'Record not found'})
            response.status_code = 404
            return response
        else:
            session.query(Car).filter(Car.id == car_id).delete()
            session.commit()
            return jsonify({'deleted_record_primary_key': int(car_id)})


# ROUTES

@app.route('/')
def index():
    with Session(bind=engine) as session:
        results = session.query(Car).all()
    data = [r.as_dict() for r in results]
    return render_template('index.html', data=data)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddCarForm()

    if request.method == "POST":
        if form.validate_on_submit():
            new_car = Car(
                engine_displacement=form.engine_displacement.data,
                max_speed=form.max_speed.data,
                type_of_fuel=form.type_of_fuel.data)
            with Session(bind=engine) as session:
                session.add(new_car)
                session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('error400.html'), 400

    return render_template('add.html', form=form)


@app.route('/delete/<car_id>', methods=["POST"])
def delete_id(car_id):
    with Session(bind=engine) as session:
        if not session.query(exists().where(Car.id == car_id)).scalar():
            return render_template('error404.html'), 404

        form = ConfirmForm()
        if form.validate():
            session.query(Car).filter(Car.id == car_id).delete()
            session.commit()
            return redirect(url_for('index'))

    return render_template('delete.html', car_id=car_id, form=form)


if __name__ == '__main__':
    app.run(debug=True)
