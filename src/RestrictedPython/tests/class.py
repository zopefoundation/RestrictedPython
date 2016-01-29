class MyClass:

    def set(self, val):
        self.state = val

    def get(self):
        return self.state

x = MyClass()
x.set(12)
x.set(x.get() + 1)
if x.get() != 13:
    raise AssertionError("expected 13, got %d" % x.get())
