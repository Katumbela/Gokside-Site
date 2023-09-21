# -*- coding:utf-8 -*-
###
# --------------------------------------------------------------
#
# Modified Date: Thursday, 11th June 2020 9:49:12 pm
# Modified By: Ritesh Singh
#
# --------------------------------------------------------------
###


from email.header import decode_header
import sqlite3
from flask import Flask, flash, render_template, request, redirect, url_for
import logging, logging.config
import sys
import imaplib
import re
import email
import time
import config
from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_de_dados.db'
app.config['SECRET_KEY'] = 'Gokside_2023_katumbela'  # Substitua com uma chave secreta forte


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# login_manager = LoginManager()
# login_manager.init_app(app)  # Onde 'app' é a instância do Flask

# Função para criar o banco de dados SQLite
# def criar_banco_de_dados():
#     connection = sqlite3.connect('seu_banco_de_dados.db')
#     connection.close()

# # Rota para criar o banco de dados (chame-a uma vez para criar o arquivo do banco de dados)
# @app.route('/banco', methods=['GET'])
# def criar_banco_de_dados_rota():
#     criar_banco_de_dados()
#     return 'Banco de dados criado com sucesso!'


class User(db.Model):
    
    senha_hash = db.Column(db.String(220), nullable=False)
    senha = db.Column(db.String(220), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(800), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    empresa = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    estado_conta = db.Column(db.String(20), default='ativo')  # Pode ser 'ativo' ou 'inativo'
    plano = db.Column(db.String(200))
    estado_pagamento = db.Column(db.String(20), default='pendente')  # Pode ser 'pendente', 'pago', etc.
    data_criacao_conta = db.Column(db.DateTime, default=db.func.current_timestamp())
    api_key = db.Column(db.String(94), unique=True)



class EmailRead:
           
    def read_emails(self):
        try:
            mail = imaplib.IMAP4_SSL(self.smtp_server)
            mail.login(self.email_address, self.password)
            mail.select(self.label, readonly=True)
            result, data = mail.uid('search', None, self.command)
            if result == 'OK':
                self.logger.info('Processing mailbox...')
            else:
                self.logger.error("Reading error", exc_info=True)
                sys.exit(0)
            
            ids = data[0].split()
            if len(ids) == 0:
                self.logger.info("No email found in selected dates.")

            emails = []  # Lista para armazenar os e-mails

            for x in ids:
                result, data = mail.uid('fetch', x, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')

                body = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        charset = part.get_content_charset()
                        body = part.get_payload(decode=True).decode(charset or 'utf-8', 'ignore')

                emails.append({"subject": subject, "body": body})

            return emails  # Retorna a lista de e-mails
        except Exception as e:
            self.logger.error("Error in reading your %s label: %s" % (self.label, str(e)), exc_info=True)
            return []  # Retorna uma lista vazia em caso de erro

    def __init__(self):
        logging.config.fileConfig('log.ini')
        self.logger = logging.getLogger('sLogger')
        self.subject = []
        self.smtp_server = "imap.gmail.com"
        self.email_address = config.email
        self.password = config.password
        self.label = '"'+config.label+'"'
        self.from_date = config.from_date
        self.to_date = config.to_date
        self.command = '(SINCE "' + self.from_date + '" BEFORE "' + self.to_date + '")'
        



@app.route('/')
def index():
    r1 = EmailRead()
    data = r1.read_emails()
    return render_template('index.html', emails=data)

@app.route('/pagina/<parametro>')
def pagina(parametro):
    if parametro == "pack1":
        pacote = "PACOTE INDIVIDUAL"
    elif parametro == "pack2":
        pacote = "PACOTE BUISINESS"
    elif parametro == "pack3":
        pacote = "PACOTE GOK"
    return render_template('cadastro.html', parametro=pacote)


@app.route('/inbox')
def inbox():
    r1 = EmailRead()
    data = r1.read_emails()
    return render_template('inbox.html', emails=data)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
# @login_required
def profile(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        # Atualize as informações do usuário aqui
        user.nome = request.form['nome']
        user.email = request.form['email']
        user.empresa = request.form['empresa']
        user.telefone = request.form['telefone']
        # Atualize outros campos conforme necessário
        db.session.commit()
    return render_template('profile.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha_hash, senha):
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('perfil'))
        else:
            flash('Credenciais   inválidas.   Por favor,   tente novamente.', 'danger')
    return render_template('login.html')


@app.route('/user/dashboard')
# @login_required
def perfil():
    return render_template('dashboard.html', user=current_user)


@app.route('/user/dash_email')
# @login_required
def dash_email():
    return render_template('dash_email.html', user=current_user)


@app.route('/user/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        empresa = request.form['empresa']
        plano = request.form['plano']
        telefone = request.form['telefone']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha, method='sha256')
        user = User(nome=nome, api_key=senha_hash, empresa=empresa, telefone=telefone, senha=senha, plano=plano, email=email, senha_hash=senha_hash)
        db.session.add(user)
        db.session.commit()
        flash('Conta criada com sucesso! Faça login para acessar.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)