собрать докер:         docker build -t cars-api .
запуск докер:          docker run -p 8000:8000 cars-api
проверка на сайте:     http://127.0.0.1:8000/docs

запуск через компоус:  docker compose up --build
остоновка:             docker compose down


запуск с uvicorn:      uv run uvicorn main_beta:app --reload


main_beta.py - Fastapi приложение
cars.db база

POST/cars - добавить тачку
GET/cars - получить все тачки
GET/cars{id} - по id
PUT - обновить
DELETE - удалить
GET /cars/{id}/trip-cost?distance=100&fuel_price=1.5 - Расчёт поездки


Юзается:
- Python 3.13
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- Docker
- uv


Что делает:
- Добавление автомобиля
- Получение списка автомобилей
- Получение автомобиля по ID
- Обновление пробега и статуса
- Удаление автомобиля

Дополнительно:
- Расчёт стоимости поездки по расходу топлива

формула:     fuel_needed = (car.fuel_consumption / 100) * distance
             total_cost = fuel_needed * fuel_price   

             #fuel_consumption - сколько жрет бенз на 100км
             #дальше просто дистанция и цена бенза(указать там же)