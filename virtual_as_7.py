import pickle
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер повинен складатися з 10 чисел")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            self.value = value 
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
    def __str__(self):
        return self.value
        
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone_obj = self.find_phone(phone_number)
        if phone_obj:
            self.phones.remove(phone_obj)

    def edit_phone(self, old_phone, new_phone):
        if not self.find_phone(old_phone):
            raise ValueError(f"Номер {old_phone} не знайдено.")
        
        self.add_phone(new_phone)
        self.remove_phone(old_phone)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = f"; {'; '.join(p.value for p in self.phones)}" if self.phones else ""
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Ім'я: {self.name.value}, телефон: {phones}{birthday}"
    

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday is None:
                continue
            
            birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            
            birthday_this_year = birthday_date.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            
            days_until_birthday = (birthday_this_year - today).days

            if 0 <= days_until_birthday <= 7:
                congratulation_date = birthday_this_year

                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                upcoming_birthdays.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays
    
    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
    

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


# Декоратори і функції-хендлери

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Контакт не знайдено"
        except IndexError:
            return "Введіть ім'я користувача"
        except AttributeError:
            return "Контакт не знайдено" 
        except Exception as e:
            return f"Помилка: {e}"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Контакт змінено"
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано"
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Номер телефону змінено"
    
@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    return f"Номер телефону {name}: {'; '.join(p.value for p in record.phones)}"
    
@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Адресна книга пуста"
    return str(book)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    record.add_birthday(birthday)
    return "Дату народження додано"
    
@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record.birthday:
        return f"День народження {name}: {record.birthday}"
    else:
        return "День народження не встановлено"
    
@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "Немає найближчого дня народження"
    
    result = "Наближчі дні народження:\n"
    for item in upcoming:
        result += f"{item['name']}: {item['birthday']}\n"
    return result.strip()

def main():
    book = load_data()    
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        if not user_input:
            continue
            
        command, args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()