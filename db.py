"""
    CREATE SEQUENCE IF NOT EXISTS pereval_id_seq;
    CREATE SEQUENCE IF NOT EXISTS pereval_areas_id_seq;
    CREATE SEQUENCE IF NOT EXISTS pereval_images_id_seq;
    CREATE SEQUENCE IF NOT EXISTS pereval_coords_id_seq;
    CREATE TABLE IF NOT EXISTS Users (
        ID SERIAL PRIMARY KEY,
        email TEXT UNIQUE,
        fam TEXT,
        name TEXT,
        otc TEXT,
        phone TEXT
    );
    
    CREATE TABLE IF NOT EXISTS Coords (
        ID SERIAL PRIMARY KEY,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        height INT
    );
    
    CREATE TABLE IF NOT EXISTS Pereval (
        ID SERIAL PRIMARY KEY,
        beautyTitle TEXT,
        title TEXT,
        other_titles TEXT,
        connect TEXT,
        add_time TIMESTAMP,
        user_id INT REFERENCES Users(ID),
        coord_id INT REFERENCES Coords(ID),
        winter TEXT,
        summer TEXT,
        autumn TEXT,
        spring TEXT
    );
    
    CREATE TABLE IF NOT EXISTS PerevalImages (
        ID SERIAL PRIMARY KEY,
        pereval_id INT REFERENCES Pereval(ID),
        image_title TEXT
    );
"""
"""
    ALTER TABLE Pereval
    ADD COLUMN status TEXT;

    -- Значения по умолчанию для поля status: new
    UPDATE Pereval SET status = 'new' WHERE status IS NULL;
"""
"""
    -- Добавление ограничения CHECK для поля status
    ALTER TABLE Pereval
    ADD CONSTRAINT status_check CHECK (status IN ('new', 'pending', 'accepted', 'rejected')
    );
"""
"""
    INSERT INTO Users (email, fam, name, otc, phone)
    VALUES
        ('user@email.tld', 'Пупкин', 'Василий', 'Иванович', '79031234567'
        );

    INSERT INTO Coords (latitude, longitude, height)
    VALUES
        (45.3842, 7.1525, 1200);

    INSERT INTO Pereval (beautyTitle, title, other_titles, connect, add_time,
                            user_id, coord_id, winter, summer, autumn, spring)
    VALUES
        ('пер. ', 'Пхия', 'Триев', '', '2021-09-22 13:18:13', 1, 1, '', '1А', '1А', '');

    INSERT INTO PerevalImages (pereval_id, image_title)
    VALUES
        (1, 'Седловина'),
        (1, 'Подъем');
"""
