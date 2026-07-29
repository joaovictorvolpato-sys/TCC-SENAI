from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'TCC_SENAI' 

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
        usuario_digitado = request.form.get('username')
        senha_digitada = request.form.get('password')

        try:
            conexao_bd = obter_conexao()
            cursor = conexao_bd.cursor(dictionary=True) 

            # Busca o usuário na tabela
            comando = "SELECT usuario, senha, funcao FROM usuarios WHERE usuario = %s"
            cursor.execute(comando, (usuario_digitado,))
            usuario_encontrado = cursor.fetchone()

            cursor.close()
            conexao_bd.close()

            # CORREÇÃO: Toda a validação só acontece se 'usuario_encontrado' NÃO for None
            if usuario_encontrado is not None:
                
                # Só tenta acessar o dicionário ['senha'] se o usuário existir
                if usuario_encontrado['senha'] == senha_digitada:
                    
                    session['usuario'] = usuario_encontrado['usuario']
                    session['funcao'] = usuario_encontrado['funcao']

                    # 🔀 REDIRECIONAMENTO CORRIGIDO E LIMPO:
                    if usuario_encontrado['funcao'] in ['Administrador', 'admin']:
                        return redirect(url_for('inicio_admin'))  # Vai para a def inicio_admin() -> abre inicio.html
                    else:
                        return redirect(url_for('inicio_usuario'))

            # Se o usuário for None OU se a senha estiver errada, cai aqui com segurança
            return "Usuário ou senha incorretos!"

        except mysql.connector.Error as erro:
            return f"Erro no banco de dados: {erro}"

    return render_template('login.html')


@app.route('/inicio')
def inicio_admin():
    # 1. Trava de segurança da sessão
    if 'usuario' in session and session.get('funcao') in ['Administrador', 'admin']:
        try:
            # 2. Conecta ao banco para buscar os itens do estoque
            conexao_bd = obter_conexao()
            cursor = conexao_bd.cursor(dictionary=True) # Importante: dictionary=True para o HTML ler os nomes das colunas
            
            comando_sql = "SELECT id, nome, categoria, funcao, quantidade, valor, foto FROM estoque"
            cursor.execute(comando_sql)
            itens_estoque = cursor.fetchall() # Guarda todos os itens cadastrados nesta lista

            cursor.close()
            conexao_bd.close()

            # 3. Envia a lista de itens para dentro do arquivo inicio.html
            return render_template('inicio.html', itens=itens_estoque)

        except mysql.connector.Error as erro:
            return f"Erro ao carregar o estoque: {erro}"
            
    # Se não tiver permissão ou não estiver logado, expulsa para o login
    return redirect(url_for('login'))




@app.route('/inicio-usuario')
def inicio_usuario():
    # 1. Verifica se o usuário comum está realmente logado
    if 'usuario' in session:
        try:
            conexao_bd = obter_conexao()
            
            # ATENÇÃO: Se no seu HTML você usa os números (item[1], item[2]), deixe os parênteses do cursor VAZIOS: cursor = conexao_bd.cursor()
            # Se no seu HTML você usa os nomes das colunas (item['nome']), deixe como está abaixo:
            cursor = conexao_bd.cursor(dictionary=True) 
            
            # 2. Puxa os dados atualizados do estoque no MySQL
            comando_sql = "SELECT id, nome, categoria, funcao, quantidade, valor, foto FROM estoque"
            cursor.execute(comando_sql)
            itens_estoque = cursor.fetchall()

            cursor.close()
            conexao_bd.close()

            # 3. Envia os dados para a página do usuário comum com o nome 'itens'
            return render_template('inicio.usuario.html', itens=itens_estoque)

        except mysql.connector.Error as erro:
            return f"Erro ao carregar o estoque do usuário: {erro}"
            
    return redirect(url_for('login'))



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

        # 🔀 CORREÇÃO DINÂMICA: Verifica quem cadastrou para mandar para a tela certa
        if 'funcao' in session and session.get('funcao') in ['Administrador', 'admin']:
            return redirect(url_for('inicio_admin')) # Se for admin, vai para inicio.html
        else:
            return redirect(url_for('inicio_usuario')) # Se for usuário comum, vai para inicio.usuario.html

    except mysql.connector.Error as erro:
        return f"Erro ao cadastrar item: {erro}"

@app.route('/retirar', methods=['GET', 'POST'])
def retirar():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # 1. Captura os dados do formulário HTML
        operacao = request.form.get('operacao') # Recebe 'Entrada' ou 'Saida'
        nome = request.form.get('nomeItem')
        quantidade = int(request.form.get('quantidade')) # Converte para número inteiro para fazer o cálculo

        try:
            conexao_bd = obter_conexao()
            cursor = conexao_bd.cursor()
            
            # 2. DECISÃO DINÂMICA: Define se vai SOMAR ou SUBTRAIR no banco de dados
            if operacao == 'Entrada':
                # Soma a nova quantidade à quantidade que já existe no banco
                comando = "UPDATE estoque SET quantidade = quantidade + %s WHERE nome = %s"
            else:
                # 💻 CORREÇÃO: Trocado 'quantity' por 'quantidade' (em português)
                comando = "UPDATE estoque SET quantidade = quantidade - %s WHERE nome = %s"


            # 3. Executa o comando no MySQL
            cursor.execute(comando, (quantidade, nome))
            conexao_bd.commit()

            cursor.close()
            conexao_bd.close()

            # 4. Redireciona o usuário para a página correta com base no cargo dele
            if session.get('funcao') in ['Administrador', 'admin']:
                return redirect(url_for('inicio_admin')) 
            else:
                return redirect(url_for('inicio_usuario')) 

        except mysql.connector.Error as erro:
            return f"Erro ao atualizar o estoque: {erro}"

    # Carrega a página HTML do formulário quando o usuário clica para entrar
    return render_template('retirar.html')


@app.route('/usuarios', methods=['POST', 'GET'])
def usuarios():

    if request.method == 'POST':
       usuario = request.form.get('usuario')
       senha = request.form.get('senha')
       funcao = request.form.get('funcao')

       try:
           conexao_bd = obter_conexao()
           cursor = conexao_bd.cursor()

           comando = "INSERT INTO usuarios (usuario, senha, funcao) VALUES (%s, %s, %s)"
           valores = (usuario, senha, funcao)
           cursor.execute(comando, valores)
           conexao_bd.commit()

           cursor.close()
           conexao_bd.close()

           return redirect(url_for('usuarios'))

       except mysql.connector.Error as erro:
           return f"Erro ao cadastrar o usuário: {erro}"

    return render_template('usuarios.html')

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