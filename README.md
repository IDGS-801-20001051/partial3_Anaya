Sistema de Gestión de Pedidos con Flask
Este proyecto es una aplicación web desarrollada con Flask, que permite gestionar pedidos de pizzas, autenticación de usuarios y consultas de ventas. Utiliza Flask-Login para la autenticación, Flask-WTF para formularios seguros y SQLAlchemy para la base de datos.
Instalación y configuración
Clonar el repositorio

git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
Crear un entorno virtual (opcional pero recomendado)

python -m venv venv  
source venv/bin/activate # En macOS/Linux  
venv\Scripts\activate # En Windows
3Instalar dependencias

pip install -r requirements.txt
Configurar la base de datos
El proyecto usa SQLAlchemy para la base de datos. Asegúrate de modificar el archivo config.py con la configuración adecuada de la base de datos.

Si estás usando SQLite, la configuración puede verse así:

SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
Después, dentro de Python o ejecutando en la terminal:

flask shell
from app import db
db.create_all()
exit()
Esto creará la base de datos y las tablas necesarias.

Ejecutar la aplicación
Para iniciar el servidor Flask en modo desarrollo, usa el siguiente comando:

python app.py
La aplicación se ejecutará en:

http://localhost:3000/
Si deseas cambiar el puerto, modifica el siguiente código en app.py:

app.run(debug=True, port=3000)
Autenticación y Login
La aplicación usa Flask-Login para gestionar usuarios.

Si no tienes usuarios registrados, debes agregarlos manualmente en la base de datos.

La ruta de inicio de sesión es:

http://localhost:3000/login
La ruta de cierre de sesión es:

http://localhost:3000/logout
