import base64
import binascii
import os
import uuid
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from functools import wraps

import bcrypt
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

# Senha do admin criado automaticamente na primeira execução
ADMIN_SENHA_INICIAL = os.getenv("ADMIN_PASSWORD", "1234")

PASTA_UPLOAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
EXTENSOES_OK = {"png", "jpg", "jpeg", "gif", "webp"}
FUNCOES_ADMIN = ("Administrador", "admin")
FUNCOES_VALIDAS = ("admin", "usuario")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "TCC_SENAI")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # limite de 16 MB por requisição
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
        charset="utf8mb4",  # necessário para gravar "Saída" com acento
    )


@contextmanager
def banco(dictionary=False, commit=False):
    """Abre conexão + cursor e fecha tudo sozinho, mesmo se der erro.
    Se der erro antes do commit, nada é gravado."""
    con = obter_conexao()
    cursor = con.cursor(dictionary=dictionary)
    try:
        yield cursor
        if commit:
            con.commit()
    finally:
        cursor.close()
        con.close()


# ---------------------------------------------------------------
# SENHAS (bcrypt)
# ---------------------------------------------------------------
def gerar_hash(senha):
    """Transforma a senha em hash bcrypt (60 caracteres, cabe no VARCHAR(255))."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha_digitada, hash_salvo):
    """Compara a senha digitada com o hash salvo no banco."""
    if not senha_digitada or not hash_salvo:
        return False
    try:
        return bcrypt.checkpw(senha_digitada.encode("utf-8"), hash_salvo.encode("utf-8"))
    except ValueError:  # hash inválido (ex.: senha antiga ainda em texto puro)
        return False


def senha_valida(senha):
    """bcrypt só considera os primeiros 72 bytes, então limitamos o tamanho."""
    return bool(senha) and len(senha.encode("utf-8")) <= 72


def verificar_login(cursor, usuario, senha):
    """Confere usuário e senha (a senha no banco é um hash).
    O cursor precisa ser dictionary=True. Devolve a linha do usuário ou None."""
    cursor.execute(
        "SELECT id, usuario, senha, funcao FROM usuarios WHERE usuario = %s",
        (usuario,),
    )
    encontrado = cursor.fetchone()
    if encontrado and verificar_senha(senha, encontrado["senha"]):
        return encontrado
    return None


def iniciar_sessao(usuario):
    session.clear()
    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["usuario"]
    session["usuario_tipo"] = usuario["funcao"]


# ---------------------------------------------------------------
# PREPARAÇÃO DO BANCO (roda ao iniciar o app)
# ---------------------------------------------------------------
def preparar_banco():
    """
    - cria a tabela 'historico' se ela não existir;
    - converte para hash qualquer senha que ainda esteja em texto puro;
    - cria o usuário 'admin' se ele não existir.
    """
    try:
        with banco(dictionary=True, commit=True) as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS historico (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    produto_nome VARCHAR(255),
                    tipo_movimentacao VARCHAR(50),
                    quantidade INT DEFAULT 0,
                    usuario VARCHAR(255),
                    data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP
                ) DEFAULT CHARSET=utf8mb4
                """
            )

            cur.execute("SELECT id, senha FROM usuarios")
            for u in cur.fetchall():
                senha_atual = u["senha"] or ""
                # hashes bcrypt começam com $2a$, $2b$ ou $2y$
                if not senha_atual.startswith("$2"):
                    cur.execute(
                        "UPDATE usuarios SET senha = %s WHERE id = %s",
                        (gerar_hash(senha_atual), u["id"]),
                    )
                    print(f"[setup] usuário id={u['id']} convertido para hash.")

            cur.execute("SELECT 1 FROM usuarios WHERE usuario = %s", ("admin",))
            if cur.fetchone() is None:
                cur.execute(
                    "INSERT INTO usuarios (usuario, senha, funcao) VALUES (%s, %s, %s)",
                    ("admin", gerar_hash(ADMIN_SENHA_INICIAL), "admin"),
                )
                print("[setup] usuário admin criado.")
    except mysql.connector.Error as erro:
        print(f"[setup] não foi possível preparar o banco: {erro}")


# ---------------------------------------------------------------
# PERMISSÕES
# ---------------------------------------------------------------
def eh_admin():
    return session.get("usuario_tipo") in FUNCOES_ADMIN


def login_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


