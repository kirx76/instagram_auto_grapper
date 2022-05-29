# Берем нужный базовый образ
FROM python:3.10-alpine
# Копируем все файлы из текущей директории в /app контейнера
COPY ./ /app
# Устанавливаем все зависимости
RUN apk update && apk add gcc && apk add libc-dev && apk add libffi-dev && pip install -r /app/requirements.txt --no-cache-dir
# Устанавливаем приложение (Подробнее смотри Distutils)
RUN pip3 install -e /app
# Говорим контейнеру какой порт слушай
#EXPOSE 8088
# Запуск нашего приложения при старте контейнера
WORKDIR /app/src
CMD python3 main.py

# В качестве альтернативы distutils можно просто указать что выполнить
#CMD python /app/src/app.py