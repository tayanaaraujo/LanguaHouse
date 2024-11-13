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
            return redirect(url_for('perfil'))
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
    cur = mysql.connection.cursor()
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
@app.route('/usuarios/login', methods=['GET', 'POST'] )
def delete_usuario():
    return render_template('usuarios/delete.html')

#Forum grupos
@app.route('/grupos/forum', methods=['GET', 'POST'] )
def forum():
    return render_template('/grupos/forum.html')

#Idiomas
@app.route('/idiomas/cadastro', methods=['GET', 'POST'] )
def cad_idioma():
    return render_template('idiomas/cadastro_idioma.html')


if __name__ == '__main__':
    app.run(debug=True)