from flask import Flask, request, jsonify
import psycopg2
import json

app = Flask(__name__)

DATABASE_NAME = 'postgres'
DATABASE_USER = 'DB_FTSR'
DATABASE_PASSWORD = ''
DATABASE_HOST = '127.0.0.1'


@app.route('/submitData', methods=['POST'])
def submit_data():
    try:
        data = request.get_json()

        conn = psycopg2.connect(
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST
        )
        cursor = conn.cursor()

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

        cursor.execute('''
            INSERT INTO Users (email, fam, name, otc, phone)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        ''', (user_email, user.get('fam', ''), user.get('name', ''), user.get('otc', ''), user.get('phone', '')))

        cursor.execute('''
            INSERT INTO Coords (latitude, longitude, height)
            VALUES (%s, %s, %s)
            RETURNING ID;
        ''', (latitude, longitude, height))

        coord_id = cursor.fetchone()[0]

        cursor.execute('''
            INSERT INTO Pereval (beautyTitle, title, other_titles, connect, add_time, user_id, coord_id, winter, summer, autumn, spring)
            VALUES (%s, %s, %s, %s, %s, (SELECT ID FROM Users WHERE email = %s), %s, %s, %s, %s, %s)
            RETURNING ID;
        ''', (
            beauty_title, title, other_titles, connect, add_time, user_email, coord_id, winter, summer, autumn, spring))

        pereval_id = cursor.fetchone()[0]

        for image in images:
            cursor.execute('''
                INSERT INTO PerevalImages (pereval_id, image_title)
                VALUES (%s, %s);
            ''', (pereval_id, image.get('title', '')))

        conn.commit()
        conn.close()

        return jsonify({"status": 200, "message": "Успешно", "id": pereval_id})

    except Exception as e:
        return jsonify({"status": 500, "message": str(e), "id": None})


if __name__ == '__main__':
    app.run(debug=True)
