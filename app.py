from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


def obter_conexao():
    return mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='Root',
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
    try:
        conexao_bd = obter_conexao()
        cursor = conexao_bd.cursor()
        cursor.execute("SELECT * FROM estoque")
        resultado = cursor.fetchall()
        cursor.close()
        conexao_bd.close()
    except mysql.connector.Error as erro:
        return f"Erro ao buscar itens do estoque: {erro}"

    return render_template('inicio.html', resultado=resultado)


@app.route('/adicionar_estoque', methods=['GET'])
def estoque():
    return render_template('adicionar_estoque.html')


@app.route('/cadastrar_item', methods=['POST'])
def cadastrar_item():
    nome_item = request.form.get('nome_item')
    categoria = request.form.get('categoria')
    funcao = request.form.get('funcao')
    quantidade = request.form.get('quantidade')
    valor = request.form.get('valor')
    foto = request.files.get('foto')

    nome_foto = foto.filename if foto and foto.filename else None

    try:
        conexao_bd = obter_conexao()
        cursor = conexao_bd.cursor()

        comando = """
            INSERT INTO estoque (nome, categoria, funcao, quantidade, valor, foto)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (nome_item, categoria, funcao, quantidade, valor, nome_foto)
        cursor.execute(comando, valores)

        conexao_bd.commit()
        cursor.close()
        conexao_bd.close()

        return redirect(url_for('inicio'))

    except mysql.connector.Error as erro:
        return f"Erro ao cadastrar item: {erro}"


@app.route('/retirar', methods=['GET', 'POST'])
def retirar():
    if request.method == 'POST':
        operacao = request.form.get('operacao')
        nome = request.form.get('nomeItem')
        categoria = request.form.get('categoria')
        quantidade = request.form.get('quantidade')
        funcao = request.form.get('funcao')
      

        try:
            conexao_bd = obter_conexao()
            cursor = conexao_bd.cursor()

            if operacao == 'Saida':
                comando = "UPDATE estoque SET quantidade = quantidade - %s WHERE nome = %s"
                valores = (quantidade, nome)
                cursor.execute(comando, valores)

            if operacao == 'Entrada':
                comando = "UPDATE estoque SET quantidade = quantidade + %s WHERE nome = %s"
                valores = (quantidade, nome)
                cursor.execute(comando, valores)

            conexao_bd.commit()
            cursor.close()
            conexao_bd.close()

            return redirect(url_for('inicio'))  # <-- corrigido: nome de função certo

        except mysql.connector.Error as erro:
            return f"Erro ao registrar a retirada: {erro}"

    return render_template('retirar.html')


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