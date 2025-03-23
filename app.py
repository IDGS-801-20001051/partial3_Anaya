from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from config import DevelopmentConfig
import forms
from models import db, Pedidos, User
import os
import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect()
app.config['WTF_CSRF_ENABLED'] = True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

PEDIDOS_TEMP_FILE = 'pedidos.txt'

def calcular_subtotal(tamaño, ingredientes, cantidad):
    """Calcula el subtotal de una pizza."""
    precio_tamaño = {'Chica': 40, 'Mediana': 80, 'Grande': 120}.get(tamaño, 0)
    precio_ingredientes = len(ingredientes) * 10
    return (precio_tamaño + precio_ingredientes) * cantidad

def guardar_pedido_temporal(tamaño, ingredientes, cantidad, subtotal):
    """Guarda un pedido temporal en un archivo (sin los datos del cliente)."""
    with open(PEDIDOS_TEMP_FILE, 'a') as f:
        f.write(f"{tamaño},{','.join(ingredientes)},{cantidad},{subtotal}\n")

def leer_pedidos_temporales():
    """Lee los pedidos temporales del archivo."""
    pedidos = []
    if os.path.exists(PEDIDOS_TEMP_FILE):
        with open(PEDIDOS_TEMP_FILE, 'r') as f:
            for line in f:
                valores = line.strip().split(',')
                if len(valores) >= 4:  
                    tamaño = valores[0]
                    ingredientes = valores[1:-2]  
                    cantidad = int(valores[-2])
                    subtotal = float(valores[-1])

                    pedidos.append({
                        'tamaño': tamaño,
                        'ingredientes': ingredientes,
                        'cantidad': cantidad,
                        'subtotal': subtotal
                    })
                else:
                    print(f"Línea incorrecta en {PEDIDOS_TEMP_FILE}: {line.strip()}")
    return pedidos

def limpiar_pedidos_temporales():
    """Limpia el archivo de pedidos temporales."""
    if os.path.exists(PEDIDOS_TEMP_FILE):
        os.remove(PEDIDOS_TEMP_FILE)

@app.route("/", methods=['GET', 'POST'])
@login_required
def pedido():
    form = forms.PedidoForm()
    pedidos_temporales = leer_pedidos_temporales()
    total_pedido_temporal = sum(pedido['subtotal'] for pedido in pedidos_temporales)

    nombre_cliente = request.args.get('nombre', '')
    direccion_cliente = request.args.get('direccion', '')
    telefono_cliente = request.args.get('telefono', '')

    fecha = request.form.get('fecha')
    periodo = request.form.get('periodo', 'dia')
    ventas = []
    total_ventas = 0.0 

    if fecha:
        try:
            fecha_dt = datetime.datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            flash("Formato de fecha incorrecto. Use AAAA-MM-DD.", "danger")
            return render_template('index.html', form=form, pedidos=pedidos_temporales,
                                   total_pedido=total_pedido_temporal, nombre_cliente=nombre_cliente,
                                   direccion_cliente=direccion_cliente, telefono_cliente=telefono_cliente)

        if periodo == 'dia':
            ventas = Pedidos.query.filter(func.date(Pedidos.fecha_compra) == fecha_dt.date()).all()
            total_ventas = sum(pedido.total_pedido for pedido in ventas)
        else:  
            ventas = Pedidos.query.filter(func.strftime('%Y-%m', Pedidos.fecha_compra) == fecha_dt.strftime('%Y-%m')).all()
            total_ventas = sum(pedido.total_pedido for pedido in ventas)

    if form.validate_on_submit():
        tamaño_pizza = form.tamaño_pizza.data
        ingredientes = form.ingredientes.data
        numero_pizzas = form.numero_pizzas.data

        subtotal = calcular_subtotal(tamaño_pizza, ingredientes, numero_pizzas)

        guardar_pedido_temporal(tamaño_pizza, ingredientes, numero_pizzas, subtotal)

        flash(f"Pizza agregada al pedido. Subtotal: ${subtotal:.2f}", "success")

        return redirect(url_for('pedido', nombre=form.nombre.data, direccion=form.direccion.data,
                                telefono=form.telefono.data))

    form.nombre.data = nombre_cliente
    form.direccion.data = direccion_cliente
    form.telefono.data = telefono_cliente

    return render_template('index.html', form=form, pedidos=pedidos_temporales,
                           total_pedido=total_pedido_temporal, nombre_cliente=nombre_cliente,
                           direccion_cliente=direccion_cliente, telefono_cliente=telefono_cliente,
                           ventas=ventas, total_ventas=total_ventas, fecha=fecha, periodo=periodo)

@app.route('/quitar_pedido', methods=['POST'])
def quitar_pedido():
    pedidos_temporales = leer_pedidos_temporales()

    nombre = request.form.get('nombre', '')
    direccion = request.form.get('direccion', '')
    telefono = request.form.get('telefono', '')

    if pedidos_temporales:
        pedidos_temporales.pop()  

        limpiar_pedidos_temporales()  

        for pedido in pedidos_temporales:
            guardar_pedido_temporal(pedido['tamaño'], pedido['ingredientes'], pedido['cantidad'], pedido['subtotal'])
        flash("Último pedido quitado.", "success")
    else:
        flash("No hay pedidos para quitar.", "danger")

    return redirect(url_for('pedido', nombre=nombre, direccion=direccion, telefono=telefono))

@app.route('/terminar_pedido', methods=['POST'])
def terminar_pedido():
    nombre = request.args.get('nombre')
    direccion = request.args.get('direccion')
    telefono = request.args.get('telefono')

    if not nombre:
        nombre = request.form.get('nombre')
    if not direccion:
        direccion = request.form.get('direccion')
    if not telefono:
        telefono = request.form.get('telefono')

    pedidos_temporales = leer_pedidos_temporales()

    if not pedidos_temporales:
        flash("No hay pedidos para terminar.", "danger")
        return redirect(url_for('pedido'))

    total_pedido = sum(pedido['subtotal'] for pedido in pedidos_temporales)

    nuevo_pedido = Pedidos(nombre=nombre, direccion=direccion, telefono=telefono, total_pedido=total_pedido)
    db.session.add(nuevo_pedido)
    db.session.commit()

    flash(f"Pedido completado. El total a pagar es: ${total_pedido:.2f}", "success")
    limpiar_pedidos_temporales()

    return redirect(url_for('pedido'))

@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    fecha = request.form.get('fecha')
    periodo = request.form.get('periodo', 'dia')

    if fecha:
        try:
            fecha_dt = datetime.datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            flash("Formato de fecha incorrecto. Use AAAA-MM-DD.", "danger")
            return render_template('ventas.html')

        if periodo == 'dia':
            ventas = Pedidos.query.filter(func.date(Pedidos.fecha_compra) == fecha_dt.date()).all()
            total_ventas = sum(pedido.total_pedido for pedido in ventas)
        else: 
            ventas = Pedidos.query.filter(func.strftime('%Y-%m', Pedidos.fecha_compra) == fecha_dt.strftime('%Y-%m')).all()
            total_ventas = sum(pedido.total_pedido for pedido in ventas)

        return render_template('ventas.html', ventas=ventas, total_ventas=total_ventas, fecha=fecha, periodo=periodo)

    return render_template('ventas.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('pedido'))
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)


@app.route('/alumnos')
@login_required
def alumnos():
    return render_template('alumnos.html')


@app.route('/maestros')
@login_required
def maestros():
    return render_template('maestros.html')



if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True, port="3000")