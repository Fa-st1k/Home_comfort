
import hashlib, secrets, string
from database import Database


def password_hash(password: str) -> str:
    # PBKDF2 with per-password salt; suitable for this educational local app.
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180_000).hex()
    return f"{salt}${digest}"


def password_matches(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180_000).hex()
        return secrets.compare_digest(check, digest)
    except ValueError:
        return False


class Account:
    @staticmethod
    def register(login, password):
        login = login.strip()
        if len(login) < 3 or len(password) < 6:
            return False, "Логин — от 3 символов, пароль — от 6."
        try:
            with Database.connect() as db:
                db.execute("INSERT INTO accounts(login,password_hash) VALUES(?,?)", (login, password_hash(password)))
            return True, "Регистрация прошла успешно."
        except Exception as e:
            if "UNIQUE" in str(e).upper(): return False, "Такой логин уже занят."
            return False, "Не удалось создать аккаунт."

    @staticmethod
    def login(login, password):
        with Database.connect() as db:
            row = db.execute("SELECT * FROM accounts WHERE login=? COLLATE NOCASE", (login.strip(),)).fetchone()
        if row and password_matches(password, row["password_hash"]):
            return dict(row)
        return None

    @staticmethod
    def create_first_admin():
        with Database.connect() as db:
            if not db.execute("SELECT 1 FROM accounts WHERE role='admin'").fetchone():
                db.execute("INSERT INTO accounts(login,password_hash,role) VALUES(?,?, 'admin')",
                           ("admin", password_hash("admin12345")))


class Employee:
    @staticmethod
    def all():
        with Database.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM employees ORDER BY last_name,first_name")]

    @staticmethod
    def add(data):
        try:
            with Database.connect() as db:
                db.execute("INSERT INTO employees(first_name,last_name,patronymic,age,position,experience,employee_code) VALUES(?,?,?,?,?,?,?)",
                    (data["Имя"].strip(),data["Фамилия"].strip(),data.get("Отчество","").strip(),int(data["Возраст"]),data["Должность"].strip(),data.get("Опыт","").strip(),data["ID"].strip()))
            return True, "Сотрудник добавлен."
        except Exception as e:
            return False, "Проверьте данные: ID должен быть уникальным, возраст — от 14 до 100."

    @staticmethod
    def update(code, data):
        try:
            with Database.connect() as db:
                cur = db.execute("UPDATE employees SET first_name=?,last_name=?,patronymic=?,age=?,position=?,experience=? WHERE employee_code=?",
                    (data["Имя"].strip(),data["Фамилия"].strip(),data.get("Отчество","").strip(),int(data["Возраст"]),data["Должность"].strip(),data.get("Опыт","").strip(),code.strip()))
                return cur.rowcount > 0
        except Exception: return False

    @staticmethod
    def remove(code):
        with Database.connect() as db:
            cur = db.execute("DELETE FROM employees WHERE employee_code=?", (code.strip(),))
            return cur.rowcount > 0

    @staticmethod
    def remove_all():
        with Database.connect() as db: db.execute("DELETE FROM employees")


class Applicant:
    @staticmethod
    def all():
        with Database.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM applicants ORDER BY created_at DESC")]

    @staticmethod
    def submit(data):
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        with Database.connect() as db:
            db.execute("INSERT INTO applicants(code,first_name,last_name,patronymic,age,position,experience,employee_code) VALUES(?,?,?,?,?,?,?,?)",
                (code,data["Имя"].strip(),data["Фамилия"].strip(),data.get("Отчество","").strip(),int(data["Возраст"]),data["Должность"].strip(),data.get("Опыт","").strip(),data["ID"].strip()))
        return code

    @staticmethod
    def hire(code):
        with Database.connect() as db:
            row = db.execute("SELECT * FROM applicants WHERE code=?", (code.strip().upper(),)).fetchone()
            if not row: return False, "Заявка не найдена."
            try:
                db.execute("INSERT INTO employees(first_name,last_name,patronymic,age,position,experience,employee_code) VALUES(?,?,?,?,?,?,?)",
                    (row["first_name"],row["last_name"],row["patronymic"],row["age"],row["position"],row["experience"],row["employee_code"]))
                db.execute("DELETE FROM applicants WHERE id=?", (row["id"],))
                return True, "Соискатель принят на работу."
            except Exception: return False, "ID сотрудника уже используется или данные некорректны."


class MenuItem:
    @staticmethod
    def all():
        with Database.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM menu WHERE available=1 ORDER BY name")]


class Basket:
    def __init__(self): self.items = {} # menu id -> dict
    def add(self, item):
        key = item["id"]
        if key in self.items: self.items[key]["quantity"] += 1
        else: self.items[key] = {"name":item["name"],"price":item["price"],"quantity":1}
    def remove(self, key): self.items.pop(key, None)
    def total(self): return sum(x["price"]*x["quantity"] for x in self.items.values())
    def clear(self): self.items.clear()


class Order:
    @staticmethod
    def create(account_id, basket, method):
        with Database.connect() as db:
            cur = db.execute("INSERT INTO orders(account_id,total,payment_method) VALUES(?,?,?)", (account_id,basket.total(),method))
            order_id = cur.lastrowid
            db.executemany("INSERT INTO order_items(order_id,product_name,price,quantity) VALUES(?,?,?,?)",
                [(order_id,x["name"],x["price"],x["quantity"]) for x in basket.items.values()])
            return order_id
