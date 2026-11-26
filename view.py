import os
from PyQt6.QtWidgets import (QMainWindow,QWidget,QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QLineEdit,QPushButton,QMessageBox,QTabWidget,QTableWidget,QTableWidgetItem,QListWidget,QInputDialog,QScrollArea,QGridLayout,QGroupBox)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

FIELDS = ["Имя","Фамилия","Отчество","Возраст","Должность","Опыт","ID"]

class MainView(QMainWindow):
    def __init__(self, controller):
        super().__init__(); self.controller=controller
        self.setWindowTitle("Home Comfort — кафе «Домашний уют»"); self.resize(480,360)
        w=QWidget(); l=QVBoxLayout(w); l.addStretch()
        title=QLabel("☕ Домашний уют\nКафе и сервис домашнего комфорта"); title.setAlignment(Qt.AlignmentFlag.AlignCenter); title.setStyleSheet("font-size:22px;font-weight:bold;color:#70452b;")
        l.addWidget(title); l.addSpacing(20)
        for text,fn in [("Войти / регистрация",controller.open_login),("Режим администратора",controller.open_admin_login),("Подать заявку на работу",controller.open_applicant)]:
            b=QPushButton(text); b.setMinimumHeight(42); b.clicked.connect(fn); l.addWidget(b)
        l.addStretch(); self.setCentralWidget(w)

class LoginDialog(QDialog):
    def __init__(self, controller, admin=False, parent=None):
        super().__init__(parent); self.controller=controller; self.admin=admin
        self.setWindowTitle("Вход администратора" if admin else "Вход в аккаунт"); self.setFixedWidth(320)
        l=QVBoxLayout(self); form=QFormLayout(); self.login=QLineEdit(); self.password=QLineEdit(); self.password.setEchoMode(QLineEdit.EchoMode.Password)
        if not admin: form.addRow("Логин",self.login)
        else: self.login.setText("admin")
        form.addRow("Пароль",self.password); l.addLayout(form)
        b=QPushButton("Войти"); b.clicked.connect(controller.login); l.addWidget(b)
        if not admin:
            r=QPushButton("Создать аккаунт"); r.clicked.connect(controller.register); l.addWidget(r)

