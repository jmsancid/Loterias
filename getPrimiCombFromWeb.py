#!
# -*- coding: cp1252 -*-

import requests
import constants as cte
import re
import time

from datetime import datetime, timedelta


def getPrimiLatestResults():
    '''
    Devuelve un diccionario con los resultados de primitiva del último mes, siendo la clave una cadena
    con la fecha y el valor una lista con los números extraídos.
    La fecha final corresponde al lunes de la semana siguiente a la actual y la fecha inicial a la del lunes de
    5 semanas atrás
    :return: diccionario {fecha: [num1, num2, num3, num4, num5, num6, comp, re]}
            1 si ha habido algún error
    '''
    # En 2025 he tenido que cambiar la forma de extraer los números de la primitiva, utilizando una script que
    # encontré mientras inspeccionaba la web de primitivas y que se llama buscadorSorteos
    next_monday = datetime.now() + timedelta(days=8-datetime.now().isoweekday())
    four_mondays_ago = next_monday + timedelta(weeks=-4)


    url = 'https://www.loteriasyapuestas.es/servicios/buscadorSorteos'
    headers = {
        'Host': 'www.loteriasyapuestas.es',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'X-Requested-With': 'XMLHttpRequest',
        'Alt-Used': 'www.loteriasyapuestas.es',
        'Connection': 'keep-alive',
        'Referer': 'https://www.loteriasyapuestas.es/es/resultados/primitiva',
        'Cookie': 'usr-lang=es; UUID=WEB-b5034850-cfee-4bc8-9c03-3f7c2c7e4179; '
                  'CookieConsent={stamp:%271UCnsPBJe8OGTadACzKrwaj8WPRPRWzQh+AUa9ZQnF8dtK0egRLfxQ=='
                  '%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:'
                  '%27explicit%27%2Cver:1%2Cutc:1740931548034%2Cregion:%27es%27}'
    }

    params = {
        'game_id': 'LAPR',
        'celebrados': 'true',
        'fechaInicioInclusiva': f"{four_mondays_ago.year}{four_mondays_ago.month:02d}{four_mondays_ago.day:02d}",
        'fechaFinInclusiva': f"{next_monday.year}{next_monday.month:02d}{next_monday.day:02d}"
    }

    response = requests.get(cte.PRIMIWEB, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error accediendo a la web {cte.PRIMIWEB}\n Código de Error: {response.status_code}")
        return 1
    print('++++++++++++++   COMBINACIONES PRIMITIVA +++++++++++++++++')
    #
    sorteos = response.json()  # En 2025, la web de primitivas devuelve un json con los resultados.
    combinaciones_extraidas = {}
    for sorteo in sorteos:
        fecha = sorteo.get("fecha_sorteo")
        if fecha is None:
          continue
        str_comb = sorteo.get("combinacion")
        combinaciones_extraidas[fecha[0:10]] = list(map(int, re.findall(r'\d+', str_comb)))
    return combinaciones_extraidas


# # print(get_primi_latest_results())
#
# # Ejemplo de uso
# if __name__ == "__main__":
#     # # Fecha de ejemplo: 5 de enero de 2025
#     # fecha_ejemplo = datetime(2025, 1, 5)
#     resultados = getPrimiLatestResults()
#     print(resultados)
