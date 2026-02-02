Чтобы запустить:

1. Клонируй репозиторий:
   git clone https://github.com/asdemura28/student_rental_service.git
   cd student_rental_service

2. Создай виртуальное окружение:
   python -m venv venv
   venv\Scripts\activate (windows)
   ls venv/bin/activate (macos)

3. Установи зависимости:
   pip install -r requirements.txt

4. Примени миграции:
   python manage.py migrate

5. Создай админа:
   python manage.py createsuperuser

6. Запусти сервер:
   python manage.py runserver

Зайди в браузере: http://127.0.0.1:8000/