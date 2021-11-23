# Imports 

from flask import Flask
from flaskext.mysql import MySQL


app=Flask(__name__)
app.secret_key = "testkey0101"

mysql = MySQL(app)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = "root"
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'Store'
mysql.init_app(app)
