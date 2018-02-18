def int_to_binary_string(n):
    return '{0:b}'.format(n)


def binary_string_to_int(s):
    return int(s,2)


def get_single_gene_bits_num(values):
    return len(int_to_binary_string(len(values) - 1))


def get_value_of_binary_string(binary_string, values):
    return values[binary_string_to_int(binary_string) % len(values)]


def pad_binary_string(binary_string, required_length):
    padding_size = required_length - len(binary_string)
    padding = ''.join(['0']*padding_size)
    return padding + binary_string


def flip_bit_char(bit):
    if bit == '1':
        return '0'
    elif bit == '0':
        return '1'
    else:
        raise ValueError("No such bit-char: {}".format(bit))


def seq_to_binary_string(sq, values):
    binarys = map(lambda x: int_to_binary_string(values.index(x)), sq)
    binary_length = get_single_gene_bits_num(values)
    padded = list(map(lambda x: pad_binary_string(x,binary_length),binarys))
    return ''.join(padded)


def binary_string_to_seq(binary_string, values):
    gene_size = get_single_gene_bits_num(values)
    binary_genes = [binary_string[i:i+gene_size] for i in range(0,len(binary_string),gene_size)]
    return list(map(lambda x: get_value_of_binary_string(x, values), binary_genes))
