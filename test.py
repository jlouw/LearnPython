def spam(divideBy):
    try:
        return 42 / divideBy
    except ZeroDivisionError:
        print(str(ZeroDivisionError))

print(spam(2))
print(spam(12))
print(spam(0))
print(spam(1))

test = 10

hello = 10

hello = 20

hello = 10


wehat = 20

