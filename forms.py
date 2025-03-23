from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, RadioField, SelectMultipleField, widgets, SubmitField, DateField
from wtforms.validators import DataRequired, Length, NumberRange
import datetime

class PedidoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(message="Campo Obligatorio"), Length(min=2, max=100)])
    direccion = StringField("Dirección", validators=[DataRequired(message="Campo Obligatorio"), Length(min=5, max=200)])
    telefono = StringField("Teléfono", validators=[DataRequired(message="Campo Obligatorio"), Length(min=8, max=15)])
    fecha_compra = DateField("Fecha de Compra", default=datetime.date.today)

    tamaño_pizza = RadioField("Tamaño Pizza", choices=[
        ('Chica', 'Chica $40'),
        ('Mediana', 'Mediana $80'),
        ('Grande', 'Grande $120')
    ], validators=[DataRequired(message="Campo Obligatorio")])

    ingredientes = SelectMultipleField("Ingredientes", choices=[
        ('Jamon', 'Jamón $10'),
        ('Piña', 'Piña $10'),
        ('Champiñones', 'Champiñones $10')
    ], option_widget=widgets.CheckboxInput(), widget=widgets.ListWidget(prefix_label=False))

    numero_pizzas = IntegerField("Número de Pizzas", validators=[DataRequired(message="Campo Obligatorio"), NumberRange(min=1, max=100)])

    submit = SubmitField("Agregar")


class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')