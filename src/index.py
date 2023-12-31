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
from flask_mail import  Mail, Message
from flask import Flask, render_template, request, jsonify
from email.utils import formataddr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from collections import OrderedDict
from datetime import datetime

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

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'contact.diversishop@gmail.com'
app.config['MAIL_PASSWORD'] = 'niwe tbir noqh owxz'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Caminho para o arquivo JSON
USERS_JSON_FILE = 'users.json'

def save_users(users):
    with open(USERS_JSON_FILE, 'w') as file:
        json.dump(users, file)

def load_users():
    try:
        with open(USERS_JSON_FILE, 'r') as file:
            users = json.load(file, object_pairs_hook=OrderedDict)
    except FileNotFoundError:
        users = {}
    return users

class User(UserMixin):
    def __init__(self, id, nome, email, senha_hash, empresa, telefone, estado_conta, plano, estado_pagamento, data_criacao_conta, api_key, senha_app, email_pr):
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
        self.senha_app = senha_app
        self.email_pr = email_pr

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

    def read_spam_emails(self):
        try:
            mail = imaplib.IMAP4_SSL(self.smtp_server)
            self.logger.debug(f"Trying to login with email: {self.email_address}")
            mail.login(self.email_address, self.password)
            self.logger.debug(f"Login successful for email: {self.email_address}")

            # Substitua 'Spam' pelo nome real da sua caixa de spam
            mail.select("Spam", readonly=True)

            result, data = mail.uid('search', None, 'ALL')
            if result == 'OK':
                self.logger.info('Processing spam emails...')
            else:
                self.logger.error("Reading error", exc_info=True)
                sys.exit(0)

            ids = data[0].split()
            if len(ids) == 0:
                self.logger.info("No spam emails found.")

            emails = []

            self.logger.debug("Processing email IDs...")
            for x in ids:
                self.logger.debug(f"Processing email ID: {x}")
                result, data = mail.uid('fetch', x, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                date_received = msg.get('Date')
                date_received_datetime = datetime.strptime(date_received, "%a, %d %b %Y %H:%M:%S %z")

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')

                body = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        charset = part.get_content_charset()
                        body = part.get_payload(decode=True).decode(charset or 'utf-8', 'ignore')

                self.logger.debug(f"Found spam email: Subject: {subject}, Body: {body}")

                sender = msg.get("From", "")
                recipient = msg.get("To", "")

                # Adicione a verificação para incluir apenas e-mails do usuário logado
                if self.email_corp in msg['To']:
                    emails.append({"sender": sender, "recipient": recipient, "subject": subject, "body": body, "date": date_received_datetime})

            return sorted(emails, key=lambda x: x['date'], reverse=True)

        except Exception as e:
            self.logger.error("Error in reading spam emails: %s" % str(e), exc_info=True)
            return []


    def read_sent_emails(self):
        try:
            mail = imaplib.IMAP4_SSL(self.smtp_server)
            self.logger.debug(f"Trying to login with email: {self.email_address}")
            mail.login(self.email_address, self.password)
            self.logger.debug(f"Login successful for email: {self.email_address}")

            # Selecione a caixa de saída (Sent)
            mail.select("Sent", readonly=True)

            result, data = mail.uid('search', None, 'ALL')
            if result == 'OK':
                self.logger.info('Processing sent emails...')
            else:
                self.logger.error("Reading error", exc_info=True)
                sys.exit(0)

            ids = data[0].split()
            if len(ids) == 0:
                self.logger.info("No sent emails found.")

            emails = []

            self.logger.debug("Processing email IDs...")
            for x in ids:
                self.logger.debug(f"Processing email ID: {x}")
                result, data = mail.uid('fetch', x, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                date_received = msg.get('Date')
                date_received_datetime = datetime.strptime(date_received, "%a, %d %b %Y %H:%M:%S %z")

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')

                body = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        charset = part.get_content_charset()
                        body = part.get_payload(decode=True).decode(charset or 'utf-8', 'ignore')

                self.logger.debug(f"Found email: Subject: {subject}, Body: {body}")

                sender = msg.get("From", "")
                recipient = msg.get("To", "")

                # Adicione a verificação para incluir apenas e-mails do usuário logado
                if self.email_corp in msg['To']:
                    emails.append({"sender": sender, "recipient": recipient, "subject": subject, "body": body, "date": date_received_datetime})

            return sorted(emails, key=lambda x: x['date'], reverse=True)

        except Exception as e:
            self.logger.error("Error in reading sent emails: %s" % str(e), exc_info=True)
            return []

    
    def read_emails(self):
        try:
            mail = imaplib.IMAP4_SSL(self.smtp_server)
            self.logger.debug(f"Trying to login with email: {self.email_address}")
            mail.login(self.email_address, self.password)
            self.logger.debug(f"Login successful for email: {self.email_address}")

            mail.select(self.label, readonly=True)

            result, data = mail.uid('search', None, 'ALL')
            if result == 'OK':
                self.logger.info('Processing mailbox...')
            else:
                self.logger.error("Reading error", exc_info=True)
                sys.exit(0)

            ids = data[0].split()
            if len(ids) == 0:
                self.logger.info("No email found in selected dates.")

            emails = []

            self.logger.debug("Processing email IDs...")
            for x in ids:
                self.logger.debug(f"Processing email ID: {x}")
                result, data = mail.uid('fetch', x, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                # self.logger.debug(f"From: {msg['From']}")
                # self.logger.debug(f"To: {msg['To']}")
                # self.logger.debug(f"Subject: {msg['Subject']}")
                # self.logger.debug(f"Content-Type: {msg.get_content_type()}")

                date_received = msg.get('Date')
                # self.logger.debug(f"Date Received: {date_received}")

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')

                body = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        charset = part.get_content_charset()
                        body = part.get_payload(decode=True).decode(charset or 'utf-8', 'ignore')

                self.logger.debug(f"Found email: Subject: {subject}, Body: {body}")

                sender = msg.get("From", "")
                recipient = msg.get("To", "")

                # Adicione a verificação para incluir apenas e-mails do usuário logado
                if self.email_corp in msg['To']:
                    emails.append({"sender": sender, "recipient": recipient, "subject": subject, "body": body, "date": date_received})

            return sorted(emails, key=lambda x: x['date'], reverse=True)



        except Exception as e:
            self.logger.error("Error in reading your %s label: %s" % (self.label, str(e)), exc_info=True)
            return []

    def __init__(self, email, password, label, from_date, to_date, email_corp):
        self.logger = logging.getLogger('sLogger')
        self.subject = []
        self.smtp_server = "imap.gmail.com"
        self.email_address = email
        self.password = password
        self.label = label
        self.from_date = from_date
        self.to_date = to_date
        self.email_corp = email_corp
        


# def enviar_email(destinatario, assunto, mensagem):
#     msg = Message(assunto, sender='geral@arotec.ao', recipients=[destinatario])
#     msg.body = mensagem
#     mail.send(msg)



@app.route('/')
def index():
    # r1 = EmailRead()
    # data = r1.read_emails()
    return render_template('login.html', )

@app.route('/pagina/<parametro>')
def pagina(parametro):
    if parametro == "pack1":
        pacote = "PACOTE INDIVIDUAL"
    elif parametro == "pack2":
        pacote = "PACOTE BUSINESS"
    elif parametro == "pack3":
        pacote = "PACOTE STARTUP"
    return render_template('cadastro.html', parametro=pacote)


@app.route('/user/inbox')
@login_required
def inbox():
        # Obtém a data atual
    data_atual = datetime.now()
    # Formata a data no formato '10-Apr-2023'
    # data_formatada = data_atual.strftime('%d-%b-%Y')
    data_formatada = '1-Jan-2023'

    r1 = EmailRead(
        email= current_user.email_pr,
        password= current_user.senha_app,
        label='Inbox',
        from_date=data_formatada,
        to_date='1-May-2024',
        email_corp=current_user.email
    )
    data = r1.read_emails()
    return render_template('inbox.html', emails=data)

# @login_manager.user_loader
# def load_user(user_id):
#     return User(user_id, '', '', '', '', '', '', '', '', '', '')  # Ajuste conforme necessário

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
            'api_key': user.api_key,
            'senhap_app': user.senha_app,
            'email_pr': user.email_pr
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
            if user.senha_hash == senha:
                login_user(user)
                flash('Login bem-sucedido!', 'success')
                print(current_user)
                return redirect(url_for('perfil'))
            
            else:
                flash('Senha incorreta. Por favor, tente novamente.', 'danger')
        else:
            flash('Usuário não encontrado. Por favor, tente novamente.', 'danger')
    return render_template('login.html')

@app.route('/user/sent')
@login_required
def sent():
        #  Obtém a data atual
    data_atual = datetime.now()
    # Formata a data no formato '10-Apr-2023'
    # data_formatada = data_atual.strftime('%d-%b-%Y')
    data_formatada = '1-jan-2023'

    r1 = EmailRead(
        email=current_user.email_pr,
        password=current_user.senha_app,
        label='Inbox',
        from_date=data_formatada,
        to_date='1-May-2024',
        email_corp=current_user.email
    )

    data = r1.read_sent_emails()

    return render_template('sent_emails.html', user=current_user, emails = data)


@app.route('/user/spam')
@login_required
def spam():
        #  Obtém a data atual
    data_atual = datetime.now()
    # Formata a data no formato '10-Apr-2023'
    # data_formatada = data_atual.strftime('%d-%b-%Y')
    data_formatada = '1-jan-2023'

    r1 = EmailRead(
        email=current_user.email_pr,
        password=current_user.senha_app,
        label='Inbox',
        from_date=data_formatada,
        to_date='1-May-2024',
        email_corp=current_user.email
    )

    data = r1.read_spam_emails()

    return render_template('spam_emails.html', user=current_user, emails = data)


@app.route('/user/dashboard')
@login_required
def perfil():
        #  Obtém a data atual
    data_atual = datetime.now()
    # Formata a data no formato '10-Apr-2023'
    # data_formatada = data_atual.strftime('%d-%b-%Y')
    data_formatada = '1-jan-2023'

    r1 = EmailRead(
        email=current_user.email_pr,
        password=current_user.senha_app,
        label='Inbox',
        from_date=data_formatada,
        to_date='1-May-2024',
        email_corp=current_user.email
    )

    data = r1.read_emails()

    return render_template('dashboard.html', user=current_user, emails = data)


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
        senha_hash = senha
        user_id = len(load_users()) + 1  # Gere um ID único
        user = User(user_id, nome, email, senha_hash, empresa, telefone, 'ativo', plano, 'pendente', "2023", senha_hash, "niwe tbir noqh owxz", "contact.diversishop@gmail.com")
        users = load_users()
        
        users[str(user_id)] = OrderedDict({
            'nome': user.nome,
            'email': user.email,
            'senha_hash': user.senha_hash,
            'empresa': user.empresa,
            'telefone': user.telefone,
            'estado_conta': user.estado_conta,
            'plano': user.plano,
            'estado_pagamento': user.estado_pagamento,
            'data_criacao_conta': user.data_criacao_conta,
            'api_key': user.api_key,
            'senha_app': 'niwe tbir noqh owxz',
            'email_pr': user.email_pr
        })

        save_users(users)

        flash('Conta criada com sucesso! Faça login para acessar.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')



@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.get_json()

    print(data)
    # Lógica para enviar o e-mail com os dados recebidos
    assunto = data.get('assunto')
    destinatario = data.get('destinatario')
    mensagem = data.get('mensagem')

    # Envia o e-mail usando o Flask-Mail
    try:
        msg = Message(assunto, sender = current_user.email, recipients = [destinatario])
        msg.body = mensagem
        mail.send(msg)
        return jsonify({'resposta': "Email enviado com Sucesso!"})

    except Exception as e:
        resposta_do_servidor = f'Erro ao enviar o e-mail: {str(e)}'
        print(current_user.email)
        print(destinatario)
        print(assunto)
        return jsonify({'resposta': resposta_do_servidor + current_user.email})
    


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
