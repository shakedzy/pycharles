def int_to_binary_string(n):
    """
    Return the binary representation of the number n
    :param n: a number
    :return: a binary representation of n as a string
    """
    return '{0:b}'.format(n)


def binary_string_to_int(s):
    """
    Convert a string of a binary representation to a number
    :param s: a binary representation as a string
    :return: an integer
    """
    return int(s,2)


def get_single_gene_bits_num(values, position=None):
    """
    Returns the max length required to represent any value
    of values as a binary sequence. For example, for values
    [0,1,2] which are converted to [0,1,10], the max length
    is 2.
    :param values: the values that will bre represented as binary sequences
    :param position: if values is a dictionary, to which key in the dictionary
                     this calculation should be applied to
    :return: max length as an integer
    """
    if isinstance(values, dict):
        values = values[position]
    return len(int_to_binary_string(len(values) - 1))


def get_value_of_binary_string(binary_string, values, position=None):
    """
    A helper function that decodes the binary-bits string provided and returns the
    value it refers to. It also handles the situation where the binary-string decoding
    points to a value that does not exist.

    :param binary_string: a string of a binary encoding of one of the values in the values sequence
    :param values: all possible values that the binary string can be decoded to
    :param position: if values is a dictionary, to which key should the function refer
    :return: the decoded value
    """
    if isinstance(values, dict):
        values = values[position]
    return values[binary_string_to_int(binary_string) % len(values)]


def pad_binary_string(binary_string, required_length):
    """
    Pads a binary string with additional zeros.
    Example: pad_binary_string('101',5) -> '00101'

    :param binary_string: a binary representation as a string
    :param required_length: the number of digits required in the output binary string
    :return: a binary representation as a string with additional zeros
    """
    padding_size = required_length - len(binary_string)
    padding = ''.join(['0']*padding_size)
    return padding + binary_string


def flip_bit_char(bit):
    """
    lips the character '1' to '0' and vice-versa. Throws an error for any other value.

    :param bit: a string, either '1' or '0'
    :return: the flipped binary character
    """
    if bit == '1':
        return '0'
    elif bit == '0':
        return '1'
    else:
        raise ValueError("No such bit-char: {}".format(bit))


def seq_to_binary_string(sq, values):
    """
    Convert each value in a sequence to a binary encoding of it, based on the provided values.

    Examples:
    >>> seq_to_binary_string(['X','Z'], ['X','Y','Z'])
    '0010'
    >>> seq_to_binary_string(['Y,','Z'], ['X','Y','Z'])
    '0110'
    >>> seq_to_binary_string(['Z,'Z'], ['X','Y','Z'])
    '1010'

    :param sq: the sequence of values to encode to a binary representation
    :param values: list or dict. all possible values each element of the sequence can have
    :return: a string made of binary encoding of the sequence provided
    """
    if isinstance(values, dict):
        binary_string = ''
        for position, vals in values.items():
            binary = int_to_binary_string(vals.index(sq[position]))
            binary_length = get_single_gene_bits_num(vals)
            padded = pad_binary_string(binary, binary_length)
            binary_string += padded
    else:
        binaries = map(lambda x: int_to_binary_string(values.index(x)), sq)
        binary_length = get_single_gene_bits_num(values)
        padded = list(map(lambda x: pad_binary_string(x,binary_length),binaries))
        binary_string = ''.join(padded)
    return binary_string


def binary_string_to_seq(binary_string, values):
    """
        Convert a string of a binary representation to a subject in the population. This is the opposite
        of seq_to_binary_string.

        Examples:
        >>> binary_string_to_seq('0010',['X','Y','Z'])
        ['X','Y']
        >>> binary_string_to_seq('0110',['X','Y','Z'])
        ['Y','Z']
        >>> binary_string_to_seq('1010',['X','Y','Z'])
        ['Z','Z']

        :param sq: the sequence of values to encode to a binary representation
        :param values: list or dict. all possible values each element of the sequence can have
        :return: string made of binary encoding of the sequence provided
        """
    if isinstance(values, dict):
        sq = list()
        starting_point = 0
        for position in range(0,len(values)):
            gene_size = get_single_gene_bits_num(values[position])
            binary_gene = binary_string[starting_point:starting_point+gene_size]
            sq.append(get_value_of_binary_string(binary_gene,values[position]))
            starting_point += gene_size
    else:
        gene_size = get_single_gene_bits_num(values)
        binary_genes = [binary_string[i:i+gene_size] for i in range(0,len(binary_string),gene_size)]
        sq = list(map(lambda x: get_value_of_binary_string(x, values), binary_genes))
    return sq
