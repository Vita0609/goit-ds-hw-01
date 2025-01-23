from collections import UserDict
from datetime import datetime, date, timedelta
import pickle
from abc import ABC, abstractmethod

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone number (10 digits) please or just name if you are looking for birthday"
        except IndexError:
            return "Give me the needed name"
        except TypeError:
            return "Some information was given wrong"

    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

# Абстрактний базовий клас для користувальницьких уявлень
class UserView(ABC):
    @abstractmethod
    def show_message(self, message: str):
        pass
    
    @abstractmethod
    def show_contact(self, contact):
        pass
    
    @abstractmethod
    def show_all_contacts(self, contacts):
        pass
    
    @abstractmethod
    def show_birthday(self, birthday):
        pass

    @abstractmethod
    def show_upcoming_birthdays(self, birthdays):
        pass

# Реалізація для консолі
class ConsoleUserView(UserView):
    def show_message(self, message: str):
        print(message)
    
    def show_contact(self, contact):
        if contact is None:
            self.show_message("Contact not found.")
        else:
            self.show_message(str(contact))

    def show_all_contacts(self, contacts):
        if not contacts:
            self.show_message("No contacts available.")
        else:
            for contact in contacts:
                self.show_message(str(contact))

    def show_birthday(self, birthday):
        if birthday is None:
            self.show_message("Birthday not found.")
        else:
            self.show_message(f"Birthday: {birthday}")
    
    def show_upcoming_birthdays(self, birthdays):
        if not birthdays:
            self.show_message("No upcoming birthdays.")
        else:
            for birthday in birthdays:
                self.show_message(f"{birthday['name']}: {birthday['congratulation_date']}")

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Номер повинен містити 10 цифр")
        
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value) 
        except ValueError:
            return "Invalid date format. Use DD.MM.YYYY"
        

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, value):
        self.birthday = Birthday(value)

    def add_phone(self, number):
        self.phones.append(Phone(number))

    def remove_phone(self, remnum):
        for phone in self.phones:
            if phone.value == remnum:
                self.phones.remove(phone)
                return f"Запис з номером '{remnum}' видалено."
        return f"Запис з номером '{remnum}' не знайдено."

    def edit_phone(self, oldnum, newnum):
        Phone(newnum)
        for phone in self.phones:
            if phone.value == oldnum:
                phone.value = newnum
                return
        raise ValueError(f"Номер '{oldnum}' не знайдено.")
             

    def __str__(self):
        phone_numbers = '; '.join(p.value for p in self.phones)
        return f"{self.name}: {phone_numbers}"

class AddressBook(UserDict):
    def add_record(self, record):
        key = record.name.value
        self.data[key] = record
    
    def find(self, neededname):
        return self.data.get(neededname)

    def delete(self, rem):
        if rem in self.data:
            del self.data[rem]
        else:
            print(f"Запис з ім'ям '{rem}' не знайдено.")

    def date_to_string(self, date):
        return date.strftime("%d.%m.%Y")
    
    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday
    

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()
        for name, record in self.data.items():
            if record.birthday != None:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)
        
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year+1)
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year = self.adjust_for_weekend(birthday_this_year)
            

                if 0 <= (birthday_this_year - today).days <= days:
                    congratulation_date_str = self.date_to_string(birthday_this_year)
                    upcoming_birthdays.append( {"name": name, "congratulation_date": congratulation_date_str})

        return upcoming_birthdays

    
    def __str__(self):
        records = '\n'.join(f"{record}" for name, record in self.data.items())
        return f"Address Book:\n{records}"


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        if Phone(phone):
            record = Record(name)   
            book.add_record(record)
            message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, oldnum, newnum, *_ = args 
    record = book.find(name)
    if record is None:
        return f'The contact was not found in the book'
    for phone in record.phones:
        if phone.value == oldnum:
            record.edit_phone(oldnum, newnum)
            return f'Contact {name} was updated'
    return f"The number you are trying to change doesn't exist"
    
@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    return book.find(name)

@input_error
def show_all(book: AddressBook):
    result = []
    for name, value in book.data.items():
        if value.birthday == None:
            result.append(f'{value}')
        elif value.birthday != None:
            result.append(f'{value}; birthday: {value.birthday}')
    return result

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record == None:
        return f'The contact was not found in the book'
    record.add_birthday(birthday)
    return f'Birthday was added'

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record.birthday == None:
        return "Birtday was not found"
    return record.birthday 

@input_error
def birthdays(book: AddressBook):
    result = []
    upcoming = book.get_upcoming_birthdays() 
    for el in upcoming:
        result.append(f"{el['name']}: {el['congratulation_date']}")
    if len(result) == 0:
        return f'No birthdays are expected'
    return '\n'.join(result)


def save_data(book=AddressBook, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    view = ConsoleUserView()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break
        elif command == "hello":
            view.show_message("How can I help you?")
        elif command == "add":
            view.show_message(add_contact(args, book))
        elif command == "change":
            view.show_message(change_contact(args, book))
        elif command == "phone":
            contact = show_phone(args, book)
            view.show_contact(contact)
        elif command == "all":
            contacts = show_all(book)
            view.show_all_contacts(contacts)
        elif command == "add-birthday":
            view.show_message(add_birthday(args, book))
        elif command == "show-birthday":
            birthday = show_birthday(args, book)
            view.show_birthday(birthday)
        elif command == "birthdays":
            birthdays = birthdays(book)
            view.show_upcoming_birthdays(birthdays)
        else:
            view.show_message("Invalid command.")

if __name__ == "__main__":
    main()
