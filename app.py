from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('username')
        senha = request.form.get('password')

        if usuario == "admin" and senha == "1234":
            return redirect(url_for('inicio'))  
        else:
            return "Usuário ou senha incorretos!"

    return render_template('login.html')  

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')  

# Executa o app
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

@app.route('/conexao')
def conexao():
    conexao = mysql.connector.connect(
    host='0.0.0.0',
    username='root',
    password='',
    port=3306,
    database='conexao')

    return render_template('login.html') 
