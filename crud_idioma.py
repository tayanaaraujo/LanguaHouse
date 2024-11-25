# app.py
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from config import DB_CONFIG
import secrets
from werkzeug.security import check_password_hash, generate_password_hash

crud_idioma = Flask(__name__)

# Inicializando o MySQL
mysql = MySQL(crud_idioma)

crud_idioma.secret_key = '9b4e5417c43ff5c1d2168b1677b1957e'

#Idiomas
@crud_idioma.route('/idiomas/cadastro/<int:id>', methods=['GET', 'POST'] )
def cad_idioma(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Verificar se o usuário existe
    cur.execute("SELECT * FROM usuario WHERE cod_usuario = %s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('some_other_route'))  # Redirecione para uma rota apropriada

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
@crud_idioma.route('/idiomas/atualizar/<int:id>', methods=['GET', 'POST'])
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
@crud_idioma.route('/delete_idioma/<int:id>', methods=['GET', 'POST'])
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