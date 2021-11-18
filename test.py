import inspect

def foo():
   print(inspect.stack()[0][3])

foo()