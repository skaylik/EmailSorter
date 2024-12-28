# EmailSorter
Бот получает письма по IMAP. Копирует вложение в папку с названием lab01 в соответствии с темой письма PY_lab01_Ivanov_09-415.zip. Проверяет даты дедлайна, указанные в файле labs_deadlines.csv. Письмо на сервере удаляется. В итоге на локальном хосте – все вложения копируются в заданный каталог: ../Python_2024/Labs.

# config
Пример, что находится в config:

mail_pass = "пароль от почты для внешних приложений"
username = "ivanov.petrov@mail.ru"
imap_server = "imap.mail.ru"
local_directory = './Python_2024/Labs'
file_deadlines = './labs_deadlines.csv'

TOKEN = 'токен'

# Установка
Клонируем репозиторий. Получаем пароль для mail.ru, создаём ТГ-бота, в проекте создаем файл config.py и вносим в него все необходимые данные.
Устанавливаем pyTelegramBotAPI==4.25.0
