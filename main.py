import sys
from PyQt6.QtWidgets import QApplication
from database import Database
from model import Account
from controller import Controller

def main():
    Database.initialize()
    Account.create_first_admin()
    app=QApplication(sys.argv)
    app.setStyle("Fusion")
    window=Controller(); window.start()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
