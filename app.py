from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


def obter_conexao():
    return mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',       
        password='',
        database='almoxarifado'
    )

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

@app.route('/estoque')
def estoque():
    return render_template('estoque.html') 

@app.route('/retirar')
def retirar():
    return render_template('retirar.html')

@app.route('/cadastro_concluido', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    categoria = request.form.get('categoria')
    funcao = request.form.get('funcao')
    quantidade = request.form.get('quantidade')
    valor = request.form.get('valor')
    foto = request.form.get('foto')

    banco = obter_conexao()
    cursor = banco.cursor()

    query = """
        INSERT INTO estoque (nome, categoria, funcao, quantidade, valor, foto) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    valores = (nome, categoria, funcao, quantidade, valor, foto)
    
    cursor.execute(query, valores)
    banco.commit() 
    
    cursor.close()
    banco.close()

    return render_template('cadastro_concluido.html') 

@app.route('/conexao')
def conexao():
    conexao_teste = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        port=3306,
        database='conexao'
    )
    conexao_teste.close()
    return render_template('login.html') 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')