from PyQt5.QtWidgets import QApplication, QLabel, QWidget,QPushButton, QInputDialog, QLineEdit, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys

# Костыль
import sqlite3


class Table(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Табличка")
        self.resize(700, 500)
        self.setFont(QFont("Comic Sans MS", 10, QFont.Bold))
        self.db = sqlite3.connect("students.db")
        self.cursor = self.db.cursor()
        self.table = QTableWidget(self)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_formation()
        self.table.move(50, 50)
        self.show()

    def table_formation(self):
        self.table.resize(600, 400)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Имя ученика", "Оценки"])
        data = list(self.cursor.execute("SELECT * FROM students"))
        self.table.setRowCount(len(data))
        for i in range(len(data)):
            for j in range(3):
                print(data[i][j], type(data[i][j]))
                self.table.setItem(i, j, QTableWidgetItem(str(data[i][j])))
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.show()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Оценочки")
        self.resize(400, 400)
        self.setFont(QFont("Comic Sans MS", 10, QFont.Bold))
        self.center_str = QLabel("<h2><a href='https://vk.com/search?c%5Bq%5D=%23ВернитеМойSystem32&c%5Bsection%5D=statuses'>#ВернитеМойSystem32</a></h2>")
        self.center_str.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.center_str.setOpenExternalLinks(True)
        self.add_buttons()
        self.init_ui()

    def init_ui(self):
        self.create_bd()
        self.show()

    def add_buttons(self):
        mark_button = QPushButton("Добавить оценку", self)
        mark_button.resize(mark_button.sizeHint())
        mark_button.move(10, 10)
        mark_button.clicked.connect(self.mark_button)

        student_button = QPushButton("Добавить ученика", self)
        student_button.resize(student_button.sizeHint())
        student_button.move(10, 50)
        student_button.clicked.connect(self.data_button)

        mark_button = QPushButton("Посмотреть таблицу", self)
        mark_button.resize(mark_button.sizeHint())
        mark_button.move(10, 90)
        mark_button.clicked.connect(self.db_view)

    def create_bd(self):
        self.db = sqlite3.connect("students.db")
        self.cursor = self.db.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL,
            mark TEXT
            )""")
        self.db.commit()
    
    def get_text(self):
        text, ok = QInputDialog.getText(self, "Добавление ученика", "Введите имя ученика:", QLineEdit.Normal, "")
        if text != "" and ok and text not in self.get_name():
            return text
        else:
            return False

    def data_button(self):
        name = self.get_text()
        if name:
            self.cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
            self.db.commit()

    def mark_button(self):
        names = self.get_name()
        if names:
            name = self.get_choice(names)
            if name:
                mark = self.get_mark(name)
                if mark:
                    add_mark = self.get_grade(name, mark)
                    self.update_mark(name, add_mark)
                else:
                    self.mark_button()

    def update_mark(self, name, mark):
        self.cursor.execute("UPDATE students SET mark = (?) WHERE name = (?)", (', '.join(mark), name))
        self.db.commit()       

    def get_grade(self, name, mark):
        marks = list(self.cursor.execute("SELECT mark FROM students WHERE name = (?)", (name,)))
        return [elem[0] for elem in marks] * (marks != [(None,)]) + [mark]

    def get_name(self):
        names_unformatted = self.cursor.execute("SELECT name FROM students")
        return [elem[0] for elem in names_unformatted]

    def get_choice(self, names):
        name, ok = QInputDialog.getItem(self, "Ученики", "Выберите ученика:", names, 0, False)
        if ok:
            return name
        else:
            return False

    def get_mark(self, name):
        Yaroslav = 5 if name == 'Ярослав' else 2
        mark, ok = QInputDialog.getInt(self, "Добавить оценку", "Выберите оценку:", 5, Yaroslav, 5, 1)
        if ok:
            return str(mark)
        else:
            return False
    
    def db_view(self):
        self.table = Table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = Window()
    sys.exit(app.exec_())