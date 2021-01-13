class Animal:
    cprop = "我是类上的属性cprop"

    def __init__(self, name, speed):
        self.name = name
        self.speed = speed

    def __str__(self):
        return '''Animal({0.name},{0.speed}) is printed
                name={0.name}
                speed={0.speed}'''.format(self)


cat = Animal('加菲猫', 8)
cat.color = 'grap'
print(cat)
print(Animal.cprop)