class ClientView(QWidget):
    def __init__(self, controller, menu):
        super().__init__(); self.controller=controller; self.setWindowTitle("Home Comfort — меню"); self.resize(850,600)
        root=QHBoxLayout(self); scroll=QScrollArea(); scroll.setWidgetResizable(True); content=QWidget(); grid=QGridLayout(content)
        for i,item in enumerate(menu):
            card=QGroupBox(item["name"])
            card.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; border: 1px solid #d8c3ad; border-radius: 10px; margin-top: 10px; padding: 8px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
            cl=QVBoxLayout(card)
            pic=QLabel(); pic.setAlignment(Qt.AlignmentFlag.AlignCenter); pic.setFixedSize(190,130)
            pic.setStyleSheet("background: #f4eee8; border-radius: 8px;")
            path=os.path.join(os.path.dirname(__file__),item.get("image", ""))
            if os.path.isfile(path):
                pixmap=QPixmap(path)
                pic.setPixmap(pixmap.scaled(190,130,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:
                pic.setText("Фото пока не добавлено")
            cl.addWidget(pic, alignment=Qt.AlignmentFlag.AlignCenter)
            price=QLabel(f"Цена: {item['price']} руб.")
            price.setStyleSheet("font-size: 14px; color: #70452b; font-weight: bold;")
            cl.addWidget(price)
            b=QPushButton("Добавить в корзину")
            b.clicked.connect(lambda _,x=item:controller.add_item(x))
            cl.addWidget(b)
            grid.addWidget(card,i//2,i%2)
        scroll.setWidget(content); root.addWidget(scroll,3)
        side=QVBoxLayout(); side.addWidget(QLabel("Корзина")); self.basket=QListWidget(); side.addWidget(self.basket); self.total=QLabel("Итого: 0 руб."); side.addWidget(self.total)
        for label,fn in [("Удалить выбранное",controller.remove_item),("Оплатить",controller.pay)]:
            b=QPushButton(label); b.clicked.connect(fn); side.addWidget(b)
        side.addStretch(); root.addLayout(side,2)
    def refresh(self,basket):
        self.basket.clear()
        for key,x in basket.items.items(): self.basket.addItem(f"{key}|{x['name']} x{x['quantity']} = {x['price']*x['quantity']} руб.")
        self.total.setText(f"Итого: {basket.total()} руб.")
    def selected_id(self):
        item=self.basket.currentItem()
        try: return int(item.text().split("|",1)[0]) if item else None
        except ValueError: return None

class ApplicantView(QWidget):
    def __init__(self, controller):
        super().__init__(); self.controller=controller; self.setWindowTitle("Заявка на работу"); self.setFixedWidth(400)
        l=QVBoxLayout(self); form=QFormLayout(); self.edits={}
        for f in FIELDS:
            e=QLineEdit(); self.edits[f]=e; form.addRow(f+":",e)
        l.addLayout(form); b=QPushButton("Отправить заявку"); b.clicked.connect(controller.submit_application); l.addWidget(b)
    def data(self): return {k:v.text().strip() for k,v in self.edits.items()}
    def clear(self):
        for e in self.edits.values(): e.clear()

class AdminView(QWidget):
    def __init__(self, controller):
        super().__init__(); self.controller=controller; self.setWindowTitle("Home Comfort — администратор"); self.resize(1000,650)
        root=QVBoxLayout(self); tabs=QTabWidget(); root.addWidget(tabs)
        ew=QWidget(); el=QVBoxLayout(ew); self.employees=QTableWidget(0,7); self.employees.setHorizontalHeaderLabels(FIELDS); self.employees.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); el.addWidget(self.employees)
        form=QHBoxLayout(); self.edits={}
        for f in FIELDS: e=QLineEdit(); e.setPlaceholderText(f); e.setMaximumWidth(125); self.edits[f]=e; form.addWidget(e)
        el.addLayout(form)
        buttons=QHBoxLayout()
        for text,fn in [("Добавить",controller.add_employee),("Изменить по ID",controller.edit_employee),("Удалить по ID",controller.remove_employee),("Уволить всех",controller.fire_all)]:
            b=QPushButton(text); b.clicked.connect(fn); buttons.addWidget(b)
        el.addLayout(buttons); tabs.addTab(ew,"Сотрудники")
        aw=QWidget(); al=QVBoxLayout(aw); self.applicants=QTableWidget(0,9); self.applicants.setHorizontalHeaderLabels(["Код","Имя","Фамилия","Отчество","Возраст","Должность","Опыт","ID","Дата"]); self.applicants.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); al.addWidget(self.applicants)
        b=QPushButton("Принять выбранного соискателя"); b.clicked.connect(controller.hire_applicant); al.addWidget(b); tabs.addTab(aw,"Заявки")
    def form_data(self): return {k:v.text().strip() for k,v in self.edits.items()}
    def clear_form(self):
        for e in self.edits.values(): e.clear()
    def refresh_employees(self, rows):
        self.employees.setRowCount(len(rows))
        keys=["first_name","last_name","patronymic","age","position","experience","employee_code"]
        for r,row in enumerate(rows):
            for c,k in enumerate(keys): self.employees.setItem(r,c,QTableWidgetItem(str(row[k])))
    def refresh_applicants(self, rows):
        self.applicants.setRowCount(len(rows)); keys=["code","first_name","last_name","patronymic","age","position","experience","employee_code","created_at"]
        for r,row in enumerate(rows):
            for c,k in enumerate(keys): self.applicants.setItem(r,c,QTableWidgetItem(str(row[k])))
    def selected_applicant(self):
        r=self.applicants.currentRow(); return self.applicants.item(r,0).text() if r>=0 and self.applicants.item(r,0) else None
