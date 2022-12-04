from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QInputDialog, QLineEdit, QWidget, QTableWidget, QTableView, QTableWidgetItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtGui import QFont
import sys

class Table(QTableWidget):
    def __init__(self): # ИНИЦИАЛИЗАЦИЯ КЛАССА
        """Инициализация класса
        ps: вот так добавляют коментарии)
        посмотреть их можно с помощью волшебного метода __doc__ """
        super().__init__()
        self.setWindowTitle("Таблица")
        self.resize(300, 200)

        self.table = QTableWidget(self)
        self.table_formation()
        self.show()

    def table_formation(self): # СОЗДАНИЕ И ЗАПОЛНЕНИЕ ТАБЛИЦЫ
        self.table.resize(600, 400)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["name", "mark", "average"])
        query = QSqlQuery("SELECT name, mark, average FROM students")

        while query.next():
            rows = self.table.rowCount()
            self.table.setRowCount(rows + 1)
            self.table.setItem(rows, 0, QTableWidgetItem(query.value(0)))
            self.table.setItem(rows, 1, QTableWidgetItem(query.value(1)))
            self.table.setItem(rows, 2, QTableWidgetItem(str(query.value(2))))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.show()

class Window(QWidget):
    def __init__(self): # ИНИЦИАЛИЗАЦИЯ КЛАССА
            super().__init__()
            self.setWindowTitle("Оценки")
            self.resize(400, 400)
            self.add_buttons()
            self.init_ui()

    def init_ui(self): # ЗАГРУЗКА ИНТЕРФЕЙСА
        self.create_bd()
        self.show()

    def add_buttons(self): # ДОБАВЛЕНИЕ КНОПОК
        mark_button = QPushButton("Добавить оценку", self)
        mark_button.resize(mark_button.sizeHint())
        mark_button.move(10, 10)
        mark_button.clicked.connect(self.mark_button)

        student_button = QPushButton("Добавить ученика", self)
        student_button.resize(student_button.sizeHint())
        student_button.move(10, 50)
        student_button.clicked.connect(self.data_button)
        
        tableData_button = QPushButton("Открыть таблицу", self)
        tableData_button.resize(tableData_button.sizeHint())
        tableData_button.move(200, 10)
        tableData_button.clicked.connect(self.db_view)

        cleardb_button = QPushButton("Очистить базу данных", self)
        cleardb_button.resize(cleardb_button.sizeHint())
        cleardb_button.move(200, 50)
        cleardb_button.clicked.connect(self.clear_button)
        
        deleteStudent_button = QPushButton("Удалить ученика", self)
        deleteStudent_button.resize(deleteStudent_button.sizeHint())
        deleteStudent_button.move(10, 90)
        deleteStudent_button.clicked.connect(self.delete_student)

    def create_bd(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("students.sqlite")
        if not self.db.open():
            print("не получилось открыть бд")
        self.query = QSqlQuery()
        self.query.exec("""CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL,
            mark TEXT,
            average FLOAT
            )""")

# ДОБАВЛЕНИЕ УЧЕНИКА

    def get_text(self):
        text, ok = QInputDialog.getText(self, "добавление ученика", "Введите имя ученика:", QLineEdit.Normal, "")
        if text != "" and ok:
            return text

# ДОБАВЛЕНИЕ ОЦЕНКИ

    def get_name(self):
        self.query.prepare("SELECT name FROM students")
        if not self.query.exec():
            print("не получилось загрузить бд", self.query.lastError())
        names = []
        name_index = self.query.record().indexOf("name")
        while self.query.next():
            name = self.query.value(name_index)
            names.append(name)
        return names

    def get_choice(self, names):
        name, ok = QInputDialog.getItem(self, "ученики", "Выберите ученика:", names, 0, False)
        if ok:
            return name

    def get_mark(self):
        mark, ok = QInputDialog.getInt(self, "добавить оценку", "Выберите оценку:", 5, 2, 5, 1)
        if ok:
            return mark
    
    def get_grade(self, name, mark):
        self.query.prepare("SELECT mark FROM students WHERE name = (?)")
        self.query.addBindValue(name)
        self.query.exec()
        while self.query.next():
            marks = self.query.value(self.query.record().indexOf("mark"))
            if marks == "":
                marks += f'{mark}'
            else:
                marks += f'{", " + str(mark)}'
        return marks

    def update_mark(self, name, mark):
        self.query.prepare("UPDATE students SET mark = (?) WHERE name = (?)")
        self.query.addBindValue(mark)
        self.query.addBindValue(name)
        self.query.exec()

# СРЕДНЯЯ ОЦЕНКА

    def set_average(self, name):
        self.query.prepare("SELECT mark FROM students WHERE name = (?)")
        self.query.addBindValue(name)
        self.query.exec()
        while self.query.next():
            marks = self.query.value(self.query.record().indexOf("mark"))
            marks = (marks.split(", "))
            sum = 0
            for mark in marks:
                sum+=int(mark)
            average = round(sum/len(marks), 1)

        self.query.prepare("UPDATE students SET average = (?) WHERE name = (?)")
        self.query.addBindValue(average)
        self.query.addBindValue(name)
        self.query.exec()

# КНОПКИ

    def data_button(self):
        name = self.get_text()
        if name:
            self.query.prepare("INSERT INTO students (name) VALUES (?)")
            self.query.addBindValue(name)
            self.query.exec()

            self.table.close()
            self.table = Table()

    def mark_button(self):
        names = self.get_name()
        name = self.get_choice(names)
        if name:
            mark = self.get_mark()
            add_mark = self.get_grade(name, mark)
            self.update_mark(name, add_mark)
            self.set_average(name)

            self.table.close()
            self.table = Table()
    
    def clear_button(self):
        self.query.prepare("DELETE FROM students")
        self.query.exec()

        self.table.close()
        self.table = Table()

    def db_view(self):
        self.table = Table()

    def delete_student(self):
        names = self.get_name()
        name = self.get_choice(names)
        if name:
            self.query.prepare("DELETE FROM students WHERE name = (?)")
            self.query.addBindValue(name)
            self.query.exec()

            self.table.close()
            self.table = Table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = Window()
    sys.exit(app.exec_())