# Берем нужный базовый образ
FROM python:3.10-alpine
# Копируем все файлы из текущей директории в /app контейнера
COPY ./ /app
# Устанавливаем все зависимости
RUN apk update && apk add gcc && apk add libc-dev && pip install -r /app/requirements.txt --no-cache-dir
# Устанавливаем приложение (Подробнее смотри Distutils)
RUN pip3 install -e /app
# Говорим контейнеру какой порт слушай
EXPOSE 8088
# Запуск нашего приложения при старте контейнера
CMD web_server

# В качестве альтернативы distutils можно просто указать что выполнить
#CMD python /app/src/app.py