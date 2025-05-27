import config
import telebot
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header    import Header

regex = re.compile(r'([A-Za-z0-9]+[._-])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
bot = telebot.TeleBot(config.token)


def QuoHead(String):
    s = quopri.encodestring(String.encode('UTF-8'), 1, 0)
    return "=?utf-8?Q?" + s.decode('UTF-8') + "?="

def isValid(email):
    if re.fullmatch(regex, email):
        return True
    else:
        return False

def save_mail(name_user, mail):
    with open('file.txt', 'a') as file:
        file.write(name_user + '|' + mail +"\n")

def load_mail(name_user):
    with open('file.txt') as f:
        lines = f.readlines()
        for line in lines:
            # check if string present on a current line
            if line.find(name_user) != -1:
                mail_l = line.split("|")
                return mail_l[1]
    return False

def send_message(loadmail, message_text):
    #https://github.com/Carcarcarson/sendmail-python/blob/master/send.py
    try:
        msg = MIMEMultipart('alternative')
        # from, to, subject
        msg["From"] = config.email
        msg["To"] = loadmail.strip()
        msg['Subject'] = message_text[0:10]
        # html
        html = """\
            <html>
                <head><meta charset="UTF-8"></head>
                <body>
                    <p>"""+ message_text +"""</p>
                </body>
            </html>
            """
        content = MIMEText(html, 'html', 'UTF-8')
        msg.attach(content)

        server = smtplib.SMTP('smtp.yandex.ru', 587)
        server.ehlo()  # Кстати, зачем это?
        server.starttls()
        server.login(config.email, config.password)
        # send mail
        server.sendmail(config.email, loadmail.strip(), msg.as_string())
        # quit
        server.quit()
        return loadmail
    except:
        return False
    # attach
    # dirname = os.path.dirname(__file__)
    # filename = "send.py"
    # full_filename = os.path.join(dirname, filename)
    #
    # attach = MIMEText(open(full_filename, "rb").read(), "base64", "UTF-8")
    # attach['Content-Type'] = 'application/octet-stream'
    # attach['Content-Disposition'] = 'attachment; filename=%s' % filename
    # msg.attach(attach)
    # try:
    #     email = config.email
    #     password = config.password
    #
    #     server = smtplib.SMTP('smtp.yandex.ru', 587)
    #     server.ehlo()  # Кстати, зачем это?
    #     server.starttls()
    #     server.login(email, password)
    #     dest_email = loadmail.strip()
    #     subject = 'massage from telegram'
    #     email_text = MIMEText(message_text)
    #     message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (email, dest_email, subject, email_text.as_string())
    #
    #     print(message)
    #
    #     server.set_debuglevel(1)  # Необязательно; так будут отображаться данные с сервера в консоли
    #     server.sendmail(email, dest_email, message)
    #     server.quit()
    #     return loadmail
    # except:
    #     return False

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет! Я бот, который умеет пересылать сообщения на почту, сначала необходимо зарегестрировать почту. Введите команду /new_mail.')

@bot.message_handler(commands=["new_mail"])
def start_handler(message):
    bot.send_message(message.chat.id, 'Укажите почту')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    #bot.reply_to(message, message.text)
    if message.from_user.username == None:
        name_user = str(message.from_user.id)
    else:
        name_user = message.from_user.username

    if isValid(message.text):
        save_mail(name_user, message.text)
        bot.send_message(message.from_user.id, 'Почта добавлена')
    else:
        loadmail = load_mail(name_user)
        if loadmail == False:
            bot.send_message(message.from_user.id, "Почта НЕ найдена, введите /new_mail")
        else:
            message_sends = send_message(loadmail, message.text)
            if message_sends == False:
                bot.send_message(message.from_user.id, "Произошла ошибка при отправке сообщения " + loadmail + " " + message.text)
            else:
                bot.send_message(message.from_user.id, "Сообщение отправлено на почту " + message_sends)

bot.polling()