import config
import telebot
import re
import smtplib
from email.mime.text import MIMEText

regex = re.compile(r'([A-Za-z0-9]+[._-])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
bot = telebot.TeleBot(config.token)

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
    try:
        email = config.email
        password = config.password

        server = smtplib.SMTP('smtp.yandex.ru', 587)
        server.ehlo()  # Кстати, зачем это?
        server.starttls()
        server.login(email, password)

        dest_email = loadmail.strip()
        subject = 'massage from telegram'
        email_text =  message_text
        message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (email, dest_email, subject, email_text)

        message = MIMEText(message)

        #print(message)

        #server.set_debuglevel(1)  # Необязательно; так будут отображаться данные с сервера в консоли
        server.sendmail(email, dest_email, message.as_string())
        server.quit()
        return loadmail
    except:
        return False

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