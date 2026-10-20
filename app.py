import os
from contextlib import contextmanager

import mysql.connector
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify)
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------
# CONFIGURAÇÃO
# Local (python app.py)  -> usa 127.0.0.1
# Docker (compose)       -> o compose define DB_HOST=db
# ---------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "almoxarifado")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

PASTA_UPLOAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
EXTENSOES_OK = {"png", "jpg", "jpeg", "gif", "webp"}
FUNCOES_ADMIN = ("Administrador", "admin")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "TCC_SENAI")
os.makedirs(PASTA_UPLOAD, exist_ok=True)


# ---------------------------------------------------------------
# BANCO DE DADOS
# ---------------------------------------------------------------
def obter_conexao():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


@contextmanager
def banco(dictionary=False, commit=False):
    """Abre conexão + cursor e fecha tudo sozinho, mesmo se der erro."""
    con = obter_conexao()
    cursor = con.cursor(dictionary=dictionary)
    try:
        yield cursor
        if commit:
            con.commit()
    finally:
        cursor.close()
        con.close()


def eh_admin():
    return session.get("funcao") in FUNCOES_ADMIN


def pagina_inicial():
    return redirect(url_for("inicio_admin" if eh_admin() else "inicio_usuario"))


def buscar_estoque():
    with banco(dictionary=True) as cur:
        cur.execute(
            "SELECT id, nome, categoria, funcao, quantidade, valor, foto FROM estoque"
        )
        return cur.fetchall()


def extensao_permitida(nome_arquivo):
    return "." in nome_arquivo and nome_arquivo.rsplit(".", 1)[1].lower() in EXTENSOES_OK


# ---------------------------------------------------------------
# ROTAS DO SITE
# ---------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_digitado = request.form.get("username")
        senha_digitada = request.form.get("password")

        try:
            with banco(dictionary=True) as cur:
                cur.execute(
                    "SELECT usuario, senha, funcao FROM usuarios WHERE usuario = %s",
                    (usuario_digitado,),
                )
                encontrado = cur.fetchone()
        except mysql.connector.Error as erro:
            return f"Erro no banco de dados: {erro}"

        if encontrado is not None and encontrado["senha"] == senha_digitada:
            session["usuario"] = encontrado["usuario"]
            session["funcao"] = encontrado["funcao"]
            return pagina_inicial()

        return "Usuário ou senha incorretos!"

    return render_template("login.html")


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


@app.route("/inicio")
def inicio_admin():
    if "usuario" not in session or not eh_admin():
        return redirect(url_for("login"))
    try:
        return render_template("inicio.html", itens=buscar_estoque())
    except mysql.connector.Error as erro:
        return f"Erro ao carregar o estoque: {erro}"


@app.route("/inicio-usuario")
def inicio_usuario():
    if "usuario" not in session:
        return redirect(url_for("login"))
    try:
        return render_template("inicio.usuario.html", itens=buscar_estoque())
    except mysql.connector.Error as erro:
        return f"Erro ao carregar o estoque do usuário: {erro}"


@app.route("/adicionar_estoque", methods=["GET"])
def estoque():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("adicionar_estoque.html")


@app.route("/cadastrar_item", methods=["POST"])
def cadastrar_item():
    if "usuario" not in session:
        return redirect(url_for("login"))

    nome_item = request.form.get("nome_item")
    categoria = request.form.get("categoria")
    funcao = request.form.get("funcao")
    quantidade = request.form.get("quantidade")
    valor = request.form.get("valor")
    foto = request.files.get("foto")

    # Salva a foto em static/uploads e guarda só o nome do arquivo no banco
    nome_foto = None
    if foto and foto.filename and extensao_permitida(foto.filename):
        nome_foto = secure_filename(foto.filename)
        foto.save(os.path.join(PASTA_UPLOAD, nome_foto))

    try:
        with banco(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO estoque (nome, categoria, funcao, quantidade, valor, foto)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (nome_item, categoria, funcao, quantidade, valor, nome_foto),
            )
        return pagina_inicial()
    except mysql.connector.Error as erro:
        return f"Erro ao cadastrar item: {erro}"


