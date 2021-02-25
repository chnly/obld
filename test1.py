list_a = [lambda x: x*i for i in range(4)]
list_b = [x(3) for x in list_a]
print(type(list_a[0]))
print(list_b)