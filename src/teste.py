from email.utils import formataddr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_email(usuario, senha, remetente, destinatario, assunto, mensagem):
    # Configuração do servidor SMTP do Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Criação da mensagem
    msg = MIMEMultipart()
    msg['From'] = remetente  # Configura o remetente desejado
    msg['To'] = destinatario
    msg['Subject'] = assunto

    # Adiciona o corpo da mensagem
    msg.attach(MIMEText(mensagem, 'plain'))

    # Conexão e envio usando SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(usuario, senha)
        server.sendmail(remetente, destinatario, msg.as_string())

# Exemplo de uso
usuario_smtp = 'contact.diversishop@gmail.com'
senha_smtp = 'elactgylqqfekeok'
remetente_desejado = formataddr(('AROTEC SU', 'geral@arotec.ao'))
destinatario = 'ja3328173@gmail.com'
assunto = 'Assunto do E-mail'
mensagem = 'Corpo do E-mail'

enviar_email(usuario_smtp, senha_smtp, remetente_desejado, destinatario, assunto, mensagem)
