class A:
    y = 213

    def __init__(self):
        self.x = 'Hello'

    def method_a(self, foo):
        print self.x + ' ' + foo + ' ' + str(self.y)