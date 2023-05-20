# """
# Создайте класс "Студент", который содержит атрибуты "имя", "возраст" и "список оценок",
# и методы "средняя оценка", который возвращает среднюю оценку студента, и
# "добавить оценку", который добавляет оценку в список оценок студента.
# """
#
#
# class Student:
#     def __init__(self, name: str, age: int):
#         self.name = name
#         self.age = age
#         self.grades = list()
#
#     def average_grade(self):
#         if not self.grades:
#             print('Ошибка! Оценок нет, добавьте оценки и повторите операцию')
#         else:
#             print(sum(self.grades) / len(self.grades))
#
#     def add_grade(self, grade: int):
#         self.grades.append(grade)
#
#
# artem = Student('Artem', 21)
#
# artem.add_grade(5)
# artem.add_grade(4)
# artem.add_grade(3)
# artem.add_grade(3)
#
# artem.average_grade()
#
# """
# Создайте класс "Банк", который содержит атрибуты "название", "список клиентов"
# и методы "добавить клиента", который добавляет клиента в список клиентов банка,
# "удалить клиента", который удаляет клиента из списка клиентов банка,
# "найти клиента по имени", который находит клиента по его имени, и
# "средний баланс", который возвращает средний баланс всех клиентов банка.
#
# Каждый клиент представлен классом "Клиент", который содержит атрибуты "имя",
# "номер счета" и "баланс".
# """
#
#
# # @dataclass
# class Client:
#     # name: str
#     # account_number: str
#     # balance: int
#     def __init__(self, name: str, account_number: str, balance: int):
#         self.name = name
#         self.account_number = account_number
#         self.balance = balance
#
#
# class Bank:
#     def __init__(self, name: str):
#         self.name = name
#         self.clients = list()
#
#     def add_client(self, client):
#         self.clients.append(client)
#
#     def remove_client(self, client):
#         if client in self.clients:
#             self.clients.remove(client)
#
#     def find_client_by_name(self, name):
#         for client in self.clients:
#             if client.name == name:
#                 print(client.name, client.balance)
#                 return
#         print(f'Клиент {name} не найден')
#
#     def average_balance(self):
#         if not self.clients:
#             print('Ошибка! Клиентов нет')
#             return
#         total_balance = sum(
#             [client.balance for client in self.clients]
#         )
#         print(total_balance / len(self.clients))
#
#
# my_bank = Bank('my_bank')
#
# client_1 = Client('Вася', '123456', 5000)
# client_2 = Client('Петя', '1234567', 10000)
# client_3 = Client('Володя', '1234568', 15000)
#
# my_bank.add_client(client_1)
# my_bank.add_client(client_2)
# my_bank.add_client(client_3)
#
# my_bank.find_client_by_name('Вася')
#
# my_bank.average_balance()
import time


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args)
        end_time = time.time()
        print(f'Время выполнения функции: {end_time - start_time:.10f} сек')
        return result

    return wrapper


@timer
def search(lst_, low_, high_, x_):
    count = 0
    for i in range(low_, high_):
        count += 1
        if lst_[i] == x_:
            return i, count
    else:
        return -1


@timer
def binary_search(lst_, low_, high_, x_):
    count = 0
    while low_ <= high_:
        count += 1
        mid = (low_ + high_) // 2
        if lst_[mid] == x_:
            return mid, count
        elif lst_[mid] > x_:
            high_ = mid - 1
        else:
            low_ = mid + 1
    else:
        return -1


lst = [i for i in range(1, 100000 + 1)]
x = 100000  # загаданное число

result = binary_search(lst, 0, len(lst) - 1, x)
if result != -1:
    print(f'Число {x} найдено в списке по индексу {result[0]}. Кол-во попыток: {result[1]}')
else:
    print('Число не найдено')
