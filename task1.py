# =========================
#1.1 Вывести все имена полей объекта, кроме служебных
# =========================
class User:
    def __init__(self):
        self.name = 'Alex'
        self.age = 20
        self.city = 'Moscow'


obj = User()

for field_name in obj.__dict__:
    print(field_name)

# =========================
# 1.2 Вызвать метод по имени, заданному строкой
# =========================
class User:
    def hello(self):
        print('Привет')

    def bye(self):
        print('Пока')


obj = User()

method_name = 'hello'

if hasattr(obj, method_name):
    method = getattr(obj, method_name)
    if callable(method):
        method()

# =========================
# 1.3 Что не так с этим кодом наследоваться только от Б
# =========================

'''
Проблема в том, что B уже наследуется от A, а C пытается наследоваться и от A, и от B одновременно.

То есть A попадает в иерархию дважды:
    напрямую
    через B

Python не может построить корректный MRO и выдаст ошибку.

'''
class A:
    pass


class B(A):
    pass


class C(B):
    pass
# =========================
# 1.4 Функция-однострочник get_inheritance
# =========================

'''
Тут просто в переменную get_inheritance записывается функция.
lambda - Это анонимная функция, то есть функция без def.  почти тоже самое что и def get_inheritance(cls):
cls - Это класс, который мы передаём в функцию.
cls.__mro__  = Method Resolution Order
То есть порядок, в котором Python ищет методы и базовые классы.
for base in cls.__mro__

Это генератор, который проходит по всем классам в цепочке наследования.
когда cls.__mro__ = (OSError, Exception, BaseException, object)
то цикл будет по очереди брать:
base = OSError
base = Exception
base = BaseException
base = object

base.__name__

У каждого класса есть имя.
print(OSError.__name__) выведет OSError
То есть из самих объектов классов мы достаём только их имена как строки.
base.__name__ for base in cls.__mro__)

Это генератор выражения. он последовательно строки выдает
' -> '.join(...) - Метод join склеивает строки через разделитель.
Вот эквивалент без lambda и без однострочности:
def get_inheritance(cls):
    names = []

    for base in cls.__mro__:
        names.append(base.__name__)

    return ' -> '.join(names)

'''
get_inheritance = lambda cls: ' -> '.join(base.__name__ for base in cls.__mro__)

# =========================
# 1.5 Реализовать хэш-таблицу, аналог dict
# =========================

'''
Нужно реализовать упрощённый аналог dict.
Обычный словарь Python хранит данные в виде:
    ключ
    значение


Здесь:
'name' это ключ
'Alex' это значение

Для этого ключ сначала преобразуют в число с помощью функции hash().
Зачем нужен hash(key)

Ключ может быть:
    строкой
    числом
    кортежем

Но нам нужно получить номер корзины, куда этот ключ попадёт.
'''
class MyDict:
    def __init__(self, bucket_count=16):
        self.bucket_count = bucket_count
        self.buckets = [[] for _ in range(bucket_count)]
        self.size = 0

    def _get_bucket_index(self, key):
        return hash(key) % self.bucket_count # даст некоторое целое число.

    def __setitem__(self, key, value):
        bucket_index = self._get_bucket_index(key)
        bucket = self.buckets[bucket_index]

        for i in range(len(bucket)):
            stored_key, _ = bucket[i]
            if stored_key == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self.size += 1

    def __getitem__(self, key):
        bucket_index = self._get_bucket_index(key)
        bucket = self.buckets[bucket_index]

        for stored_key, stored_value in bucket:
            if stored_key == key:
                return stored_value

        raise KeyError(key)

    def __len__(self):
        return self.size
