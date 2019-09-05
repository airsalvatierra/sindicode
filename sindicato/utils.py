from itertools import cycle

def validarRut(rut):

    rut = rut.upper();
    rut = rut.replace("-","")
    rut = rut.replace(".","")
    aux = rut[:-1]
    if not aux.isdigit() :
        print('no es entero')
        return False
    dv = rut[-1:]

    revertido = map(int, reversed(str(aux)))
    factors = cycle(range(2,8))
    s = sum(d * f for d, f in zip(revertido,factors))
    res = (-s)%11

    if str(res) == dv:
        return True
    elif dv=="K" and res==10:
        return True
    else:
        return False

def formatRut(rut):
    aux = rut[:-1]
    dv = rut[-1:]
    length = len(aux)
    print(length)

    if length>7:
        rutFormateado = aux[0]+aux[1]+"."+aux[2]+aux[3]+aux[4]+"."+aux[5]+aux[6]+aux[7]+"-"+dv
    else:
        rutFormateado = aux[0]+"."+aux[1]+aux[2]+aux[3]+"."+aux[4]+aux[5]+aux[6]+"-"+dv

    return rutFormateado
