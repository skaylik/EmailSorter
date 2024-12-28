import imaplib
import email
import os
from email.header import decode_header
import config
import csv
from datetime import datetime, timedelta


# Подключение к серверу

def connection():
    mail_pass = config.mail_pass
    username = config.user_name
    imap_server = config.imap_server

    imap = imaplib.IMAP4_SSL(imap_server)
    sts, res = imap.login(username, mail_pass)
    if sts == "OK":
        print("Успешно подключено к почтовому серверу.")
        return imap
    else:
        return False

def get_attachments(msg):
    attachments = list()
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            filename = part.get_filename() #имя файла вложения
            if filename:
                attachments.append(part)
            #else:
                #print("Не найдено имя для вложения.")
        #else:
            #print("Не вложение")
    return attachments

def decode_filename(filename):
    decoded_parts = decode_header(filename)
    decoded_filename = ''
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            part = part.decode(encoding if encoding else 'utf-8')
        decoded_filename += part
    return decoded_filename

def save_attachment(part, subject):
    filename = part.get_filename()
    if filename:
        filename = decode_filename(filename)
        
        # создаем папку для темы письма
        subject_folder = subject.split('_')[1]  # часть темы для имени папки
        directory_path = os.path.join(config.local_directory, subject_folder) # формируем путь к папке
        os.makedirs(directory_path, exist_ok=True)  # создаем папку, если она не существует
        
        filepath = os.path.join(directory_path, filename)
        with open(filepath, 'wb') as f:
            f.write(part.get_payload(decode=True))
        print(f"Вложение сохранено: {filepath}")
    #else:
        #print("Не найдено имя для вложения.")

def load_deadlines(filename):
    deadlines = {}
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            lab_name, deadline = row
            deadlines[lab_name] = datetime.strptime(deadline, '%d.%m.%Y')
    return deadlines

def fetch_emails(imap, deadlines):
    valid_email_ids = []

    imap.select("inbox")
    # получаем идентификаторы всех писем с темой PY_lab
    status, messages = imap.search(None, 'SUBJECT "PY_lab"')
    if status == 'OK':
        email_ids = messages[0].split()

        for lab_name, deadline in deadlines.items():

            date_from = (deadline - timedelta(days=15))
            for email_id in email_ids:
                # получаем письмо по ID
                status, msg_data = imap.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                subject = decode_filename(msg['Subject'])

                # проверяем, соответствует ли тема письма дедлайну
                if lab_name in subject:
                    received_date = email.utils.parsedate_to_datetime(msg['Date']).replace(tzinfo=None)
                    # проверяем, если дата письма попадает в диапазон 15 дней до дедлайна
                    if received_date >= date_from and received_date <= deadline:
                        print(subject)
                        valid_email_ids.append(email_id)
    
    return valid_email_ids

def process_emails(imap, email_ids, chat_id, bot):
    if email_ids == []:
        bot.send_message(chat_id, "Писем нет")
        
    for email_id in email_ids:
        # получаем письмо по ID
        status, msg_data = imap.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])

        name_send = msg['From']
        subject = decode_filename(msg['Subject'])

        # получаем вложения
        attachments = get_attachments(msg)
        #print(f"Вложения для письма {email_id}: ", [decode_filename(part.get_filename()) for part in attachments])
        
        bot.send_message(chat_id, f"Было сохранено вложение из письма от {decode_filename(name_send)}: " + 
                         ', '.join([decode_filename(part.get_filename()) for part in attachments]))

        for attachment in attachments:
            save_attachment(attachment, subject)

def delete_emails(imap, email_ids):
    for email_id in email_ids:
        # помечаем письмо как удаленное
        imap.store(email_id, '+FLAGS', '\\Deleted')
    # удаление всех помеченных писем
    #imap.expunge()  #полное удаление закомментирую