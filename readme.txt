Создаём виртуальное окружение (venv):
    python -m venv venv

Активируем виртуальное окружение:
    Windiws:
    venv\Scripts\activate

    Linux/Mac:
    source venv/bin/activate

Установите библиотеки из requirements.txt:
    pip install -r requirements.txt

Деактивация venv:
    deactivate

Проверка установленных библиотек:
    pip list

Экспортируйте список библиотек в requirements.txt
    pip freeze > requirements.txt


Эфекты к фото:
Цветовой баланс (для яркой) (blue-red: -40, purple-green: +20, yellow-blue: -30)
Черно-белое
Цветовой тон/Насыщенность (color tone: +80,saturation: -80, brightness:0)
Цветовой баланс (для менее светлой) (blue-red: -30, purple-green: +40, yellow-blue: -20)
Яркость/Контрастность (Brightness: -20, Contrast Ratio: 10)
Уровни (RGB; 0, 0.50, 255; 0, 255)

Рабочая заметка, нужно учитывать альфа каналы, на jpg его нет и будет ошибка