@app.route("/retirar", methods=["GET", "POST"])
def retirar():
    if "usuario" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        operacao = request.form.get("operacao")  # 'Entrada' ou 'Saida'
        nome = request.form.get("nomeItem")
        try:
            quantidade = int(request.form.get("quantidade"))
        except (TypeError, ValueError):
            return "Quantidade inválida!"

        if operacao not in ("Entrada", "Saida") or not nome or quantidade <= 0:
            return "Dados inválidos!"

        if operacao == "Entrada":
            comando = "UPDATE estoque SET quantidade = quantidade + %s WHERE nome = %s"
            valores = (quantidade, nome)
        else:
            # Só retira se houver quantidade suficiente (evita estoque negativo)
            comando = (
                "UPDATE estoque SET quantidade = quantidade - %s "
                "WHERE nome = %s AND quantidade >= %s"
            )
            valores = (quantidade, nome, quantidade)

        try:
            with banco(commit=True) as cur:
                cur.execute(comando, valores)
                linhas = cur.rowcount
        except mysql.connector.Error as erro:
            return f"Erro ao atualizar o estoque: {erro}"

        if linhas == 0:
            return "Item não encontrado ou quantidade insuficiente em estoque!"

        return pagina_inicial()

    return render_template("retirar.html")


@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if "usuario" not in session or not eh_admin():
        return redirect(url_for("login"))

    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        funcao = request.form.get("funcao")

        try:
            with banco(commit=True) as cur:
                cur.execute(
                    "INSERT INTO usuarios (usuario, senha, funcao) VALUES (%s, %s, %s)",
                    (usuario, senha, funcao),
                )
            return redirect(url_for("usuarios"))
        except mysql.connector.Error as erro:
            return f"Erro ao cadastrar o usuário: {erro}"

    return render_template("usuarios.html")


@app.route("/conexao")
def conexao():
    """Teste rápido de conexão com o banco."""
    try:
        obter_conexao().close()
        return jsonify({"status": "ok", "host": DB_HOST}), 200
    except mysql.connector.Error as erro:
        return jsonify({"status": "erro", "detalhe": str(erro)}), 500


# ---------------------------------------------------------------
# API (usada pelo app / mobile) - mesma tabela 'estoque' do site
# Colunas: id, nome, categoria, funcao, quantidade, valor, foto
# ---------------------------------------------------------------
@app.errorhandler(mysql.connector.Error)
def erro_banco(erro):
    return jsonify({"erro": f"Erro no banco de dados: {erro}"}), 500


def converter_item(item):
    item["valor"] = float(item["valor"] or 0)
    return item


# POST /api/login -> {"username": "...", "password": "..."}
@app.route("/api/login", methods=["POST"])
def api_login():
    dados = request.get_json(silent=True) or request.form
    usuario = dados.get("username")
    senha = dados.get("password")

    with banco(dictionary=True) as cur:
        cur.execute(
            "SELECT usuario, senha, funcao FROM usuarios WHERE usuario = %s",
            (usuario,),
        )
        encontrado = cur.fetchone()

    if encontrado is None or encontrado["senha"] != senha:
        return jsonify({"erro": "Usuário ou senha incorretos."}), 401

    return jsonify({"usuario": encontrado["usuario"], "funcao": encontrado["funcao"]}), 200


# GET /api/estoque (e /api/itens, mesmo resultado)
@app.route("/api/estoque", methods=["GET"])
@app.route("/api/itens", methods=["GET"])
def api_listar_estoque():
    return jsonify([converter_item(i) for i in buscar_estoque()]), 200


