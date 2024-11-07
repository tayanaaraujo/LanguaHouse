# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from config import DB_CONFIG
import secrets

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

#Cadastro de Usuario
@app.route('/usuarios/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        data_nasc = request.form['data_nasc']
        senha = request.form['senha']
        cidade = request.form['cidade']
        estado = request.form['estado']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (nome, email, data_nasc, senha, cidade, estado) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nome, email, data_nasc, senha, cidade, estado))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))

    
    return render_template('usuarios/create.html')

#Login
@app.route('/usuarios/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obter os dados do formulário
        email = request.form['email']
        password = request.form['password']

        # Conectar ao banco de dados
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        # Verificar se o usuário existe e se a senha é correta
        if user and user[4] == password:  # user[4] contém a senha (ajuste conforme sua estrutura de tabela)
            # Salvar as informações do usuário na sessão
            session['user_id'] = user[0]  # ID do usuário (coluna 0)
            session['user_email'] = user[2]  # Email do usuário (coluna 2)

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
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redireciona para o login se o usuário não estiver logado

    # Aqui você deve passar o usuário para o template 'perfil.html'
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()

    return render_template('usuarios/perfil.html', user=user)
    
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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        data_nasc = request.form['data_nasc']
        senha = request.form['senha']
        cidade = request.form['cidade']
        estado = request.form['estado']

        cur.execute("UPDATE usuario SET nome=%s, email=%s, data_nasc=%s, senha=%s, cidade=%s, estado=%s WHERE cod_usuario=%s",
                    (nome, email, data_nasc, senha, cidade, estado, id))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))

    cur.close()
    return render_template('update.html', usuario=usuario)


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