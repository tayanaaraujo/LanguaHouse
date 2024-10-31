# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from config import DB_CONFIG

app = Flask(__name__)

# Configuração do banco de dados
app.config['MYSQL_HOST'] = DB_CONFIG['MYSQL_HOST']
app.config['MYSQL_USER'] = DB_CONFIG['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = DB_CONFIG['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = DB_CONFIG['MYSQL_DB']

# Inicializando o MySQL
mysql = MySQL(app)

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


#Login de Usuario
@app.route('/usuarios/login', methods=['GET', 'POST'] )
def login():
    return render_template('usuarios/login.html')
 



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

#perfil do usuario
@app.route('/usuarios/perfil', methods=['GET', 'POST'] )
def perfil():
    return render_template('usuarios/perfil.html')

#Deletar usuario
@app.route('/usuarios/login', methods=['GET', 'POST'] )
def delete_usuario():
    return render_template('usuarios/delete.html')

#Forum grupos
@app.route('/grupos/forum', methods=['GET', 'POST'] )
def form():
    return render_template('/grupos/forum.html')

#Idiomas
@app.route('/idiomas/cadastro', methods=['GET', 'POST'] )
def cad_idioma():
    return render_template('idiomas/cadastro_idioma.html')


if __name__ == '__main__':
    app.run(debug=True)