def admin_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        if not eh_admin():
            return redirect(url_for("inicio_usuario"))
        return func(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ---------------------------------------------------------------
def pagina_inicial():
    return redirect(url_for("inicio_admin" if eh_admin() else "inicio_usuario"))


def registrar_historico(cursor, produto_nome, tipo, quantidade=0):
    """Grava no histórico (usa o mesmo cursor/transação da operação principal)."""
    usuario = session.get("usuario_nome", "desconhecido")
    cursor.execute(
        "INSERT INTO historico (produto_nome, tipo_movimentacao, quantidade, usuario) "
        "VALUES (%s, %s, %s, %s)",
        (produto_nome, tipo, quantidade, usuario),
    )


def buscar_historico(limite=500):
    with banco(dictionary=True) as cur:
        cur.execute(
            "SELECT id, produto_nome, tipo_movimentacao, quantidade, usuario, data_movimentacao "
            "FROM historico ORDER BY data_movimentacao DESC, id DESC LIMIT %s",
            (limite,),
        )
        linhas = cur.fetchall()
    for linha in linhas:
        data = linha.pop("data_movimentacao")
        linha["data_formatada"] = data.strftime("%d/%m/%Y %H:%M:%S") if data else ""
    return linhas


def buscar_estoque():
    with banco(dictionary=True) as cur:
        cur.execute(
            "SELECT id, nome, categoria, funcao, quantidade, valor, foto FROM estoque"
        )
        return cur.fetchall()


def movimentar_estoque(cur, operacao, nome, quantidade):
    """
    Faz a Entrada/Saída e grava no histórico.
    Devolve None se deu certo, ou 'nao_encontrado' / 'insuficiente'.
    """
    if operacao == "Entrada":
        cur.execute(
            "UPDATE estoque SET quantidade = quantidade + %s WHERE nome = %s",
            (quantidade, nome),
        )
        tipo = "Entrada"
    else:
        # Só retira se houver quantidade suficiente (evita estoque negativo)
        cur.execute(
            "UPDATE estoque SET quantidade = quantidade - %s "
            "WHERE nome = %s AND quantidade >= %s",
            (quantidade, nome, quantidade),
        )
        tipo = "Saída"

    if cur.rowcount == 0:
        cur.execute("SELECT 1 FROM estoque WHERE nome = %s LIMIT 1", (nome,))
        return "insuficiente" if cur.fetchone() else "nao_encontrado"

    registrar_historico(cur, nome, tipo, quantidade)
    return None


def extensao_permitida(nome_arquivo):
    return "." in nome_arquivo and nome_arquivo.rsplit(".", 1)[1].lower() in EXTENSOES_OK


def salvar_foto(arquivo_storage):
    """Salva a foto enviada pelo formulário com nome único. Devolve o nome salvo ou None."""
    if not (arquivo_storage and arquivo_storage.filename
            and extensao_permitida(arquivo_storage.filename)):
        return None
    nome = f"{uuid.uuid4().hex}_{secure_filename(arquivo_storage.filename)}"
    arquivo_storage.save(os.path.join(PASTA_UPLOAD, nome))
    return nome


def salvar_foto_base64(texto_base64, nome_original=""):
    """Salva foto enviada pelo app em base64. Devolve o nome salvo ou levanta ValueError."""
    if "," in texto_base64[:100]:  # remove o prefixo "data:image/jpeg;base64,"
        texto_base64 = texto_base64.split(",", 1)[1]
    try:
        conteudo = base64.b64decode(texto_base64, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("Foto inválida")

    extensao = os.path.splitext(secure_filename(nome_original or ""))[1].lower()
    if extensao.lstrip(".") not in EXTENSOES_OK:
        extensao = ".jpg"

    nome = uuid.uuid4().hex + extensao
    with open(os.path.join(PASTA_UPLOAD, nome), "wb") as arquivo:
        arquivo.write(conteudo)
    return nome


def apagar_foto(nome):
    if nome:
        try:
            os.remove(os.path.join(PASTA_UPLOAD, nome))
        except OSError:
            pass


def ler_inteiro(valor):
    """Converte para int ou devolve None se não for número inteiro."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def ler_decimal(valor):
    """Converte para Decimal (aceita vírgula) ou devolve None."""
    try:
        return Decimal(str(valor).replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


# ---------------------------------------------------------------
# ROTAS DO SITE
# ---------------------------------------------------------------
# 1. Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_digitado = request.form.get("username")
        senha_digitada = request.form.get("password")

        try:
            with banco(dictionary=True, commit=True) as cur:
                encontrado = verificar_login(cur, usuario_digitado, senha_digitada)
                if encontrado:
                    iniciar_sessao(encontrado)
                    registrar_historico(cur, "-", "Login", 0)  # registra o login no relatório
        except mysql.connector.Error:
            return render_template("login.html", erro="Erro ao conectar ao banco de dados.")

        if not encontrado:
            return render_template("login.html", erro="Usuário ou senha incorretos!")

        return pagina_inicial()

    return render_template("login.html")


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


# 2. Início do administrador
@app.route("/inicio")
@admin_obrigatorio
def inicio_admin():
    try:
        return render_template("inicio.html", itens=buscar_estoque())
    except mysql.connector.Error as erro:
        return f"Erro ao carregar o estoque: {erro}"


# 3. Início do usuário comum
@app.route("/inicio-usuario")
@login_obrigatorio
def inicio_usuario():
    try:
        return render_template("inicio.usuario.html", itens=buscar_estoque())
    except mysql.connector.Error as erro:
        return f"Erro ao carregar o estoque do usuário: {erro}"


# 4. Adicionar item
@app.route("/adicionar_estoque", methods=["GET"])
@login_obrigatorio
def estoque():
    return render_template("adicionar_estoque.html")


@app.route("/cadastrar_item", methods=["POST"])
@login_obrigatorio
def cadastrar_item():
    nome_item = request.form.get("nome_item")
    categoria = request.form.get("categoria")
    funcao = request.form.get("funcao")
    quantidade = ler_inteiro(request.form.get("quantidade"))
    valor = ler_decimal(request.form.get("valor"))
    foto = request.files.get("foto")

    if not nome_item or quantidade is None or quantidade < 0 or valor is None or valor < 0:
        return "Dados inválidos! Informe nome, quantidade (inteiro) e valor (número), ambos maiores ou iguais a 0."

    nome_foto = salvar_foto(foto)  # só salva depois de validar os dados

    try:
        with banco(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO estoque (nome, categoria, funcao, quantidade, valor, foto)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (nome_item, categoria, funcao, quantidade, valor, nome_foto),
            )
            registrar_historico(cur, nome_item, "Cadastro", quantidade)
        return pagina_inicial()
    except mysql.connector.Error as erro:
        apagar_foto(nome_foto)  # não deixa arquivo órfão
        return f"Erro ao cadastrar item: {erro}"


# 5. Entrada / saída de estoque
@app.route("/retirar", methods=["GET", "POST"])
@login_obrigatorio
def retirar():
    if request.method == "POST":
        operacao = request.form.get("operacao")  # 'Entrada' ou 'Saida'
        nome = request.form.get("nomeItem")
        quantidade = ler_inteiro(request.form.get("quantidade"))

        if quantidade is None:
            return "Quantidade inválida!"
        if operacao not in ("Entrada", "Saida") or not nome or quantidade <= 0:
            return "Dados inválidos!"

        try:
            with banco(commit=True) as cur:
                problema = movimentar_estoque(cur, operacao, nome, quantidade)
        except mysql.connector.Error as erro:
            return f"Erro ao atualizar o estoque: {erro}"

        if problema == "nao_encontrado":
            return "Item não encontrado!"
        if problema == "insuficiente":
            return "Quantidade insuficiente em estoque!"

        return pagina_inicial()

    return render_template("retirar.html")


# 6. Usuários (somente admin)
@app.route("/usuarios", methods=["GET", "POST"])
@admin_obrigatorio
def usuarios():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        funcao = request.form.get("funcao")

        if not usuario or not senha_valida(senha) or funcao not in FUNCOES_VALIDAS:
            return "Dados inválidos! A senha deve ter no máximo 72 caracteres."

        try:
            with banco(commit=True) as cur:
                cur.execute(
                    "INSERT INTO usuarios (usuario, senha, funcao) VALUES (%s, %s, %s)",
                    (usuario, gerar_hash(senha), funcao),  # salva o hash
                )
                registrar_historico(cur, f"Novo usuário: {usuario}", "Cadastro de usuário", 0)
            return redirect(url_for("usuarios"))
        except mysql.connector.IntegrityError:
            return "Esse usuário já existe!"
        except mysql.connector.Error as erro:
            return f"Erro ao cadastrar o usuário: {erro}"

    return render_template("usuarios.html")


# 7. Histórico (relatório de movimentações)
@app.route("/historico")
@login_obrigatorio
def historico():
    try:
        return render_template("historico.html", movimentacoes=buscar_historico())
    except mysql.connector.Error as erro:
        return f"Erro ao carregar o histórico: {erro}"


# 8. Teste de conexão
@app.route("/conexao")
def conexao():
    try:
        obter_conexao().close()
        return jsonify({"status": "ok"}), 200
    except mysql.connector.Error:
        return jsonify({"status": "erro"}), 500


# ---------------------------------------------------------------
# API (usada pelo app / mobile) - mesma tabela 'estoque' do site
# Colunas: id, nome, categoria, funcao, quantidade, valor, foto
# ---------------------------------------------------------------
# Protege todas as rotas /api/ (menos o login). /api/usuarios é só para admin.
# O app precisa enviar o cookie de sessão recebido no /api/login.
@app.before_request
def proteger_api():
    if not request.path.startswith("/api/") or request.path == "/api/login":
        return None
    if "usuario_id" not in session:
        return jsonify({"erro": "Não autenticado."}), 401
    if request.path.startswith("/api/usuarios") and not eh_admin():
        return jsonify({"erro": "Apenas administradores."}), 403
    return None


# Erros de banco nas rotas /api/ voltam como JSON
@app.errorhandler(mysql.connector.Error)
def erro_banco(erro):
    if not request.path.startswith("/api/"):
        raise erro
    return jsonify({"erro": f"Erro no banco de dados: {erro}"}), 500


def converter_item(item):
    item["valor"] = float(item["valor"] or 0)
    return item


# POST /api/login -> {"username": "...", "password": "..."}  (aceita também "nome"/"senha")
@app.route("/api/login", methods=["POST"])
def api_login():
    dados = request.get_json(silent=True) or request.form
    usuario = dados.get("username") or dados.get("nome")
    senha = dados.get("password") or dados.get("senha")

    with banco(dictionary=True, commit=True) as cur:
        encontrado = verificar_login(cur, usuario, senha)
        if encontrado:
            iniciar_sessao(encontrado)
            registrar_historico(cur, "-", "Login", 0)

    if not encontrado:
        return jsonify({"erro": "Usuário ou senha incorretos."}), 401

    return jsonify({
        "id": encontrado["id"],
        "usuario": encontrado["usuario"],
        "funcao": encontrado["funcao"],
    }), 200


# GET /api/estoque (e /api/itens, mesmo resultado)  -> opcional: ?q=texto
@app.route("/api/estoque", methods=["GET"])
@app.route("/api/itens", methods=["GET"])
def api_listar_estoque():
    busca = request.args.get("q", "").strip()
    if not busca:
        return jsonify([converter_item(i) for i in buscar_estoque()]), 200

    padrao = f"%{busca}%"
    with banco(dictionary=True) as cur:
        cur.execute(
            "SELECT id, nome, categoria, funcao, quantidade, valor, foto FROM estoque "
            "WHERE nome LIKE %s OR categoria LIKE %s ORDER BY id ASC",
            (padrao, padrao),
        )
        itens = cur.fetchall()
    return jsonify([converter_item(i) for i in itens]), 200


# GET /api/estoque/<id>
@app.route("/api/estoque/<int:estoque_id>", methods=["GET"])
@app.route("/api/itens/<int:estoque_id>", methods=["GET"])
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


# POST /api/estoque -> {"nome", "valor", "quantidade", "categoria", "funcao",
#                       "foto" (nome do arquivo) OU "foto_base64" + "foto_nome"}
@app.route("/api/estoque", methods=["POST"])
@app.route("/api/itens", methods=["POST"])
def api_adicionar_estoque():
    dados = request.get_json(silent=True) or request.form

    nome = dados.get("nome")
    valor = ler_decimal(dados.get("valor", dados.get("preco")))  # aceita "preco" também
    quantidade = ler_inteiro(dados.get("quantidade"))
    categoria = dados.get("categoria")
    funcao = dados.get("funcao")
    foto = dados.get("foto")
    foto_base64 = dados.get("foto_base64")

    if not nome or valor is None or quantidade is None:
        return jsonify({"erro": "Campos obrigatórios: nome, valor e quantidade."}), 400
    if quantidade < 0 or valor < 0:
        return jsonify({"erro": "Quantidade e valor não podem ser negativos."}), 400

    foto_salva = None
    if foto_base64:
        try:
            foto_salva = salvar_foto_base64(foto_base64, dados.get("foto_nome"))
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        foto = foto_salva

    try:
        with banco(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO estoque (nome, categoria, funcao, quantidade, valor, foto)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (nome, categoria, funcao, quantidade, valor, foto),
            )
            novo_id = cur.lastrowid
            registrar_historico(cur, nome, "Cadastro", quantidade)
    except mysql.connector.Error:
        apagar_foto(foto_salva)
        raise

    return jsonify({"mensagem": "Item adicionado com sucesso.", "id": novo_id}), 201


# POST /api/estoque/movimentar -> {"operacao": "Entrada"|"Saida", "nome": "...", "quantidade": 5}
@app.route("/api/estoque/movimentar", methods=["POST"])
@app.route("/api/movimentacoes", methods=["POST"])
def api_movimentar_estoque():
    dados = request.get_json(silent=True) or request.form

    operacao = dados.get("operacao")
    nome = dados.get("nome")
    quantidade = ler_inteiro(dados.get("quantidade")) or 0

    if operacao not in ("Entrada", "Saida") or not nome or quantidade <= 0:
        return jsonify({"erro": "Informe operacao ('Entrada' ou 'Saida'), nome e quantidade maior que 0."}), 400

    with banco(dictionary=True, commit=True) as cur:
        problema = movimentar_estoque(cur, operacao, nome, quantidade)
        estoque_atual = None
        if problema is None:
            cur.execute("SELECT quantidade FROM estoque WHERE nome = %s LIMIT 1", (nome,))
            estoque_atual = cur.fetchone()["quantidade"]

    if problema == "nao_encontrado":
        return jsonify({"erro": "Item não encontrado."}), 404
    if problema == "insuficiente":
        return jsonify({"erro": "Estoque insuficiente."}), 409

    return jsonify({
        "mensagem": f"{operacao} registrada com sucesso.",
        "estoque_atual": estoque_atual,
    }), 200


# GET /api/historico  -> opcional: ?limit=100 (máximo 500)
@app.route("/api/historico", methods=["GET"])
def api_historico():
    limite = min(max(request.args.get("limit", 100, type=int), 1), 500)
    return jsonify(buscar_historico(limite)), 200


# GET /api/usuarios -> lista usuários (sem senha) - só admin
@app.route("/api/usuarios", methods=["GET"])
def api_listar_usuarios():
    with banco(dictionary=True) as cur:
        cur.execute("SELECT id, usuario, funcao FROM usuarios ORDER BY usuario")
        lista = cur.fetchall()
    return jsonify(lista), 200


# POST /api/usuarios -> {"usuario": "...", "senha": "...", "funcao": "admin"|"usuario"} - só admin
@app.route("/api/usuarios", methods=["POST"])
def api_cadastrar_usuario():
    dados = request.get_json(silent=True) or request.form

    usuario = dados.get("usuario")
    senha = dados.get("senha")
    funcao = dados.get("funcao") or "usuario"

    if not usuario or not senha or funcao not in FUNCOES_VALIDAS:
        return jsonify({"erro": "Informe usuario, senha e funcao ('admin' ou 'usuario')."}), 400
    if not senha_valida(senha):
        return jsonify({"erro": "A senha deve ter no máximo 72 caracteres."}), 400

    try:
        with banco(commit=True) as cur:
            cur.execute(
                "INSERT INTO usuarios (usuario, senha, funcao) VALUES (%s, %s, %s)",
                (usuario, gerar_hash(senha), funcao),  # salva o hash
            )
            novo_id = cur.lastrowid
            registrar_historico(cur, f"Novo usuário: {usuario}", "Cadastro de usuário", 0)
    except mysql.connector.IntegrityError:
        # a coluna 'usuario' é UNIQUE no banco
        return jsonify({"erro": "Esse usuário já existe."}), 409

    return jsonify({"mensagem": "Usuário cadastrado com sucesso.", "id": novo_id}), 201


# Cria a tabela de histórico, converte senhas antigas e cria o admin ao iniciar
preparar_banco()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1", host="0.0.0.0", port=5000)