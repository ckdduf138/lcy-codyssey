import csv
import mysql.connector


class MySQLHelper:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def insert_weather_data(self, mars_date, temp, storm):
        query = (
            'INSERT INTO mars_weather (mars_date, temp, storm) '
            'VALUES (%s, %s, %s)'
        )
        self.cursor.execute(query, (mars_date, temp, storm))

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()


def read_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)  # 컬럼명 기준으로 읽기
        for row in reader:
            mars_date = row['mars_date']
            temp = float(row['temp'])     
            storm = int(row['stom']) 
            data.append((mars_date, temp, storm))
    return data



def main():
    db = MySQLHelper(
        host='localhost',
        user='root',
        password='011013',
        database='mars_db'  
    )

    data = read_csv('mars_weathers_data.csv')

    for row in data:
        db.insert_weather_data(row[0], row[1], row[2])

    db.commit()
    db.close()


if __name__ == '__main__':
    main()
