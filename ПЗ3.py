import mysql.connector

db_config = {
        ############
    }

class SQLTable:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                print('Подключение к базе данных установлено')
        except:
            print('Ошибка подключения')
            raise


    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print('Соединение отключено')


    def execute_query(self, query, param=None):
        cursor = None
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, param)
            self.connection.commit()
            count = cursor.rowcount
            print(f'Запрос выполнен успешно. Затронуто строк: {count}')
            return count
        except:
            print(f'Ошибка при выполнении запроса')
            self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()


    def select(self, query, param=None):
        cursor = None
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, param)
            result = cursor.fetchall()
            print(f'SELECT выполнен. Получено строк: {len(result)}')
            return result
        except:
            print(f'Ошибка SELECT')
            return []
        finally:
            if cursor:
                cursor.close()


    def insert(self, table_name, data):
        colum = []
        values = []
        for key, val in data.items():
            colum.append(key)
            values.append(val)
        columns_str = ', '.join(colum)
        shablon = ', '.join(['%s'] * len(colum))
        query = f'INSERT INTO {table_name} ({columns_str}) VALUES ({shablon})'
        cursor = None
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()
            new_id = cursor.lastrowid
            print(f'Добавлена запись в таблицу {table_name}. ID: {new_id}')
            return new_id
        except:
            print(f'Ошибка INSERT')
            self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()


    def update(self, table, data, where_new_value, where_param=None):
        set_parts = []
        for key in data.keys():
            set_parts.append(f"{key} = %s")
        set_old_value = ', '.join(set_parts)
        set_values = list(data.values())
        if where_param:
            all_params = set_values + list(where_param)
        else:
            all_params = set_values
        query = f'UPDATE {table} SET {set_old_value} WHERE {where_new_value}'
        return self.execute_query(query, all_params)


    def delete(self, table, where_value, where_param=None):
        query = f'DELETE FROM {table} WHERE {where_value}'
        return self.execute_query(query, where_param)


    def create_table(self, table_name, colum_names):
        query = f'CREATE TABLE IF NOT EXISTS {table_name} ({colum_names})'
        result = self.execute_query(query)
        if result is not None:
            print(f'Таблица {table_name} создана (или уже существует)')
        else:
            print(f'Не удалось создать таблицу {table_name}')


    def drop_table(self, table_name):
        query = f'DROP TABLE IF EXISTS {table_name}'
        result = self.execute_query(query)
        if result is not None:
            print(f'Таблица {table_name} удалена (или не существовала)')
        else:
            print(f'Не удалось удалить таблицу {table_name}')


'''Проверка работы'''
db = SQLTable(db_config)

# Создаю таблицу people
columns = '''
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT'''
db.create_table('people', columns)
print()

# Добавляю людей
person1 = {'name': 'Катя', 'age': 18}
person2 = {'name': 'Иван', 'age': 57}
person3 = {'name': 'Маша', 'age': 32}

id1 = db.insert('people', person1)
id2 = db.insert('people', person2)
id3 = db.insert('people', person3)
print()

# Вывожу людей старше 30 лет
result = db.select('SELECT * FROM people WHERE age > %s', (30,))
print('Люди старше 30 лет:')
for row in result:
    print(f'ID: {row['id']}, Имя: {row['name']}, Возраст: {row['age']}')
print()

# Меняю возраст человека
db.update('people', {'age': 30}, 'id = %s', (id2,))
print()

# Удаляю человека
db.delete('people', 'id = %s', (id3,))
print()

# Удаляю таблицу people
db.drop_table('people')
print()

db.disconnect()