# GET /api/estoque/<id>
@app.route("/api/estoque/<int:estoque_id>", methods=["GET"])
def api_buscar_estoque(estoque_id):
    with banco(dictionary=True) as cur:
        cur.execute(
            "SELECT id, nome, categoria, funcao, quantidade, valor, foto "
            "FROM estoque WHERE id = %s",
            (estoque_id,),
        )
        item = cur.fetchone()

    if item is None:
        return jsonify({"erro": "Item não encontrado."}), 404
    return jsonify(converter_item(item)), 200


# POST /api/estoque -> {"nome", "valor", "quantidade", "categoria", "funcao", "foto"}
@app.route("/api/estoque", methods=["POST"])
def api_adicionar_estoque():
    dados = request.get_json(silent=True) or request.form

    nome = dados.get("nome")
    valor = dados.get("valor", dados.get("preco"))  # aceita "preco" também
    quantidade = dados.get("quantidade")
    categoria = dados.get("categoria")
    funcao = dados.get("funcao")
    foto = dados.get("foto")

    if not nome or valor is None or quantidade is None:
        return jsonify({"erro": "Campos obrigatórios: nome, valor e quantidade."}), 400

    with banco(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO estoque (nome, categoria, funcao, quantidade, valor, foto)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nome, categoria, funcao, quantidade, valor, foto),
        )
        novo_id = cur.lastrowid

    return jsonify({"mensagem": "Item adicionado com sucesso.", "id": novo_id}), 201


# POST /api/estoque/movimentar -> {"operacao": "Entrada"|"Saida", "nome": "...", "quantidade": 5}
@app.route("/api/estoque/movimentar", methods=["POST"])
def api_movimentar_estoque():
    dados = request.get_json(silent=True) or request.form

    operacao = dados.get("operacao")
    nome = dados.get("nome")
    try:
        quantidade = int(dados.get("quantidade"))
    except (TypeError, ValueError):
        quantidade = 0

    if operacao not in ("Entrada", "Saida") or not nome or quantidade <= 0:
        return jsonify({"erro": "Informe operacao ('Entrada' ou 'Saida'), nome e quantidade maior que 0."}), 400

    if operacao == "Entrada":
        query = "UPDATE estoque SET quantidade = quantidade + %s WHERE nome = %s"
        valores = (quantidade, nome)
    else:
        query = (
            "UPDATE estoque SET quantidade = quantidade - %s "
            "WHERE nome = %s AND quantidade >= %s"
        )
        valores = (quantidade, nome, quantidade)

    with banco(commit=True) as cur:
        cur.execute(query, valores)
        linhas = cur.rowcount

    if linhas == 0:
        return jsonify({"erro": "Item não encontrado ou quantidade insuficiente."}), 404

    return jsonify({"mensagem": f"{operacao} registrada com sucesso."}), 200


# GET /api/usuarios -> lista usuários (sem senha)
@app.route("/api/usuarios", methods=["GET"])
def api_listar_usuarios():
    with banco(dictionary=True) as cur:
        cur.execute("SELECT usuario, funcao FROM usuarios")
        lista = cur.fetchall()
    return jsonify(lista), 200


# POST /api/usuarios -> {"usuario": "...", "senha": "...", "funcao": "..."}
@app.route("/api/usuarios", methods=["POST"])
def api_cadastrar_usuario():
    dados = request.get_json(silent=True) or request.form

    usuario = dados.get("usuario")
    senha = dados.get("senha")
    funcao = dados.get("funcao")

    if not usuario or not senha or not funcao:
        return jsonify({"erro": "Campos obrigatórios: usuario, senha e funcao."}), 400

    with banco(commit=True) as cur:
        cur.execute("SELECT 1 FROM usuarios WHERE usuario = %s", (usuario,))
        if cur.fetchone() is not None:
            return jsonify({"erro": "Esse usuário já existe."}), 409

        cur.execute(
            "INSERT INTO usuarios (usuario, senha, funcao) VALUES (%s, %s, %s)",
            (usuario, senha, funcao),
        )

    return jsonify({"mensagem": "Usuário cadastrado com sucesso."}), 201


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1", host="0.0.0.0", port=5000)