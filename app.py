from flask import Flask, request, jsonify
import psycopg2
from decouple import Config

app = Flask(__name__)

config = Config()
config.read('conf.env')

# значения переменных из окружения
DATABASE_NAME = config.get('FSTR_DB_NAME')
DATABASE_USER = config.get('FSTR_DB_USER')
DATABASE_PASSWORD = config.get('FSTR_DB_PASS')
DATABASE_HOST = config.get('FSTR_DB_HOST')
DATABASE_PORT = config.get('FSTR_DB_PORT')


@app.route('/submitData', methods=['POST'])
# Это декоратор Flask, который указывает, что
# следующая функция должна выполняться при отправке запроса POST к конечной точке /submitData.
# В целом @app.route: это декоратор,
# который используется для связывания функции Python с определенным URL-адресом или конечной точкой.
def submit_data():
    try:
        data = request.get_json()
        # Извлекает данные JSON запроса POST.
        # request — это объект, предоставляемый Flask, который содержит информацию о текущем запросе.
        # get_json() — это метод, который анализирует данные JSON из запроса, и возвращает их в виде словаря.
        conn = psycopg2.connect(  # Устанавливается соединение с бд с помощью psycopg2
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST
        )
        cursor = conn.cursor()
        # Управляющая структура, используемая для управления контекстом операции выборки.
        # Он создается на основе соединения и используется для выполнения SQL-запросов.
        # В данном случае мы создаем курсор для взаимодействия с базой данных.

        # Преобразование JSON в Python-объект для более удобного доступа к данным
        beauty_title = data.get('beauty_title')
        title = data.get('title')
        other_titles = data.get('other_titles')
        connect = data.get('connect')
        add_time = data.get('add_time')

        user = data.get('user', {})
        user_email = user.get('email', '')

        coords = data.get('coords', {})
        latitude = coords.get('latitude', '')
        longitude = coords.get('longitude', '')
        height = coords.get('height', '')

        level = data.get('level', {})
        winter = level.get('winter', '')
        summer = level.get('summer', '')
        autumn = level.get('autumn', '')
        spring = level.get('spring', '')

        images = data.get('images', [])

        # Вставка данных в таблицы.
        # Объект курсора используется для выполнения SQL.
        cursor.execute('''
            INSERT INTO Users (email, fam, name, otc, phone)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        ''', (user_email, user.get('fam', ''), user.get('name', ''), user.get('otc', ''), user.get('phone', '')))

        cursor.execute('''
            INSERT INTO Coords (latitude, longitude, height)
            VALUES (%s, %s, %s)
            RETURNING ID;
        ''', (latitude, longitude, height))  # Заполняем SQL запрос значениями.
        # RETURNING ID - эта часть запроса SQL указывает, что после вставки идентификатор вновь вставленной строки
        # должен быть возвращен как результат операции INSERT.

        coord_id = cursor.fetchone()[0]
        # Этот метод объекта курсора извлекает следующую строку из результатов выполненного запроса.
        # В данном случае извлекается строка, которая была вставлена в таблицу Coords
        # и возвращена с помощью условия RETURNING.
        # [0] используется для доступа к первому столбцу результата, который является
        # идентификатором новой вставленной записи.

        cursor.execute('''
            INSERT INTO Pereval (beautyTitle, title, other_titles, connect, add_time, user_id, coord_id, winter, summer, autumn, spring)
            VALUES (%s, %s, %s, %s, %s, (SELECT ID FROM Users WHERE email = %s), %s, %s, %s, %s, %s)
            RETURNING ID;
        ''', (
            beauty_title, title, other_titles, connect, add_time, user_email, coord_id, winter, summer, autumn, spring))
        # (SELECT ID FROM Users WHERE email = %s) - используется запрос для получения идентификатора
        # из таблицы Users на основе  user_email.
        pereval_id = cursor.fetchone()[0]  # Тоже самое, только для pereval_id.

        for image in images:  # цикл перебирает список изображений,
            # который содержит данные изображений для объекта Pereval.
            cursor.execute('''
                INSERT INTO PerevalImages (pereval_id, image_title)
                VALUES (%s, %s);
            ''', (pereval_id, image.get('title', '')))

        conn.commit()  # Фиксируем транзакцию в бд.
        conn.close()  # Закрываем соединение с бд после завершения транзакции.

        return jsonify({"status": 200, "message": "Успешно", "id": pereval_id})
        # Создаём ответ JSON с использованием функции Flask jsonify, которая преобразует словарь Python в JSON.
        # "id": pereval_id: - это позволяет ссылаться на вновь созданную запись.
    except Exception as e:
        return jsonify({"status": 500, "message": str(e), "id": None})
        # str(e) - сообщение об ошибке преобразуется в строку и включается в ответ.

if __name__ == '__main__':
    app.run(debug=True)
