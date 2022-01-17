from math import atan, cos, sqrt, degrees, radians
from turtle import forward, left, right


def house(width, height, roof_angle):
    draw_rectangle(width, height)
    draw_diagonals(height, width)
    draw_roof(roof_angle, width)


def draw_roof(roof_angle, width):
    roof_side_angle = (180 - roof_angle) / 2
    roof_size = (width / 2) / cos(radians(roof_side_angle))

    left(90 - roof_side_angle)
    forward(roof_size)
    left(180 - roof_angle)
    forward(roof_size)


def draw_diagonals(height, width):
    diagonal_size = sqrt(width ** 2 + height ** 2)
    diagonal_angle = degrees(atan(height/width))

    right(diagonal_angle)
    forward(diagonal_size)
    right(180 - diagonal_angle)
    forward(width)
    right(180 - diagonal_angle)
    forward(diagonal_size)
    left(90 - diagonal_angle)


def draw_rectangle(width, height):
    for i in range(2):
        forward(width)
        right(90)
        forward(height)
        right(90)


def largest_on_path(num):
    max_num = num
    while num != 1:
        if num % 2 == 0:
            num //= 2
        else:
            num = num * 3 + 1
        if max_num < num:
            max_num = num
    return max_num


def nth_exact_multi_prime_divisor(num, power, index):
    num_index = 0
    if num % 2 == 0:
        prime_num = 2
    else:
        prime_num = next_prime_div(3, num)
    while num > 1:
        if prime_num is None:
            break
        num_rate = get_num_rate(num, prime_num)
        if power == num_rate:
            num_index += 1
            if num_index == index:
                return prime_num
        num //= prime_num ** num_rate
        prime_num += 1
        prime_num = next_prime_div(prime_num, num)


def get_num_rate(num, div):
    count = 0
    while num % div == 0:
        count += 1
        num //= div
    return count


def next_prime_div(start, num):
    if start % 2 == 0:
        start += 1
    for i in range(start, num + 1, 2):
        if num % i == 0 and is_prime_num(i):
            return i


def is_prime_num(num):
    end = int(sqrt(num)) + 1
    for i in range(3, end, 2):
        if num % i == 0:
            return False
    return True


def main():
    # you have to check the output of house yourself

    assert largest_on_path(1) == 1
    assert largest_on_path(19) == 88
    assert largest_on_path(20) == 20
    assert largest_on_path(27) == 9232

    assert nth_exact_multi_prime_divisor(18, 1, 1) == 2
    assert nth_exact_multi_prime_divisor(18, 1, 2) is None
    assert nth_exact_multi_prime_divisor(39083, 1, 1) == 17
    assert nth_exact_multi_prime_divisor(39083, 1, 2) == 19
    assert nth_exact_multi_prime_divisor(254100, 1, 2) == 7
    assert nth_exact_multi_prime_divisor(254100, 2, 3) == 11
    assert nth_exact_multi_prime_divisor(254100, 3, 1) is None


if __name__ == '__main__':
    main()
