import math
import re

char_bits = 7
mantissa_bits = 19

class Converter:
    def __init__(self, num, char_bits, mantissa_bits):
        self.number = num
        self.BIAS = (1 << (char_bits - 1)) - 1
        self.char_bits = char_bits
        self.mantissa_bits = mantissa_bits
        self.ieee_number = self.convert_dec_to_ieee754(self.number)

    def convert_dec_to_ieee754(self, num):
        special_cases = {
            '+inf': '0 1111111 0 0000000000000000000',
            '-inf': '1 1111111 0 0000000000000000000',
            'NaN': '0 1111111 1 0000000000000000000'
        }
        if num in special_cases:
            return special_cases[num]
        if num == 0:
            return "0" + " " + "0" * self.char_bits + " " + "0" + " " + "0" * self.mantissa_bits

        s = "0" if num >= 0 else "1"
        num = abs(num)

        k = math.floor(math.log(num, 2))
        k = max(k, -self.BIAS)

        char = self.convert_int_to_bin(k + self.BIAS, self.char_bits)

        m = num / (2 ** k)
        i_bit = "1" if 1 <= m < 2 else "0"
        m -= int(i_bit)

        mantissa = self.convert_float_to_bin(m, self.mantissa_bits)

        return f"{s} {char} {i_bit} {mantissa}"

    def convert_int_to_bin(self, num, bits):
        return bin(num)[2:].zfill(bits)

    def convert_float_to_bin(self, m, bits):
        n = ""
        for _ in range(bits):
            m *= 2
            bit = int(m)
            if m >= 1:
                m -= bit
                n += str(bit)
        return n

    def show_register(self):
        print(self.number)

