def square(n):
    """
    Calculate the square of n

    >>> [square(n) for n in range(6)]
    [0, 1, 4, 9, 16, 25]
    """
    return n**2

if __name__ == "__main__":
    import doctest
    print(doctest.testmod(verbose=True))