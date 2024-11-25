# app.py
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from config import DB_CONFIG
import secrets
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configuração do banco de dados
app.config['MYSQL_HOST'] = DB_CONFIG['MYSQL_HOST']
app.config['MYSQL_USER'] = DB_CONFIG['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = DB_CONFIG['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = DB_CONFIG['MYSQL_DB']

# Inicializando o MySQL
mysql = MySQL(app)

app.secret_key = '9b4e5417c43ff5c1d2168b1677b1957e'

@app.route('/')
def index():
    return render_template('index.html')

#Cadastro
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
            cur.close()

            # Flash de mensagem de sucesso
            flash('Usuário criado com sucesso!', 'success')
            
            
        
        except Exception as e:
            flash(f'Erro ao criar usuário: {str(e)}', 'danger')
            return redirect(url_for('create'))

    return render_template('usuarios/create.html')

#Login
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
            # Se a autenticação falhar
            flash('E-mail ou senha inválidos. Tente novamente.', 'error')
            return redirect(url_for('login'))

    return render_template('usuarios/login.html')

# Rota para a página de perfil
@app.route('/usuarios/perfil')
def perfil():
    user_id = session.get('user_id')
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redireciona para o login se o usuário não estiver logado

    # Aqui você deve passar o usuário para o template 'perfil.html'
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
    # Redireciona para a página de login após o logout
    return redirect(url_for('index'))

#Atualizar dados do usuario
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Pegue o usuário do banco de dados
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
            flash("Senha atual incorreta", "error")  # Flash para mensagem de erro
            return render_template('usuarios/update.html', usuario=usuario)
        
        # Se a senha for correta, atualize os dados
        nova_senha = request.form['nova_senha']
        if nova_senha:  # Verifica se uma nova senha foi fornecida
            nova_senha_hash = generate_password_hash(nova_senha)  # Gera o hash da nova senha
        else:
            nova_senha_hash = usuario['senha']  # Se não for fornecida nova senha, mantém a antiga

        # Atualiza os dados no banco
        cur.execute("""
            UPDATE usuario 
            SET nome=%s, email=%s, data_nasc=%s, senha=%s, cidade=%s, estado=%s 
            WHERE cod_usuario=%s
        """, (nome, email, data_nasc, nova_senha_hash, cidade, estado, id))

        mysql.connection.commit()
        cur.close()

        # Após a atualização, redireciona para a página de perfil
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for('perfil'))  # Redireciona para a rota do perfil

    cur.close()
    return render_template('usuarios/update.html', usuario=usuario)


#Pesquisar usuarios
@app.route('/usuarios/read', methods=['GET', 'POST'] )
def read():
    return render_template('usuarios/read.html')

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

    if not idioma:
        flash('Nenhum idioma encontrado para este usuário.', 'danger')
        return redirect(url_for('perfil_idioma', id=id))
    
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
@app.route('/grupos/todos_grupos/<int:id>', methods=['GET'])
def todos_grupos(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('index'))  
    
    cur.close()

    return render_template('grupos/todos_grupos.html', usuario=usuario)

if __name__ == '__main__':
    app.run(debug=True)