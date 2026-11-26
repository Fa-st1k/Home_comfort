
from PyQt6.QtWidgets import QMessageBox,QInputDialog
from model import Account,Employee,Applicant,MenuItem,Basket,Order
from view import MainView,LoginDialog,ClientView,AdminView,ApplicantView

class Controller:
    def __init__(self):
        self.main=MainView(self); self.login_dialog=None; self.client=None; self.admin=None; self.applicant=None
        self.account=None; self.basket=Basket()
    def start(self): self.main.show()
    def open_login(self): self.login_dialog=LoginDialog(self,parent=self.main); self.login_dialog.show()
    def open_admin_login(self): self.login_dialog=LoginDialog(self,admin=True,parent=self.main); self.login_dialog.show()
    def login(self):
        d=self.login_dialog; account=Account.login(d.login.text(),d.password.text())
        if not account: QMessageBox.warning(d,"Вход","Неверный логин или пароль"); return
        if d.admin and account["role"]!="admin": QMessageBox.warning(d,"Доступ","Этот аккаунт не администратор"); return
        if not d.admin and account["role"]!="client": QMessageBox.warning(d,"Доступ","Войдите через режим администратора"); return
        self.account=account; d.accept()
        if account["role"] == "admin": self.open_admin()
        else: self.open_client()
    def register(self):
        d=self.login_dialog; ok,msg=Account.register(d.login.text(),d.password.text()); (QMessageBox.information if ok else QMessageBox.warning)(d,"Регистрация",msg)
    def open_client(self):
        self.basket.clear(); self.client=ClientView(self,MenuItem.all()); self.client.show(); self.client.refresh(self.basket)
    def add_item(self,item): self.basket.add(item); self.client.refresh(self.basket)
    def remove_item(self):
        key=self.client.selected_id()
        if key is not None: self.basket.remove(key); self.client.refresh(self.basket)
    def pay(self):
        if not self.basket.items: QMessageBox.information(self.client,"Оплата","Корзина пуста"); return
        method,ok=QInputDialog.getItem(self.client,"Оплата",f"К оплате: {self.basket.total()} руб.", ["Карта","Наличные"],0,False)
        if not ok:return
        if method=="Наличные":
            cash,ok=QInputDialog.getInt(self.client,"Наличные","Внесённая сумма:",self.basket.total(),self.basket.total(),1000000)
            if not ok:return
            change=cash-self.basket.total()
        else: change=0
        order_id=Order.create(self.account["id"],self.basket,method); total=self.basket.total(); self.basket.clear(); self.client.refresh(self.basket)
        QMessageBox.information(self.client,"Заказ",f"Заказ №{order_id} оформлен!\nСумма: {total} руб.\nСдача: {change} руб.\nСпасибо за покупку!")
    def open_admin(self): self.admin=AdminView(self); self.admin.show(); self.refresh_admin()
    def refresh_admin(self): self.admin.refresh_employees(Employee.all()); self.admin.refresh_applicants(Applicant.all())
    def add_employee(self):
        d=self.admin.form_data()
        if not all(d[k] for k in ["Имя","Фамилия","Возраст","Должность","ID"]): QMessageBox.warning(self.admin,"Данные","Заполните имя, фамилию, возраст, должность и ID."); return
        ok,msg=Employee.add(d); (QMessageBox.information if ok else QMessageBox.warning)(self.admin,"Сотрудники",msg)
        if ok:self.admin.clear_form(); self.refresh_admin()
    def edit_employee(self):
        d=self.admin.form_data(); code=d["ID"]
        if not code or not all(d[k] for k in ["Имя","Фамилия","Возраст","Должность"]): QMessageBox.warning(self.admin,"Данные","Укажите ID и заполните обязательные поля."); return
        if Employee.update(code,d): QMessageBox.information(self.admin,"Сотрудники","Данные обновлены."); self.refresh_admin()
        else: QMessageBox.warning(self.admin,"Сотрудники","Не найден сотрудник или данные некорректны.")
    def remove_employee(self):
        code=self.admin.form_data()["ID"]
        if not code:return
        if Employee.remove(code):self.refresh_admin(); QMessageBox.information(self.admin,"Сотрудники","Сотрудник удалён.")
        else:QMessageBox.warning(self.admin,"Сотрудники","ID не найден.")
    def fire_all(self):
        if QMessageBox.question(self.admin,"Подтверждение","Удалить всех сотрудников?")==QMessageBox.StandardButton.Yes: Employee.remove_all(); self.refresh_admin()
    def hire_applicant(self):
        code=self.admin.selected_applicant()
        if not code:return
        ok,msg=Applicant.hire(code); (QMessageBox.information if ok else QMessageBox.warning)(self.admin,"Найм",msg); self.refresh_admin()
    def open_applicant(self): self.applicant=ApplicantView(self); self.applicant.show()
    def submit_application(self):
        d=self.applicant.data()
        if not all(d.values()): QMessageBox.warning(self.applicant,"Заявка","Заполните все поля."); return
        try: code=Applicant.submit(d)
        except ValueError: QMessageBox.warning(self.applicant,"Заявка","Возраст должен быть числом."); return
        QMessageBox.information(self.applicant,"Заявка",f"Заявка отправлена!\nВаш код: {code}\nСохраните его для администратора."); self.applicant.clear()
