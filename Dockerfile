# Берем нужный базовый образ
FROM python:3.10.4-slim-bullseye
# Копируем все файлы из текущей директории в /app контейнера
COPY ./ /app
# Устанавливаем все зависимости
RUN apt-get update && apt-get install -y gcc && apt-get install -y libc-dev && apt-get install -y libffi-dev && pip3 install -r /app/requirements.txt --no-cache-dir
# Устанавливаем приложение (Подробнее смотри Distutils)
RUN pip3 install -e /app
# Говорим контейнеру какой порт слушай
#EXPOSE 8088
# Запуск нашего приложения при старте контейнера
WORKDIR /app/src
CMD python3 main.py

# В качестве альтернативы distutils можно просто указать что выполнить
#CMD python /app/src/app.py