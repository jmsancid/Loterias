#!/usr/bin/env python3
# -*- coding: cp1252 -*-

import constants as cte
from clases import PrimiComb, EuroComb

from typing import Union, Dict, List


def getSeason(fecha) -> int:
    """
    Devuelve la estación del año a la que pertenece 'fecha'

    :param fecha: objeto datetime que necesita al menos mes y día del mes
    :return: valor entero
        PRIMAVERA = 1 desde 0321 a 0620
        VERANO = 2 desde 0621 a 0920
        OTOCHO = 3 desde 0921 a 1220
        INVIERNO = 4 resto de fechas
    """
    mesDia = fecha.month * 100 + fecha.day
    match mesDia:
        case intervalo if 321 <= intervalo < 620:
            estacion = cte.PRIMAVERA
        case intervalo if 621 <= intervalo < 920:
            estacion = cte.VERANO
        case intervalo if 921 <= intervalo < 1220:
            estacion = cte.OTONO
        case _:
            estacion = cte.INVIERNO
    return estacion


def seleccionaCombinaciones(estadisticas:Dict, numerosExcluidos:Union[List,None]=None, qCombinaciones:int=5) -> List:
    """
    Selecciona qCombinaciones a partir del diccionario con la frecuencia con la que ha
    salido cada número en cada posición
    :param estadisticas: diccionario con la frecuencia con la que han salido los números en los sorteos.
    Las claves son los identificadores de las posiciones de los números: n1, n2,,, re / e1, e2
    :param numerosExluidos: lista con números que no queremos usar, por ejemplo, los del último sorteo
    :param qCombinaciones: cantidad de combinaciones a devolver en la lista
    :return: lista con las combinaciones seleccionadas. Los elementos de la lista son objetos del tipo
    PrimiComb o EuroComb
    """
    esPrimitiva = True if "re" in estadisticas.keys() else False
    if numerosExcluidos is None:    # numerosExcluidos se utiliza para no repetir números y no incluir los de la
        # semana anterior (en desarrollo). No afecta ni a reintegros de primitiva ni a estrellas 1 y 2 de euromillón
        numerosExcluidos = []
    reintegrosExcluidos = [None]
    estrellasExcluidas = []
    combinaciones = []
    added = False
    qValores = len(estadisticas.get(tuple(estadisticas.keys())[0]))
    rango = min(qValores, qCombinaciones)
    for combinacionId in range(rango):
        comb = PrimiComb() if esPrimitiva else EuroComb()
        for numId, num in estadisticas.items():
            candidatos = [n[0] for n in estadisticas.get(numId)]    # lista con los candidatos de una determinada
            # posición n1, n2.. ordenados por frecuencia
            for i in range(len(candidatos)):
                if not (candidatos[i] in numerosExcluidos) and not numId in ['re', 'e1', 'e2']:
                    setattr(comb, numId, candidatos[i])
                    numerosExcluidos.append(candidatos[i])
                    added = True
                    break
                elif not (candidatos[i] in reintegrosExcluidos) and numId == 're':
                    setattr(comb, numId, candidatos[i])
                    reintegrosExcluidos.append(candidatos[i])
                    added = True
                    break
                elif not (candidatos[i] in estrellasExcluidas) and numId in ['e1', 'e2']:
                    setattr(comb, numId, candidatos[i])
                    estrellasExcluidas.append(candidatos[i])
                    added = True
                    break

            if not added:   # no se ha utilizado ningún candidato
                # tomo un candidato que no esté en la combinación actual
                numCombActual = comb.__dict__.values()
                for candidato in candidatos:
                    # utilizo un candidato no usado en la combinación actual en otra posición
                    if not candidato in numCombActual:
                        setattr(comb, numId, candidato)
            added = False

        comb.ordena()
        combinaciones.append(comb)
    return combinaciones


def printCombinaciones(titulo:str, combinaciones:List) -> int:
    """
    imprime a consola las combinaciones seleccionadas según el método __repr__ de
    las dataclasses PrimiComb y EuroComb.

    :param titulo: descripción del sorteo al que corresponden las combinaciones
    :param combinaciones: lista con las combinaciones en forma de objeto PrimiComb o EuroComb
    :return: 0 si la operación termina correctamente
    """
    print(f"\n{titulo.upper()}")
    esPrimitiva = True if isinstance(combinaciones[0], PrimiComb) else False
    if esPrimitiva:
        for comb in combinaciones:
            print(f"{comb.n1:<2} {comb.n2:<2} {comb.n3:<2} {comb.n4:<2} {comb.n5:<2} {comb.n6:<2}\tRe-{comb.re}")
    else:
        for comb in combinaciones:
            print(f"{comb.n1:<2} {comb.n2:<2} {comb.n3:<2} {comb.n4:<2} {comb.n5:<2}\te1-{comb.e1:<2} e2-{comb.e2}")
    print("___________________")
    return 0