class Processor:
    def __init__(self):
        self.stack = []
        self.num_of_registers = 8
        self.number_command_register = 0
        self.number_tact_register = 0

    def push_back_to_stack(self, reg):
        self.stack.append(reg)

    def print_info(self):
        print('TC: ', self.number_tact_register)
        print('PC: ', self.number_command_register)
        print()

    def show_stack(self):
        iteration = 1
        for reg in reversed(self.stack):
            print(f'R{iteration}: {reg.ieee_number}')
            iteration += 1
        print("___________________________________________")

    def load(self, value, char_bits, mantissa_bits):
        print(f"LOAD {value}:")
        self.push_back_to_stack(Converter(value, char_bits, mantissa_bits))
        self.number_tact_register = 1
        self.number_command_register += 1

    def multiply(self):
        print("MULT:")
        self.number_command_register += 1

        a = self.stack[-2].number
        b = self.stack[-1].number

        if a in ['+inf', '-inf'] or b in ['+inf', '-inf']:
            if (a == '+inf' and b != 0) or (a != 0 and b == '+inf'):
                result = '+inf'
            elif (a == '-inf' and b != 0) or (a != 0 and b == '-inf'):
                result = '-inf'
            else:
                result = 0
        else:
            result = a * b

        self.stack = self.stack[:-2]

        if result == 0:
            self.stack.extend([Converter(0, char_bits, mantissa_bits), Converter(0, char_bits, mantissa_bits)])
        else:
            self.stack.extend([Converter(0, char_bits, mantissa_bits),Converter(result, char_bits, mantissa_bits)])

        self.number_tact_register += 1

    def add(self):
        print("ADD:")
        self.number_command_register += 1
        a = self.stack[-1].number
        b = self.stack[-2].number
        if b == '+inf':
            result = '+inf'
        elif b == '-inf':
            result = '+inf'
        else:
            result = a + b
            self.stack = self.stack[:-2]
            self.push_back_to_stack(Converter(result, char_bits, mantissa_bits))
            self.number_tact_register += 1

    def swap(self):
        print("SWAP: ")
        self.number_command_register += 1
        a = self.stack[-1].number
        b = self.stack[-2].number
        self.stack = self.stack[:-2]
        a, b = b, a
        self.push_back_to_stack(Converter(b, char_bits, mantissa_bits))
        self.push_back_to_stack(Converter(a, char_bits, mantissa_bits))
        self.number_tact_register += 1

    def divide(self):
        print("DIV:")
        self.number_command_register += 1
        self.number_tact_register = 3
        divisor = self.stack[-1].number
        dividend = self.stack[-2].number

        if divisor == '+inf' or divisor == '-inf':
            if dividend == '+inf' or dividend == '-inf':
                result = 'NaN'
            else:
                    result = '+inf' if (divisor == '+inf' and dividend > 0) or (divisor == '-inf' and dividend < 0) else '-inf'

        elif dividend == '+inf':
            result = '+inf'
        elif dividend == '-inf':
            result = '-inf'
        elif divisor == 0 and dividend > 0:
            result = '+inf'
        elif divisor == 0 and dividend < 0:
            result = '-inf'
        elif divisor == 0 and dividend == 0:
            result = 'NaN'
        else:
            result = dividend / divisor

        self.stack = self.stack[:-2]

        if result == 0:
            self.push_back_to_stack(Converter(0, char_bits, mantissa_bits))
            self.push_back_to_stack(Converter(0, char_bits, mantissa_bits))
        elif result == 'NaN':
            self.push_back_to_stack(Converter(0, char_bits, mantissa_bits))
            self.push_back_to_stack(Converter('NaN', char_bits, mantissa_bits))
        else:
            self.push_back_to_stack(Converter(0, char_bits, mantissa_bits))
            self.push_back_to_stack(Converter(0, char_bits, mantissa_bits))
            self.push_back_to_stack(Converter(result, char_bits, mantissa_bits))

    def commands(self):
        a = self.stack[-2].number
        b = self.stack[-1].number
        del self.stack[-1]
        del self.stack[-1]
        print("Press enter to continue...")
        input()
        self.load(a, char_bits, mantissa_bits)

        self.show_stack()
        self.print_info()
        del self.stack[-8]
        print("Press enter to continue...")
        input()
        self.load(b, char_bits, mantissa_bits)
        self.show_stack()
        self.print_info()
        print("Press enter to continue...")
        input()
        self.multiply()
        self.show_stack()
        self.print_info()
        del self.stack[-8]
        print("Press enter to continue...")
        input()
        self.load(b, char_bits, mantissa_bits)
        self.show_stack()
        self.print_info()
        del self.stack[-8]
        print("Press enter to continue...")
        input()
        self.load(2.4, char_bits, mantissa_bits)
        self.show_stack()
        self.print_info()
        print("Press enter to continue...")
        input()
        self.add()
        self.show_stack()
        self.print_info()
        print("Press enter to continue...")
        input()
        self.divide()
        self.show_stack()
        self.print_info()

        print("___________________________________________")
        print("Res: ", self.stack[-1].ieee_number)
        print("Num: ", end='')
        self.stack[-1].show_register()
        print("___________________________________________")


def main():
    p = Processor()
    a_str = input("Enter a: ")
    b_str = input("Enter b: ")

    print("0 1111111 0 0000000000000000000 <<< inf \n"
            "1 1111111 0 0000000000000000000 <<< -inf \n"
            "0 1111111 1 0000000000000000000 <<< NaN \n"
            "0 1111110 1 1111111111111111111 <<< max \n"
            "1 1111110 1 1111111111111111111 <<< min \n")

    a = float(a_str) if not re.match(r'^[0-9]+(\.[0-9]*)?e[+-]?\d+$', a_str.lower()) else float(a_str)
    b = float(b_str) if not re.match(r'^[0-9]+(\.[0-9]*)?e[+-]?\d+$', b_str.lower()) else float(b_str)

    for _ in range(7):
        p.push_back_to_stack(Converter(0, char_bits, mantissa_bits))

    def handle_infinities(value):
        if value > 2 ** (2 ** (char_bits - 1)):
            return Converter('+inf', char_bits, mantissa_bits)
        elif value < -2 ** (2 ** (char_bits - 1)):
            return Converter('-inf', char_bits, mantissa_bits)
        elif 'e' in str(value).lower():
            return Converter(float(value), char_bits, mantissa_bits)
        else:
            return Converter(value, char_bits, mantissa_bits)

    p.push_back_to_stack(handle_infinities(a))
    p.push_back_to_stack(handle_infinities(b))

    print("F = (a * b)/(b + 2.4)")
    print()

    p.commands()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("You've ended this session")
    except BaseException:
        print("Something unexpected happened")