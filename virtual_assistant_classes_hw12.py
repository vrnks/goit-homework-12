from collections import UserDict
from datetime import datetime
import re
import csv

class AddressBook(UserDict): 
    def __init__(self, records_per_page=10):
        super().__init__()
        self.records_per_page = records_per_page

    def add_record(self, record):
        self.data[record.name.value] = record

    def iterator(self):
        record_names = list(self.data.keys())
        num_records = len(record_names)
        current_index = 0

        while current_index < num_records:
            batch = record_names[current_index:current_index + self.records_per_page]
            yield [self.data[name] for name in batch]
            current_index += self.records_per_page
            
    # ==========================================        
    def save_to_file(self, filename):
        # Відкриваємо файл для запису 
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            # Записуємо кожен запис у форматі CSV: ім'я, телефони, день народження
            for record in self.data.values():
                writer.writerow([record.name.value] + [phone.value for phone in record.phones] + [record.birthday.value])

    def load_from_file(self, filename):
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                name = row[0]
                phones = row[1:-1]  # Всі елементи крім першого та останнього будуть телефонами
                birthday = row[-1]
                record = Record(Name(name), phones, birthday)
                self.add_record(record)
                
    def search_contacts(self, search_query):
        matching_contacts = []
        for record in self.values():
            match_found = False 
            if search_query in record.name.value:
                match_found = True

            for phone in record.phones:
                if search_query in phone:
                    match_found = True
                    break 

            if match_found:
                matching_contacts.append(record)

        return matching_contacts

    # ==========================================        
# додавання/видалення/редагування необов'язкових полів та зберігання обов'язкового поля Name
class Record(): 
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = [phone] if phone else []
        self.birthday = birthday
        
    def add_phone(self, phone):
        self.phones.append(phone)
    def delete_phone(self, phone):
        self.phones.remove(phone)
    def modify_phone(self, phone):
        self.phones = phone
    
    def days_to_birthday(self):
        if self.birthday:
            current_date = datetime.now().date() # Отримуємо поточну дату
            value_date = datetime.strptime(self.birthday.value, '%d-%m-%Y').date() # Отримуємо дату дн
            
            if (value_date.month, value_date.day) < (current_date.month, current_date.day):
                next_birthday = value_date.replace(year=current_date.year + 1)
            else:
                next_birthday = value_date.replace(year=current_date.year)
            
            days_left = (next_birthday - current_date).days
            return days_left
        return "Birthday not provided"
        

class Field():
    def __init__(self, value):
        self.value = value
    
# обов'язкове поле з ім'ям
class Name(Field):
    pass

# необов'язкове поле з телефоном
class Phone(Field):
    def __init__(self):
        self.__value = None
    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, new_value):
        if not (re.match((r'\+380\(\d{2}\)\d{3}-\d{1,2}-\d{2,3}'), new_value) and len(new_value) == 17): # шаблон: +380(67)777-7-777 або +380(67)777-77-77
            raise ValueError("Invalid phone number")
        self.__value = new_value

# поле не обов'язкове, але може бути тільки одне.
class Birthday(Field):
    def __init__(self):
        self.__value = None
    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, new_value):
        try:
            date_obj = datetime.strptime(new_value, '%d-%m-%Y')
            current_year = datetime.now().year
            if 1900 <= date_obj.year <= current_year and 1 <= date_obj.month <= 12 and 1 <= date_obj.day <= 31:
                self.__value = new_value
            else:
                raise ValueError("Invalid birthdate format")
        except ValueError:
            raise ValueError("Invalid birthdate format")
            
  
  
name = Name('Bill')
phone = Phone()
phone.value = '+380(67)777-77-77'  # Правильний номер телефону згідно з шаблоном
birthday = Birthday()
birthday.value = '01-09-1990'  # Правильний формат дня народження
rec = Record(name, phone, birthday)
ab = AddressBook()
ab.add_record(rec)

assert isinstance(ab['Bill'], Record)
assert isinstance(ab['Bill'].name, Name)
assert isinstance(ab['Bill'].phones, list)
assert isinstance(ab['Bill'].phones[0], Phone)
assert ab['Bill'].phones[0].value == '+380(67)777-77-77'
print(ab['Bill'].days_to_birthday())  # Виведе кількість днів до наступного дня народження

# Збереження даних в файл
ab.save_to_file("address_book.csv")
# Відновлення даних з файлу
ab.load_from_file("address_book.csv")

# Перевірка, чи програма втратила дані
if "Bill" in ab:
    print("Data was not lost after exiting the program and was successfully restored from the file.")
else:
    print("Data was lost or could not be restored from the file.")

# Пошук користувачів за ім'ям або номером телефону
search_query = "Bill"  
matching_contacts = ab.search_contacts(search_query)

if matching_contacts:
    print(f"Matching contacts for '{search_query}':")
    for contact in matching_contacts:
        print(f"Name: {contact.name.value}, Phones: {', '.join(str(phone) for phone in contact.phones)}, BD: {contact.birthday}")

else:
    print(f"No matching contacts found for '{search_query}'.")