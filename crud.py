import psycopg2

with psycopg2.connect(database='clients', user='postgres', password='postgres') as conn:

    def drop_db(conn):

        with conn.cursor() as cur:

            cur.execute("""
                DROP TABLE IF EXISTS phones;
                DROP TABLE IF EXISTS users;
            """)
            conn.commit()

    def create_db(conn):

        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    user_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40) NOT NULL,
                    last_name VARCHAR(60) NOT NULL,
                    email VARCHAR(80) UNIQUE NOT NULL
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phones(
                    phone_id SERIAL PRIMARY KEY,
                    phone VARCHAR(12) UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL REFERENCES users(user_id)
                );
            """)

            conn.commit()

    def add_user(conn, first_name, last_name, email, phones=None):

        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO users(first_name, last_name, email)
                VALUES(%s, %s, %s) RETURNING user_id;
                """, (first_name, last_name, email))
            user_id = cur.fetchone()[0]
            if phones:
                for phone in phones:
                    cur.execute("""
                        INSERT INTO phones(user_id, phone)
                        VALUES(%s, %s);
                        """, (user_id, phone))
                
            conn.commit()
            return user_id

    def add_phone(conn, user_id, phone):

        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO phones(user_id, phone)
                VALUES(%s, %s);
                """, (user_id, phone))

            conn.commit()

    def change_user(conn, user_id, first_name=None, last_name=None, email=None, phones=None):

        with conn.cursor() as cur:
            
            if first_name:
                cur.execute("""
                    UPDATE users
                    SET first_name = %s
                    WHERE user_id = %s;
                    """, (first_name, user_id))
            if last_name:
                cur.execute("""
                    UPDATE users
                    SET last_name = %s
                    WHERE user_id = %s;
                    """, (last_name, user_id))
            if email:
                cur.execute("""
                    UPDATE users
                    SET email = %s
                    WHERE user_id = %s;
                    """, (email, user_id))
            if phones is not None:
                cur.execute("""
                    DELETE FROM phones
                    WHERE user_id = %s;
                    """, (user_id,))
                for phone in phones:
                    cur.execute("""
                        INSERT INTO phones(user_id, phone)
                        VALUES(%s, %s);
                        """, (user_id, phone))

            conn.commit()

    def delete_phone(conn, user_id, phone):

        with conn.cursor() as cur:

            cur.execute("""
                DELETE FROM phones
                WHERE user_id = %s AND phone = %s;
                """, (user_id, phone))

            conn.commit()

    def delete_user(conn, user_id):

        with conn.cursor() as cur:

            cur.execute("""
                DELETE FROM phones
                WHERE user_id = %s;
                """, (user_id,))
            
            cur.execute("""
                DELETE FROM users
                WHERE user_id = %s;
                """, (user_id,))

            conn.commit()

    def find_user(conn, first_name=None, last_name=None, email=None, phone=None):

        with conn.cursor() as cur:

            query = """
                SELECT u.user_id, u.first_name, u.last_name, u.email, p.phone
                FROM users AS u
                LEFT JOIN phones AS p ON u.user_id = p.user_id
                WHERE(%s IS NULL OR u.first_name = %s)
                    AND(%s IS NULL OR u.last_name = %s)
                    AND(%s IS NULL OR u.email = %s)
                    AND(%s IS NULL OR p.phone = %s);
            """
            cur.execute(query, (first_name, first_name, last_name, last_name, email, email, phone, phone))
            result = cur.fetchall()
            return result

    if __name__ == "__main__":

        with psycopg2.connect(database='clients', user='postgres', password='postgres') as conn:

            drop_db(conn)

            create_db(conn)

            user_id = add_user(conn, 'Ivan', 'Ivanov', 'ivanov@mail.ru', ['9003330000', '987654321'])
            print(f'Added client with ID: {user_id}')

            add_phone(conn, user_id, '123456789')
            print(f'Added phone to client ID: {user_id}')

            change_user(conn, user_id, first_name='Ivan', phones = ['111111111', '555555555'])
            print(f'Changed client ID: {user_id}')

            delete_phone(conn, user_id, '555555555')
            print(f'Deleted phone from client ID: {user_id}')

            found_clients = find_user(conn, first_name='Ivan')
            print(f'Found clients: {found_clients}')

            delete_user(conn, user_id)
            print(f'Deleted client ID: {user_id}')
