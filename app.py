# app.py
import MySQLdb
import secrets
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from config import DB_CONFIG
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configuração do banco de dados
app.config['MYSQL_HOST'] = DB_CONFIG['MYSQL_HOST']
app.config['MYSQL_USER'] = DB_CONFIG['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = DB_CONFIG['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = DB_CONFIG['MYSQL_DB']

# Inicializando o MySQL
mysql = MySQL(app)

#
app.secret_key = '9b4e5417c43ff5c1d2168b1677b1957e'

@app.route('/')
def index():
    return render_template('index.html')

# Cadastro usuário
@app.route('/usuarios/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        data_nasc = request.form['data_nasc']
        senha = request.form['senha']
        cidade = request.form['cidade']
        estado = request.form['estado']
        
        senha_hash = generate_password_hash(senha)

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO usuario (nome, email, data_nasc, senha, cidade, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, email, data_nasc, senha_hash, cidade, estado))
            mysql.connection.commit()
            
            # Agora pega o ID do usuário recém-criado
            user_id = cur.lastrowid  # Isso pega o ID gerado pelo banco

            # Definir o user_id na sessão para "logar" o usuário
            session['user_id'] = user_id
            
            cur.close()

            return redirect(url_for('forum')) 

        except Exception as e:
            # Em caso de erro, redireciona de volta para o cadastro
            return redirect(url_for('create'))

    return render_template('usuarios/create.html')

# Endpoint para buscar os estados
@app.route('/api/estados', methods=['GET'])
def get_estados():
    try:
        # Fazendo a requisição para a API de estados
        response = requests.get('https://brasilapi.com.br/api/ibge/uf/v1/')
        response.raise_for_status()  # Levanta um erro se a requisição falhar
        return jsonify(response.json())  # Retorna os estados como JSON
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Retorna o erro se ocorrer algum problema
    
@app.route('/api/cidades/<estado>', methods=['GET'])
def get_cidades(estado):
    try:
        # Fazendo a requisição para a API de cidades com o estado
        response = requests.get(f'https://brasilapi.com.br/api/ibge/municipios/v1/{estado}')
        response.raise_for_status()  # Levanta um erro se a requisição falhar
        return jsonify(response.json())  # Retorna as cidades como JSON
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Retorna o erro se ocorrer algum problema

#Login usuario
@app.route('/usuarios/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obter os dados do formulário
        email = request.form['email']
        password = request.form['password']

        # Conectar ao banco de dados
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        # Verificar se o usuário existe e se a senha é correta
        if user and check_password_hash(user['senha'], password):  # Verifica o hash da senha
            # Salvar as informações do usuário na sessão
            session['user_id'] = user['cod_usuario']  # ID do usuário (ajustado para o nome correto da coluna)
            session['user_email'] = user['email']  # Email do usuário (ajustado para o nome correto da coluna)

            # Redireciona para a página de perfil após login
            return redirect(url_for('forum'))
        else:
            flash('Usuário não encontrado.', 'danger')
            return redirect(url_for('login'))

    return render_template('usuarios/login.html')

# Rota para a página de perfil
@app.route('/usuarios/perfil')
def perfil():
    user_id = session.get('user_id')
    if 'user_id' not in session:
        return redirect(url_for('login'))  

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()

    return render_template('usuarios/perfil.html', user=user, user_id=user_id)
    
#LogOut
@app.route('/logout')
def logout():
    # Remove informações da sessão para efetuar o logout
    session.pop('user_id', None)
    session.pop('user_email', None)
    return redirect(url_for('index'))

#Pesquisar usuarios
# @app.route('/usuarios/read', methods=['GET', 'POST'])
# def read():
#     # Verifica se o usuário está logado
#     if 'user_id' not in session:
#         return redirect(url_for('login'))  

#     user_id = session['user_id']
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
#     # Obtém os dados do usuário logado
#     cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (user_id,))
#     user = cur.fetchone()

#     # Lida com a pesquisa
#     search_query = request.args.get('search', '')  # Obtém o termo de pesquisa do campo de busca
#     if search_query:
#         # Filtra os usuários por categoria
#         cur.execute("""
#             SELECT * FROM usuario
#             WHERE nome LIKE %s OR email LIKE %s JOIN idioma WHERE categoria LIKE %s
#         """, (f"%{search_query}%", f"%{search_query}%"))
#     else:
#         # Retorna todos os usuários se não houver pesquisa
#         cur.execute("SELECT * FROM usuario")
    
#     users = cur.fetchall()  # Recupera os resultados da consulta
#     cur.close()

#     # Renderiza a página com os usuários e o termo de pesquisa
#     return render_template('usuarios/read.html', user=user, users=users, search_query=search_query)

#Atualizar dados do usuario
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        return "Usuário não encontrado", 404

    # Se o formulário for enviado via POST
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nome = request.form['nome']
        email = request.form['email']
        data_nasc = request.form['data_nasc']
        cidade = request.form['cidade']
        estado = request.form['estado']
        
        # Verifica se a senha atual fornecida corresponde ao hash da senha no banco
        if not check_password_hash(usuario['senha'], senha_atual):
            flash("Senha atual incorreta", "error")  
            return render_template('usuarios/update.html', usuario=usuario)
        
        # Se a senha for correta, atualize os dados
        nova_senha = request.form['nova_senha']
        if nova_senha:  
            nova_senha_hash = generate_password_hash(nova_senha)  # Gera o hash da nova senha
        else:
            nova_senha_hash = usuario['senha']  

        # Atualiza os dados no banco
        cur.execute("""
            UPDATE usuario 
            SET nome=%s, email=%s, data_nasc=%s, senha=%s, cidade=%s, estado=%s 
            WHERE cod_usuario=%s
        """, (nome, email, data_nasc, nova_senha_hash, cidade, estado, id))

        mysql.connection.commit()
        cur.close()

        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for('perfil'))  # Redireciona para a rota do perfil

    cur.close()
    return render_template('usuarios/update.html', usuario=usuario)

#Deletar usuario
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        return "Usuário não encontrado", 404

    if request.method == 'POST':
        senha_atual = request.form['senha_atual']

        if not check_password_hash(usuario['senha'], senha_atual):
            flash("Senha atual incorreta", "error")
            return render_template('usuarios/delete.html', usuario=usuario)

        cur.execute("DELETE FROM usuario WHERE cod_usuario = %s", (id,))
        mysql.connection.commit()
        cur.close()

        flash("Usuário deletado com sucesso", "success")
        return redirect(url_for('index'))

    return render_template('usuarios/delete.html', usuario=usuario)

# CAMINHOS DO FORUM 
@app.route('/mensagens')
def mensagens():
    # Lógica para mostrar as mensagens
    return render_template('mensagens.html')

@app.route('/notificações')
def notificações():
    # Lógica para mostrar as notificações
    return render_template('notificações.html')

#Idiomas
@app.route('/idiomas/<int:id>', methods=['GET', 'POST'] )
def perfil_idioma(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('perfil'))  
    
    # Verificar se o idioma pertence ao usuário (usando a coluna 'linguagem' para identificar)
    cur.execute("""
        SELECT i.* 
        FROM idioma i
        LEFT JOIN usuario u ON i.cod_usuario = u.cod_usuario
        WHERE i.cod_usuario = %s
    """, (id,))
    idioma = cur.fetchall()  # Pega todos os idiomas do usuário

    cur.close()

    return render_template('idiomas/idioma_perfil.html', usuario=usuario, idioma=idioma)

@app.route('/idiomas/cadastro/<int:id>', methods=['GET', 'POST'] )
def cad_idioma(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Verificar se o usuário existe
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('perfil'))  # Redirecione para uma rota apropriada

    if request.method == 'POST':
        linguagem = request.form['linguagem']
        nivel = request.form['nivel']
        categoria = request.form['categoria']
        cod_usuario = id

        try:
            # Verificar duplicidade
            cur.execute("""
                SELECT * FROM idioma 
                WHERE cod_usuario = %s AND linguagem = %s
            """, (cod_usuario, linguagem))
            idioma_existente = cur.fetchone()

            if idioma_existente:
                flash('Este idioma já foi cadastrado para o usuário.', 'warning')
                return redirect(url_for('cad_idioma', id=id))

            # Inserir novo idioma
            cur.execute("""
                INSERT INTO idioma (cod_usuario, nivel, linguagem, categoria)
                VALUES (%s, %s, %s, %s)
            """, (cod_usuario, nivel, linguagem, categoria))
            mysql.connection.commit()

            flash('Idioma cadastrado com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar idioma: {str(e)}', 'danger')
        finally:
            cur.close()
            return redirect(url_for('cad_idioma', id=id))

    return render_template('idiomas/cadastro_idioma.html')

#ATUALIZAR IDIOMA
@app.route('/idiomas/atualizar/<int:id>', methods=['GET', 'POST'])
def atual_idioma(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Verificar se o idioma pertence ao usuário (usando a coluna 'linguagem' para identificar)
    cur.execute("""
        SELECT i.* 
        FROM idioma i
        LEFT JOIN usuario u ON i.cod_usuario = u.cod_usuario
        WHERE i.cod_usuario = %s
    """, (id,))
    idioma = cur.fetchall()  # Pega todos os idiomas do usuário

    if not idioma:
        flash('Nenhum idioma encontrado para este usuário.', 'danger')
        return redirect(url_for('perfil', id=id))

    # Carregar o usuário
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchall()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('perfil', id=id))

    if request.method == 'POST':
        nivel = request.form['nivel']
        linguagem = request.form['linguagem']
        categoria = request.form['categoria']
        linguagem_selecionada = request.form['linguagem']  # Linguagem específica que o usuário selecionou para atualizar

        try:
            # Verificar se o idioma e a linguagem já estão cadastrados para o usuário
            cur.execute("""
                SELECT * 
                FROM idioma 
                WHERE cod_usuario = %s AND linguagem = %s
            """, (id, linguagem_selecionada))  # Verificando pela 'linguagem'
            idioma_existente = cur.fetchone()

            if not idioma_existente:
                flash('Idioma ou linguagem não encontrado para este usuário.', 'danger')
                return redirect(url_for('atual_idioma', id=id))

            # Atualizar idioma
            cur.execute("""
                UPDATE idioma 
                SET nivel = %s, linguagem = %s, categoria = %s
                WHERE cod_usuario = %s AND linguagem = %s
            """, (nivel, linguagem, categoria, id, linguagem_selecionada))
            mysql.connection.commit()

            flash('Idioma atualizado com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao atualizar idioma: {str(e)}', 'danger')
        finally:
            cur.close()
            return redirect(url_for('atual_idioma', id=id))

    # Passando as variáveis 'usuario' e 'idiomas' para o template
    return render_template('idiomas/atualizar_idioma.html', usuario=usuario, idioma=idioma)

#Deletar 
@app.route('/delete_idioma/<int:id>', methods=['GET', 'POST'])
def delete_idioma(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        return "Usuário não encontrado", 404

    if request.method == 'POST':
        linguagem = request.form['linguagem']
        senha_atual = request.form['senha_atual']

        if not check_password_hash(usuario['senha'], senha_atual):
            flash("Senha atual incorreta", "error")
            return render_template('usuarios/delete.html', usuario=usuario)

        cur.execute("DELETE FROM idioma WHERE cod_usuario = %s AND linguagem = %s", (id, linguagem))
        mysql.connection.commit()
        cur.close()

        #Deleta a participação no grupo
        cur.execute("DELETE FROM Integrante WHERE cod_usuario = %s", (id))
        mysql.connection.commit()
        cur.close()

        flash("Idioma deletado com sucesso", "success")

    return render_template('idiomas/deletar_idioma.html', usuario=usuario)

#Forum
@app.route('/grupos/forum', methods=['GET'])
def forum():
    user_id = session.get('user_id')
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redireciona para o login se o usuário não estiver logado

    # Conectar ao banco de dados
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Se o usuário estiver logado, buscar o nome no banco
    usuario_logado = None
    if user_id:
        cur.execute("SELECT nome FROM usuario WHERE cod_usuario = %s", (user_id,))
        usuario_logado = cur.fetchone()  # A variável agora tem o nome do usuário logado
        print(f"Usuário logado: {usuario_logado}")  # Debugging: Verifique o conteúdo de usuario_logado

    query = request.args.get('query', '')  # Pega o parâmetro da query, se houver

    # Se a busca não estiver vazia, buscar no banco de dados
    if query:
        cur.execute(""" 
            SELECT * FROM usuario
            WHERE nome LIKE %s OR email LIKE %s
        """, ('%' + query + '%', '%' + query + '%'))
    else:
        cur.execute("SELECT * FROM usuario")  # Caso contrário, traz todos os usuários

    usuarios = cur.fetchall()
    cur.close()

    # Retorna a página do fórum com os resultados da pesquisa
    return render_template('grupos/forum.html', usuarios=usuarios, query=query, 
                           usuario_logado=usuario_logado, user_id=user_id)

#Grupos
@app.route('/grupos/todos_grupos/<int:id>', methods=['GET', 'POST'])
def todos_grupos(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('index'))  
    
    query = request.args.get('query', '')  # Pega o parâmetro da query, se houver

    # Se a busca não estiver vazia, buscar no banco de dados
    if query:
        cur.execute("""
            SELECT * FROM grupo
            WHERE nome_grupo LIKE %s OR linguagem LIKE %s
        """, ('%' + query + '%', '%' + query + '%'))
    else:
        cur.execute("SELECT * FROM grupo")  # Caso contrário, traz todos os usuários
    grupos = cur.fetchall()
    cur.close()

    return render_template('grupos/todos_grupos.html', usuario=usuario, grupos=grupos)

@app.route('/grupos/cadastro_grupo/<int:id>', methods=['GET', 'POST'])
def cad_grupos(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Busca o usuário
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        cod_usuario = id
        nome_grupo = request.form['nome_grupo']
        linguagem = request.form['linguagem']
        descricao = request.form['descricao']

        try:
            # Verificar duplicidade na tabela idioma
            cur.execute("""
                SELECT cod_idioma FROM idioma 
                WHERE cod_usuario = %s AND linguagem = %s
            """, (cod_usuario, linguagem))
            idioma_existente = cur.fetchone()

            if not idioma_existente:
                flash('Idioma não encontrado para este usuário.', 'danger')
                return redirect(url_for('cad_grupos', id=id))

            # Inserir novo grupo
            cur.execute("""
                INSERT INTO grupo (cod_usuario, cod_idioma, nome_grupo, linguagem, descricao)
                VALUES (%s, %s, %s, %s, %s)
            """, (cod_usuario, idioma_existente['cod_idioma'], nome_grupo, linguagem, descricao))

            # Recuperar o ID do grupo recém-criado
            cod_grupo = cur.lastrowid

            # Inserir criador na tabela integrante
            cur.execute("""
                INSERT INTO integrante (cod_usuario, cod_grupo, data_entrada, status, papel)
                VALUES (%s, %s, CURDATE(), 'ativo', 'criador')
            """, (cod_usuario, cod_grupo))

            mysql.connection.commit()

            flash('Grupo cadastrado com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar grupo: {str(e)}', 'danger')
        finally:
            cur.close()
            return redirect(url_for('cad_grupos', id=id))

    return render_template('grupos/cadastro_grupo.html', usuario=usuario)

@app.route('/grupos/atualizar_grupo/<int:id>', methods=['GET', 'POST'])
def atual_grupos(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("""
        SELECT g.* 
        FROM grupo g
        LEFT JOIN usuario u ON g.cod_usuario = u.cod_usuario
        WHERE g.cod_usuario = %s
    """, (id,))
    grupo = cur.fetchall()  # Pega todos os idiomas do usuário

    if not grupo:
        flash('Nenhum grupo encontrado para este usuário.', 'danger')
        return redirect(url_for('forum'))

    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('forum', id=id))

    if request.method == 'POST':
        cod_usuario = id
        nome_grupo = request.form['nome_grupo']
        linguagem = request.form['linguagem']
        descricao = request.form['descricao']
 
        try:
            # Verificar se o grupo já está cadastrados para o usuário
            cur.execute("""
                SELECT * 
                FROM grupo 
                WHERE cod_usuario = %s AND nome_grupo = %s
            """, (id, nome_grupo))   
            grupo_existente = cur.fetchone()

            if not grupo_existente:
                flash('Grupo não encontrado para este usuário.', 'danger')
                return redirect(url_for('atual_grupos', id=id))

            # Atualizar grupo
            cur.execute("""
                UPDATE grupo 
                SET nome_grupo = %s, linguagem = %s, descricao = %s
                WHERE cod_usuario = %s AND nome_grupo = %s
            """, ( nome_grupo, linguagem, descricao, cod_usuario, grupo_existente['nome_grupo']))
            mysql.connection.commit()

            flash('Grupo atualizado com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao atualizar grupo: {str(e)}', 'danger')
        finally:
            cur.close()
            return redirect(url_for('atual_grupos', id=id))


    return render_template('grupos/atualizar_grupo.html', usuario=usuario)


@app.route('/grupos/deletar_grupo/<int:id>', methods=['GET', 'POST'])
def del_grupos(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        return "Usuário não encontrado", 404

    if request.method == 'POST':
        nome_grupo = request.form['nome_grupo']
        senha_atual = request.form['senha_atual']

        if not check_password_hash(usuario['senha'], senha_atual):
            flash("Senha atual incorreta", "error")
            return render_template('grupos/deletar_grupo.html', usuario=usuario)

        cur.execute("DELETE FROM grupo WHERE cod_usuario = %s AND nome_grupo = %s", (id, nome_grupo))
        mysql.connection.commit()
        cur.close()

        flash("Grupo deletado com sucesso", "success")

    return render_template('grupos/deletar_grupo.html', usuario=usuario)

@app.route('/grupos/entrar/<int:grupo_id>', methods=['POST'])
def entrar_grupo(grupo_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id = session['user_id']  # Assumindo que o usuário está logado e o ID está na sessão

    # Verificar se o usuário já é integrante
    cur.execute("""
        SELECT * FROM integrante WHERE cod_usuario = %s AND cod_grupo = %s
    """, (user_id, grupo_id))
    integrante = cur.fetchone()

    if integrante:
        flash('Você já é integrante deste grupo.', 'info')
    else:
        # Inserir usuário como integrante
        cur.execute("""
            INSERT INTO integrante (cod_usuario, cod_grupo, data_entrada, status, papel)
            VALUES (%s, %s, CURDATE(), 'ativo', 'membro')
        """, (user_id, grupo_id))
        mysql.connection.commit()
        flash('Você entrou no grupo com sucesso!', 'success')

    cur.close()
    return redirect(url_for('todos_grupos', id=user_id))

@app.route('/grupos/membros/<int:grupo_id>/<int:user_id>')
def ver_membros(grupo_id, user_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Obter o nome do grupo
    cur.execute("SELECT nome_grupo FROM grupo WHERE cod_grupo = %s", (grupo_id,))
    grupo = cur.fetchone()

    if not grupo:
        flash('Grupo não encontrado.', 'danger')
        return redirect(url_for('todos_grupos', id=user_id))

    # Obter os membros do grupo
    cur.execute("""
        SELECT u.nome, i.papel, i.status 
        FROM integrante i 
        JOIN usuario u ON i.cod_usuario = u.cod_usuario 
        WHERE i.cod_grupo = %s
    """, (grupo_id,))
    membros = cur.fetchall()
    cur.close()

    return render_template('grupos/membros.html', grupo=grupo, membros=membros, user_id=user_id)

# Rota para o teste de inglês
@app.route('/idiomas/teste_ingles')
def teste_ingles():
    return render_template('idiomas/teste_ingles.html')

# Rota para o teste de espanhol
@app.route('/idiomas/teste_espanhol')
def teste_espanhol():
    return render_template('idiomas/teste_espanhol.html')

#Dados FAQ 
faq_data = [
    {"pergunta": "O que é LanguaHouse?", "resposta": "LanguaHouse é uma plataforma para aprender idiomas."},
    {"pergunta": "Como funciona o teste de idiomas?", "resposta": "O teste avalia suas habilidades e sugere um nível."},
    {"pergunta": "A plataforma é gratuita?", "resposta": "Sim, a plataforma oferece recursos gratuitos."}
]

@app.route('/faq')
def faq():
    faq_items = [
        {"pergunta": "O que é LanguaHouse?", "resposta": "LanguaHouse é uma plataforma para aprender idiomas."},
        {"pergunta": "Como funciona o teste de idiomas?", "resposta": "O teste avalia suas habilidades e sugere um nível."},
        {"pergunta": "A plataforma é gratuita?", "resposta": "Sim, a plataforma oferece recursos gratuitos."}
    ]
    return render_template('faq.html', faq_items=faq_items)

@app.route('/test')
def test():
    return render_template('faq.html')


if __name__ == '__main__':
    app.run(debug=True)