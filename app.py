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

@app.route('/retirar', methods=['GET', 'POST'])
def retirar():
    if request.method == 'POST':
        # Aqui dentro vai o código que pega os dados e salva no banco...
        operacao = request.form.get('operacao')
        nome = request.form.get('nomeItem')
        categoria = request.form.get('categoria')
        quantidade = request.form.get('quantidade')
        funcao = request.form.get('funcao')
        valor = request.form.get('valor')

        try:
            conexao_bd = obter_conexao()
            cursor = conexao_bd.cursor()

            if operacao == 'Saida':        
                comando = "UPDATE estoque SET quantidade_estoque = quantidade_estoque - %s WHERE nome = %s"
                valores = (quantidade, nome)
                
                cursor.execute(comando, valores)
            
            if operacao == 'Entrada':        
                comando = "UPDATE estoque SET quantidade_estoque = quantidade_estoque + %s WHERE nome = %s"
                valores = (quantidade, nome)
                
                cursor.execute(comando, valores)

            conexao_bd.commit()
                    
            cursor.close()
            conexao_bd.close()
            
            return redirect(url_for('estoque'))
            
        except mysql.connector.Error as erro:
            return f"Erro ao registrar a retirada: {erro}"
            

    return render_template('retirar.html')

@app.route('/', methods=['POST'])
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

    return render_template('inicio.html') 

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