from django import template

register = template.Library()

@register.filter
def rut_format(value, separator="."):
    """
    Formats a given RUT
    Args:
        value (str): Given RUT
        separator (str): Char used for thousands separator, by default it's ','
    Returns:
        str: Formatted RUT
    """
    # if 'div' in value:
    #     ini = value.find('value=\"')
    #     lista = value[ini:]
    #     temp = lista.split('value=\"')
    #     temp2 = temp[1].split('\"')
    #     value = temp2[0]

    # Unformat the RUT
    value = rut_unformat(value)

    rut, verifier_digit = value[:-1], value[-1]

    try:
        # Add thousands separator
        rut = "{0:,}".format(int(rut))

        # If you specified another thousands separator instead of ','
        if separator != ",":
            # Apply the custom thousands separator
            rut = rut.replace(",", separator)

        return "%s-%s" % (rut, verifier_digit)
    except ValueError:
        # If the RUT cannot be converted to Int
        raise template.TemplateSyntaxError("RUT must be numeric, in order to be formatted, Value: " + rut)


@register.filter
def rut_unformat(value):
    """
    It's the opposite of rut_format
    Args:
        value (str): Given RUT
    """
    return value.replace("-", "").replace(".", "").replace(",", "")
