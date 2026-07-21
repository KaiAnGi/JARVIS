"""datetime_calc plugin - Time, date, and basic calculations."""

import re
from datetime import datetime
import locale

_NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000,
    "cero": 0, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9,
    "diez": 10, "once": 11, "doce": 12, "trece": 13,
    "catorce": 14, "quince": 15, "dieciséis": 16, "diecisiete": 17,
    "dieciocho": 18, "diecinueve": 19, "veinte": 20, "treinta": 30,
    "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70,
    "ochenta": 80, "noventa": 90, "cien": 100, "mil": 1000,
}

_DAYS_ES = {
    "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
    "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo",
}
_MONTHS_ES = {
    "January": "enero", "February": "febrero", "March": "marzo", "April": "abril",
    "May": "mayo", "June": "junio", "July": "julio", "August": "agosto",
    "September": "septiembre", "October": "octubre", "November": "noviembre", "December": "diciembre",
}


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "get_time":
        now = datetime.now().strftime("%I:%M %p")
        bus.emit("speak", f"Son las {now}")

    elif action == "get_date":
        now = datetime.now()
        day = _DAYS_ES.get(now.strftime("%A"), now.strftime("%A"))
        month = _MONTHS_ES.get(now.strftime("%B"), now.strftime("%B"))
        bus.emit("speak", f"Hoy es {day} {now.day} de {month} de {now.year}")

    elif action == "calculate":
        result = _calculate(text)
        if result is not None:
            bus.emit("speak", f"El resultado es {result}")
        else:
            bus.emit("speak", "No pude entender ese cálculo")


def _words_to_number(text: str) -> str:
    for word, num in sorted(_NUMBER_WORDS.items(), key=lambda x: -len(x[0])):
        text = text.replace(word, str(num))
    return text


def _calculate(text: str):
    text = text.lower()

    for prefix in ("calculate", "what is", "what's", "calcular", "cuánto es", "cuanto es"):
        if prefix in text:
            text = text.split(prefix, 1)[1]
            break

    text = _words_to_number(text)

    for word, op in [
        ("plus", "+"), ("minus", "-"), ("times", "*"),
        ("multiplied by", "*"), ("divided by", "/"), ("over", "/"),
        ("más", "+"), ("menos", "-"), ("por", "*"),
        ("multiplicado por", "*"), ("dividido entre", "/"), ("entre", "/"),
    ]:
        text = text.replace(word, op)

    tokens = re.findall(r"\d+\.?\d*|[+\-*/]", text)
    if not tokens:
        return None

    try:
        result = float(tokens[0])
        i = 1
        while i < len(tokens) - 1:
            op, num = tokens[i], float(tokens[i + 1])
            if op == "+":
                result += num
            elif op == "-":
                result -= num
            elif op == "*":
                result *= num
            elif op == "/":
                result = result / num if num != 0 else float("inf")
            i += 2
        return int(result) if result == int(result) else round(result, 10)
    except Exception:
        return None