def combinacionExistente(comb: Union[PrimiComb, EuroComb], listaComb: List[Union[PrimiComb, EuroComb]],
                         conFecha: bool = True) -> bool:
    """
    si la combinación 'comb' está en la lista de combinaciones devuelve true. si no, devuelve false
    :param comb: combinación a verificar si está en la lista de combinaciones
    :param listaComb: lista de combinaciones en la que se comprueba la existencia de 'comb'
    :param conFecha: indica si se tiene en cuenta la fecha o no.
    La fecha se tiene en cuenta a la hora de comprobar si hay que añadir una combinación a la lista de
    combinaciones seleccionadas y no se tiene en cuenta al comprobar si una determinada combinación ha sido premiada
    :return: True si 'comb' está en 'listaComb'. False si no está o los elementos de 'listaComb' son de un tipo
    diferente a 'comb'
    """
    comb_en_listaComb = False

    # compruebo si hay algo que comparar
    nothing_to_search = True if comb is None or listaComb == [] or listaComb is None else False
    if nothing_to_search:
        return comb_en_listaComb

    types_match = all([type(comb) == type(c) for c in listaComb])
    if not types_match:
        return comb_en_listaComb

    if conFecha:    # hay que comprobar también la fecha
        comb_en_listaComb = any(comb.__eq__(c) for c in listaComb)
    else:
        comb_en_listaComb = any(comb.compara_sin_fecha(c) for c in listaComb)

    return comb_en_listaComb


def check_to_add(comb_sel: List[Union[PrimiComb, EuroComb]], comb_list: List) -> List:
    """
    Comprueba si en comb_list hay combinaciones con la misma fecha que comb_sel.
    Si no las hay, comprueba si ya existen en comb_list y, si no existen, las añade.

    IMPORTANTE: antes de llamar a esta función hay que asignarle fecha a la combinación
    :param comb_sel: lista de combinaciones a comprobar si se añaden o no al histórico
    :param comb_list: lista de combinaciones histórica
    :return: lista de combinaciones histórica actualizada
    """
    list_comb_to_add = []
    for comb in comb_sel:
        add_comb = False
        if not any([comb.combDate == allcomb.combDate for allcomb in comb_list]):
            # no hay combinaciones guardadas con la fecha de comb
            if not any([comb.compara_sin_fecha(allcomb) for allcomb in comb_list]):
                # tampoco hayguardada ninguna combinación igual que comb
                add_comb = True
                list_comb_to_add.append(comb)
        if not add_comb:
            print(f"{__name__}. La combinación {comb} ya se había guardado anteriormente")
    comb_list += list_comb_to_add
    return comb_list


