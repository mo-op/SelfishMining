from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, SubmitField, StringField, IntegerField

from wtforms import validators, ValidationError

class simulationForm(FlaskForm):
	#string field due to odd behaviour of float
	alpha = StringField("Alpha")
	#gamma = TextField("Gamma")
	iterations = IntegerField("Iterations")
	simulate = SubmitField("Simulate")