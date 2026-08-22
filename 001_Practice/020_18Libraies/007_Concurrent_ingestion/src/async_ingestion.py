from concurrent.futures import ProcessPoolExecutor


def calculate(number):

    return number * number


numbers = [1, 2, 3, 4, 5]


with ProcessPoolExecutor(max_workers=4) as executor:

    results = list(
        executor.map(calculate, numbers)
    )


print(results)``