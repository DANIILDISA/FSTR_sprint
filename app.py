from flask import Flask, request, jsonify
import psycopg2
# from decouple import Config

app = Flask(__name__)

# значения переменных из окружения
# config = Config()
# config.read('conf.env')
# DATABASE_NAME = config.get('FSTR_DB_NAME')
# DATABASE_USER = config.get('FSTR_DB_USER')
# DATABASE_PASSWORD = config.get('FSTR_DB_PASS')
# DATABASE_HOST = config.get('FSTR_DB_HOST')
# DATABASE_PORT = config.get('FSTR_DB_PORT')

# Второй вариант для упрощения тестов
DATABASE_NAME = 'DB_FTSR'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = ''
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '5432'


# Метод для создания записи
@app.route('/submitData', methods=['POST'])
# Это декоратор Flask, который указывает, что
# следующая функция должна выполняться при отправке запроса POST к конечной точке /submitData.
# В целом @app.route: это декоратор,
# который используется для связывания функции Python с определенным URL-адресом или конечной точкой.
def submit_data():
    """
    Submit data to the API
    ---
    parameters:
      - name: data
        in: body
        required: true
        schema:
          type: object
          properties:
            beauty_title:
              type: string
            title:
              type: string
            other_titles:
              type: string
            connect:
              type: string
            add_time:
              type: string
            user:
              type: object
              properties:
                email:
                  type: string
                fam:
                  type: string
                name:
                  type: string
                otc:
                  type: string
                phone:
                  type: string
            coords:
              type: object
              properties:
                latitude:
                  type: string
                longitude:
                  type: string
                height:
                  type: string
            level:
              type: object
              properties:
                winter:
                  type: string
                summer:
                  type: string
                autumn:
                  type: string
                spring:
                  type: string
            images:
              type: array
              items:
                type: object
                properties:
                  title:
                    type: string
    responses:
      200:
        description: Successfully submitted data
      500:
        description: Internal Server Error
    """
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


# Метод для получения записи по ID
@app.route('/submitData/<int:id>', methods=['GET'])
def get_record_by_id(id):  # параметр id будет передан из url
    """
    Get record by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the record
    responses:
      200:
        description: Successfully retrieved record
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 200
            data:
              type: object
              example: {"ID": 1, "beautyTitle": "Beautiful Title", "title": "Title", "other_titles": "Other Titles",
              "connect": "Connection Info", "add_time": "2023-11-21", "user_id": 1, "coord_id": 1,
              "winter": "Winter Info", "summer": "Summer Info", "autumn": "Autumn Info", "spring": "Spring Info"}

      404:
        description: Record not found
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 404
            message:
              type: string
              example: "Запись не найдена"
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 500
            message:
              type: string
              example: "Internal Server Error"
    """
    try:
        conn = psycopg2.connect(  # Соединение с бд
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST
        )
        cursor = conn.cursor()  # подключение к бд

        cursor.execute('''
            SELECT * FROM Pereval WHERE ID = %s;
        ''', (id,))  # выполнение sql запроса, выбираем все столбцы из таблицы 'Pereval',
        # где значение id такое, какое мы передали из url

        record = cursor.fetchone()  # извлекаем результат (одна запись из таблицы 'Pereval')

        conn.close()  # закрываем соединение с бд

        if record:
            return jsonify({"status": 200, "data": record})
        else:
            return jsonify({"status": 404, "message": "Запись не найдена"})

    except Exception as e:
        return jsonify({"status": 500, "message": str(e)})


# Метод для редактирования записи по ID
@app.route('/submitData/<int:id>', methods=['PATCH'])
def edit_record_by_id(id):
    """
    Edit record by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the record to edit
      - name: data
        in: body
        required: true
        schema:
          type: object
          properties:
            beauty_title:
              type: string
            title:
              type: string
            other_titles:
              type: string
            connect:
              type: string
            add_time:
              type: string
            level:
              type: object
              properties:
                winter:
                  type: string
                summer:
                  type: string
                autumn:
                  type: string
                spring:
                  type: string
    responses:
      200:
        description: Successfully edited record
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 200
            state:
              type: integer
              example: 1
            message:
              type: string
              example: "Запись успешно отредактирована"
      403:
        description: Forbidden
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 403
            message:
              type: string
              example: "Редактировать можно только записи new"
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 500
            state:
              type: integer
              example: 0
            message:
              type: string
              example: "Internal Server Error"
    """

    try:
        data = request.get_json()

        conn = psycopg2.connect(
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST
        )
        cursor = conn.cursor()  # подключение к бд и создание курсора

        # Проверка статуса записи
        cursor.execute('''
            SELECT status FROM Pereval WHERE ID = %s;
        ''', (id,))  # Делаем sql запрос на статус записи по id

        status = cursor.fetchone()  # получаем статус записи

        if status and status[0] != 'new':  # если статус записи не 'new', то:
            conn.close()  # закрываем соединение
            return jsonify({"status": 403, "message": "Редактировать можно только записи new"})

        # Обновление данных
        cursor.execute('''
            UPDATE Pereval SET
            beautyTitle = %s, title = %s, other_titles = %s, connect = %s, add_time = %s,
            winter = %s, summer = %s, autumn = %s, spring = %s
            WHERE ID = %s;
        ''', (
            data.get('beauty_title'), data.get('title'), data.get('other_titles'), data.get('connect'),
            data.get('add_time'),
            data.get('level', {}).get('winter'), data.get('level', {}).get('summer'),
            data.get('level', {}).get('autumn'), data.get('level', {}).get('spring'), id
        ))  # sql запрос на обновление полей в таблице 'Pereval' по id,
        # значения берутся из JSON запроса. Вторая часть - картеж параметров для sql

        conn.commit()  # выполнение
        conn.close()

        return jsonify({"status": 200, "state": 1, "message": "Запись успешно отредактирована"})

    except Exception as e:
        return jsonify({"status": 500, "state": 0, "message": str(e)})


# Метод для получения списка записей пользователя по email
@app.route('/submitData/', methods=['GET'])
def get_records_by_user_email():
    """
    Get records by user email
    ---
    parameters:
      - name: user__email
        in: query
        type: string
        required: true
        description: Email of the user to retrieve records
    responses:
      200:
        description: Successfully retrieved records
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 200
            data:
              type: array
              items:
                type: object
                example: {"ID": 1, "beautyTitle": "Beautiful Title", "title": "Title", "other_titles": "Other Titles",
                "connect": "Connection Info", "add_time": "2023-11-21", "user_id": 1, "coord_id": 1,
                "winter": "Winter Info", "summer": "Summer Info", "autumn": "Autumn Info", "spring": "Spring Info"}

      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 500
            message:
              type: string
              example: "Internal Server Error"
    """
    try:
        # Получаем значение user__email из запроса
        user_email = request.args.get('user__email')

        conn = psycopg2.connect(
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST
        )
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM Pereval WHERE user_id = (SELECT ID FROM Users WHERE email = %s);
        ''', (user_email,))  # Получаем записи пользователя по email

        records = cursor.fetchall()  # извлекаем записи
        conn.close()

        return jsonify({"status": 200, "data": records})

    except Exception as e:
        return jsonify({"status": 500, "message": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
