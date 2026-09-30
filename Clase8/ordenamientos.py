def fibonacci(n):
    if n <= 1:
        return n

    return fibonacci(n-1) + fibonacci(n-2)

def fibonacci_dp(n):
    if n <= 1:
        return n

    F = [0] * (n+1)

    F[0] = 0
    F[1] = 1

    for i in range(2, n + 1):
        F[i] = F[i-1] + F[i-2]

    return F[n]