def comprueba_premios(year:int, week_number:int, combinaciones: Dict):
    """
    Para una determinada semana de un determinado año, comprueba los aciertos comparando la combinación ganadora
    con las combinaciones seleccionadas.
    :param year: año a evaluar
    :param week_number: semana a evaluar
    :param combinaciones: diccionario con todas las combinaciones ganadoras y las seleccionadas por el programa
    :return: 0 si all is right
    """
    combinaciones_primi_ganadoras = combinaciones.get("primiResults")
    if combinaciones_primi_ganadoras is None:
        print("\n\t No se han encontrado las combinaciones ganadoras de la primitiva en la semana indicada")
    else:
        comb_primi_ganadoras_ultima_semana = [comb for comb in combinaciones_primi_ganadoras
                                              if comb.combDate.year==year and
                                              comb.combDate.isocalendar().week == week_number]
        # comb_primi_sel = combinaciones.get("allPrimi") + \
        #                  combinaciones.get("allPrimiSeason") + \
        #                  combinaciones.get("allPrimiWeek") + \
        #                  combinaciones.get("primiLunes") + \
        #                  combinaciones.get("primiLunesSeason") + \
        #                  combinaciones.get("primiLunesWeek") + \
        #                  combinaciones.get("primiJueves") + \
        #                  combinaciones.get("primiJuevesSeason") + \
        #                  combinaciones.get("primiJuevesWeek") + \
        #                  combinaciones.get("primiSabado") + \
        #                  combinaciones.get("primiSabadoSeason") + \
        #                  combinaciones.get("primiSabadoWeek")
        primi_calc_group = [field for field in combinaciones.keys() if "primi" in str(field).lower() and not "results" in str(field).lower()]

        sin_aciertos = True
        for sorteo in primi_calc_group:
            primi_group = combinaciones.get(sorteo)
            combinaciones_primi_seleccionadas = [comb for comb in primi_group
                                                 if comb.combDate.year == year and
                                                 comb.combDate.isocalendar().week == week_number]
            for comb1 in combinaciones_primi_seleccionadas:
                for comb2 in comb_primi_ganadoras_ultima_semana:
                    aciertos_msg = cuenta_aciertos(comb1, comb2)
                    if aciertos_msg:
                        aciertos_msg = f"{sorteo}: {cuenta_aciertos(comb1, comb2)}"
                        sin_aciertos = False
                        print(aciertos_msg)
        if sin_aciertos:
            msg = f"La semana {week_number} no ha habido aciertos de primitiva"
            print(msg)

    combinaciones_euro_ganadoras = combinaciones.get("euroResults")
    if combinaciones_euro_ganadoras is None:
        print("\n\t No se han encontrado las combinaciones ganadoras de euromillones en la semana indicada")
    else:
        comb_euro_ganadoras_ultima_semana = [comb for comb in combinaciones_euro_ganadoras
                                             if comb.combDate.year==year and
                                             comb.combDate.isocalendar().week==week_number]
        # comb_euro_sel = combinaciones.get("allEuro") + \
        #                 combinaciones.get("allEuroSeason") + \
        #                 combinaciones.get("allEuroWeek") + \
        #                 combinaciones.get("euroMartes") + \
        #                 combinaciones.get("euroMartesSeason") + \
        #                 combinaciones.get("euroMartesWeek") + \
        #                 combinaciones.get("euroViernes") + \
        #                 combinaciones.get("euroViernesSeason") + \
        #                 combinaciones.get("euroViernesWeek")
        euro_calc_group = [field for field in combinaciones.keys() if "euro" in str(field).lower() and not "results" in str(field).lower()]
        # combinaciones_euro_seleccionadas = [comb for comb in comb_euro_sel
        #                                     if comb.combDate.year == year and
        #                                     comb.combDate.isocalendar().week == week_number]

        sin_aciertos = True
        for sorteo in euro_calc_group:
            euro_group = combinaciones.get(sorteo)
            combinaciones_euro_seleccionadas = [comb for comb in euro_group
                                                 if comb.combDate.year == year and
                                                 comb.combDate.isocalendar().week == week_number]
            for comb1 in combinaciones_euro_seleccionadas:
                for comb2 in comb_euro_ganadoras_ultima_semana:
                    aciertos_msg = cuenta_aciertos(comb1, comb2)
                    if aciertos_msg:
                        aciertos_msg = f"{sorteo}: {cuenta_aciertos(comb1, comb2)}"
                        sin_aciertos = False
                        print(aciertos_msg)
        if sin_aciertos:
            msg = f"La semana {week_number} no ha habido aciertos de euromillón"
            print(msg)

    return 0  # alright


def cuenta_aciertos(comb1: Union[PrimiComb, EuroComb], comb2:Union[PrimiComb, EuroComb]) -> Union[str, None]:
    """
    comprueba cuantos números de comb1 aparecen en comb2. Comb2 debe ser una combinación premiada
    :param comb1: combinación de primitiva o euromillones
    :param comb2: idem comb1
    :return: número de aciertos o None si comb1 y comb2 son de distinto tipo
    """
    if type(comb1) != type(comb2):
        print(f"{comb1} y {comb2} son de distinto tipo. Deben ser ambas de euromillones o de primitiva")
        return

    # atributos de los números
    num_fields = [num_attrib for num_attrib in comb1.__dict__.keys() if "n" in num_attrib]
    # hago un set con todos los números de comb1 y comb2
    result = set([getattr(comb1, n) for n in num_fields] + [getattr(comb2, n) for n in num_fields])
    aciertos = 2 * len(num_fields) - len(result)

    msg = ""
    if comb1.__class__.__name__ == "PrimiComb":
        reintegro = True if comb1.re == comb2.re else False
        if aciertos >= 3:
            msg = f"En {comb1} ha habido {aciertos} aciertos sobre {comb2}"
            if reintegro:
                msg = msg + f" y el reintegro, {comb1.re}"
        elif reintegro:
            msg = f"En {comb1} se ha acertado el reintegro sobre {comb2}"
        # else:
        #     msg = f"{comb1} no ha tenido aciertos"
    else:   # comprobación de euromillones
        comb1_y_comb2_stars = [comb1.e1, comb1.e2, comb2.e1, comb2.e2]
        estrellas_acertadas = 4 - len(set(comb1_y_comb2_stars))
        if aciertos == 1:
            if estrellas_acertadas == 2:
                msg = f"En {comb1} se ha acertado {aciertos} número"
                msg = msg + f" y {estrellas_acertadas} estrellas sobre {comb2}."
        elif aciertos:  # hay 2 aciertos o más
            msg = f"En {comb1} se han acertado {aciertos} números sobre {comb2}"
            if estrellas_acertadas:
                msg1 = f" y {estrellas_acertadas} estrella"
                msg2 = f" y {estrellas_acertadas} estrellas"
                msg = msg + msg1 if estrellas_acertadas == 1 else msg + msg2
        # else:
        #     msg = f"{comb1} no ha tenido aciertos"
    return msg

