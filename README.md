

# Тестовое задание procontext

## Текст задания
1. Вытащить из апи Центробанка (пример http://www.cbr.ru/scripts/XML_daily_eng.asp?date_req=11/11/2020) данные по переводу различных валют в рубли за последние 90 дней.

2. Результатом работы программы:

- нужно указать значение максимального курса валюты, название этой валюты и дату этого максимального значения.

- нужно указать значение минимального курса валюты, название этой валюты и дату этого минимального значения.

- нужно указать среднее значение курса рубля за весь период по всем валютам.

К файлу с программой, нужно прикрепить инструкцию по запуску.

## Доп. инфо.

Третий пункт трактовал как средний курс рубля по каждой валюте из api.

## Запуск локально
- Создать виртуальное окружение:
```
python3 -m venv venv 
```
- Активировать
```
source venv/bin/activate
```
- Установить
```
python3 install -r requirements.txt
```
- Запуск
```
python3 main.py
``` 

## Запуск из готового docker образа
```bash
docker run --rm kratorr/procontext 
```
