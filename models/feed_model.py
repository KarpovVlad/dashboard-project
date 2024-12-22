import sqlite3
from datetime import datetime

DATABASE = 'data_changes.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS offers (
        id TEXT PRIMARY KEY,
        name TEXT,
        price TEXT,
        vendor TEXT,
        quantity_in_stock TEXT,
        picture TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        offer_id TEXT,
        field TEXT,
        old_value TEXT,
        new_value TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (offer_id) REFERENCES offers (id)
    )''')
    conn.commit()
    conn.close()


def save_offer(offer):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO offers (id, name, price, vendor, quantity_in_stock, picture, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (offer['id'], offer['name'], offer['price'], offer['vendor'], offer['quantity_in_stock'], offer['picture'], offer['timestamp']))
    conn.commit()
    conn.close()

def save_change(change):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT INTO changes (offer_id, field, old_value, new_value, timestamp)
                 VALUES (?, ?, ?, ?, ?)''',
              (change['offer_id'], change['field'], change['old_value'], change['new_value'], datetime.now()))
    conn.commit()
    conn.close()

def get_all_changes():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT offer_id, field, old_value, new_value, timestamp FROM changes ORDER BY timestamp DESC')
    changes = c.fetchall()
    conn.close()
    return changes

def get_filtered_changes(field, start_date, end_date, search):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    query = '''
        SELECT changes.offer_id, offers.name, changes.field, changes.old_value, changes.new_value, changes.timestamp
        FROM changes
        JOIN offers ON changes.offer_id = offers.id
        WHERE 1=1
    '''
    params = []

    if field:
        query += ' AND changes.field = ?'
        params.append(field)
    if start_date:
        query += ' AND changes.timestamp >= ?'
        params.append(start_date + " 00:00:00")
    if end_date:
        query += ' AND changes.timestamp <= ?'
        params.append(end_date + " 23:59:59")
    if search:
        query += ' AND offers.name LIKE ?'
        params.append(f'%{search}%')

    query += ' ORDER BY changes.timestamp DESC'
    c.execute(query, params)
    changes = [
        {
            "offer_id": row[0],
            "name": row[1],
            "field": row[2],
            "old_value": row[3],
            "new_value": row[4],
            "timestamp": row[5],
        }
        for row in c.fetchall()
    ]
    conn.close()
    return changes


def get_all_offers(search=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    query = 'SELECT * FROM offers'
    params = []

    if search:
        query += ' WHERE name LIKE ?'
        params.append(f'%{search}%')

    print("SQL-запит:", query)
    print("Параметри:", params)

    c.execute(query, params)
    offers = c.fetchall()
    conn.close()

    print("Результат запиту:", offers)
    return offers


def get_offer_by_id(offer_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, name, price, vendor, quantity_in_stock, picture, timestamp FROM offers WHERE id = ?', (offer_id,))
    result = c.fetchone()
    conn.close()

    if result:
        return {
            "id": result[0],
            "name": result[1],
            "price": result[2],
            "vendor": result[3],
            "quantity_in_stock": result[4],
            "picture": result[5],
            "timestamp": result[6],
        }
    return None

