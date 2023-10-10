# -*- coding:utf-8 -*-
###
# --------------------------------------------------------------
#
# Modified Date: Thursday, 11th June 2020 9:49:12 pm
# Modified By: Ritesh Singh
#
# --------------------------------------------------------------
###

import logging
logging.basicConfig(level=logging.DEBUG)  # Isso configura o nível de log para DEBUG

from email.header import decode_header
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import json
import logging
import sys
import imaplib
import re
import email
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Gokside_2023_katumbela'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Caminho para o arquivo JSON
USERS_JSON_FILE = 'users.json'

def load_users():
    try:
        with open(USERS_JSON_FILE, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}
    return users

def save_users(users):
    with open(USERS_JSON_FILE, 'w') as file:
        json.dump(users, file)

class User(UserMixin):
    def __init__(self, id, nome, email, senha_hash, empresa, telefone, estado_conta, plano, estado_pagamento, data_criacao_conta, api_key):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.empresa = empresa
        self.telefone = telefone
        self.estado_conta = estado_conta
        self.plano = plano
        self.estado_pagamento = estado_pagamento
        self.data_criacao_conta = data_criacao_conta
        self.api_key = api_key

# Função para encontrar um usuário por e-mail
def find_user_by_email(email):
    users = load_users()
    for user_id, user_data in users.items():
        if user_data['email'] == email:
            return User(user_id, **user_data)
    return None

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    user_data = users.get(str(user_id))
    if user_data:
        return User(user_id, **user_data)
    return None

class EmailRead:
           
    def read_emails(self):
        try:
            mail = imaplib.IMAP4_SSL(self.smtp_server)
            mail.login(self.email_address, self.password)
            mail.select(self.label, readonly=True)
            result, data = mail.uid('search', None, self.command)
            if result == 'OK':
                self.logger.info('Processing mailbox..')
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


@app.route('/user/inbox')
def inbox():
    r1 = EmailRead()
    data = r1.read_emails()
    return render_template('inbox.html', emails=data)


@login_manager.user_loader
def load_user(user_id):
    return User(user_id, '', '', '', '', '', '', '', '', '', '')  # Ajuste conforme necessário

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = load_user(user_id)
    if request.method == 'POST':
        # Atualize as informações do usuário aqui
        user.nome = request.form['nome']
        user.email = request.form['email']
        user.empresa = request.form['empresa']
        user.telefone = request.form['telefone']
        # Atualize outros campos conforme necessário
        users = load_users()
        users[str(user.id)] = {
            'nome': user.nome,
            'email': user.email,
            'senha_hash': user.senha_hash,
            'empresa': user.empresa,
            'telefone': user.telefone,
            'estado_conta': user.estado_conta,
            'plano': user.plano,
            'estado_pagamento': user.estado_pagamento,
            'data_criacao_conta': user.data_criacao_conta,
            'api_key': user.api_key
        }
        save_users(users)
    return render_template('profile.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = find_user_by_email(email)
        if user:
            logging.debug(f'Usuário encontrado: {user.email}')
            logging.debug(f'Senha do usuário: {user.senha_hash}')
            if check_password_hash(user.senha_hash, senha):
                login_user(user)
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('perfil'))
            else:
                flash('Senha incorreta. Por favor, tente novamente.', 'danger')
        else:
            flash('Usuário não encontrado. Por favor, tente novamente.', 'danger')
    return render_template('login.html')

@app.route('/user/dashboard')
@login_required
def perfil():
    return render_template('dashboard.html', user=current_user)


@app.route('/user/dash_email')
@login_required
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
        user_id = len(load_users()) + 1  # Gere um ID único
        user = User(user_id, nome, email, senha_hash, empresa, telefone, 'ativo', plano, 'pendente', 'alguma_data', 'alguma_api_key')
        users = load_users()
        users[str(user_id)] = {
            'nome': user.nome,
            'email': user.email,
            'senha_hash': user.senha_hash,
            'empresa': user.empresa,
            'telefone': user.telefone,
            'estado_conta': user.estado_conta,
            'plano': user.plano,
            'estado_pagamento': user.estado_pagamento,
            'data_criacao_conta': user.data_criacao_conta,
            'api_key': user.api_key
        }
        save_users(users)
        flash('Conta criada com sucesso! Faça login para acessar.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

# Função para lidar com erros 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('/404/index.html'), 404

# Rota padrão para erro 404
@app.route('/404')
def not_found():
    return render_template('/404/index.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
