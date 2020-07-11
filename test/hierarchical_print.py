from varname import nameof
from functions import nested_print

# ##### EXECUTE CODE #####


if __name__ == '__main__':
    snarg = dict()
    snarg[100] = 300
    snarg['AA'] = 'BB'

    piffle = dict()
    piffle[10] = 30
    piffle['A'] = 'B'
    piffle['C'] = snarg

    blarvitz = dict()
    blarvitz[1] = 3
    blarvitz['a'] = 'b'
    blarvitz['c'] = piffle

    name = nameof(blarvitz)
    nested_print(name, blarvitz)

    print()
    print()

    if not isinstance(blarvitz, dict):
        print("Huh?")
    else:
        for key1, value1 in blarvitz.items():
            if isinstance(key1, int):
                key1_value = "[%d]" % key1
            elif isinstance(key1, str):
                key1_value = "['%s']" % key1
            else:
                raise NotImplementedError

            if isinstance(value1, int):
                value1_value = "%d" % value1
            elif isinstance(value1, str):
                value1_value = "'%s'" % value1
            else:
                raise NotImplementedError

            if not isinstance(value1, dict):
                print("%s%s = %s" % (name, key1_value, value1_value))
            else:
                name = name + key1_value
                for key2, value2 in value1.items():
                    if isinstance(key2, int):
                        key2_value = "[%d]" % key2
                    elif isinstance(key2, str):
                        key2_value = "['%s']" % key2
                    else:
                        raise NotImplementedError

                    if isinstance(value2, int):
                        value2_value = "%d" % value2
                    elif isinstance(value2, str):
                        value2_value = "'%s'" % value2
                    else:
                        raise NotImplementedError

                    if not isinstance(value2, dict):
                        print("%s%s = %s" % (name, key2_value, value2_value))
                    else:
                        name = name + key2_value
                        for key3, value3 in value2.items():
                            if isinstance(key3, int):
                                key3_value = "[%d]" % key3
                            elif isinstance(key3, str):
                                key3_value = "['%s']" % key3
                            else:
                                raise NotImplementedError

                            if isinstance(value3, int):
                                value3_value = "%d" % value3
                            elif isinstance(value3, str):
                                value3_value = "'%s'" % value3
                            else:
                                raise NotImplementedError

                            if not isinstance(value3, dict):
                                print("%s%s = %s" % (name, key3_value, value3_value))
