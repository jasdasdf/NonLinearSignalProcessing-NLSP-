import nlsp
import sumpf
import functools

def func(a=1, b=2, c=3):
    print a
    print b
    print c


array = [5,6,7]

func = functools.partial(func,a=444)

func()

