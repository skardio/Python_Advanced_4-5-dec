class Bankaccount():
    def __init__(self, balance, holder):
        self.__balance = balance
        self.__holder = holder
    
    def deposit(self, amount):
        self.__balance += amount
    
    def withdraw(self, amount):
        self.__balance -= amount
    
    def info(self):
        return f"Holder: {self.__holder}, Balance: {self.__balance}."

ba1 = Bankaccount(200, 'Tessel')
ba2 = Bankaccount(700, 'Peter')

print(ba1.info())
ba1.deposit(300)
print(ba1.info())


print(ba2.info())
ba2.withdraw(300)
print(ba2.info())