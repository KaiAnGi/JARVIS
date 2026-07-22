"""chitchat plugin - Conversational responses and small talk."""

import random
from datetime import datetime

from core.language import resp, get_lang


def init(bus):
    pass


def handle(action: str, text: str, bus):
    lang = get_lang()
    hour = datetime.now().hour

    if action == "greeting":
        bus.emit("speak", _greeting(lang, hour))

    elif action == "how_are_you":
        bus.emit("speak", _how_are_you(lang))

    elif action == "who_are_you":
        bus.emit("speak", _who_are_you(lang))

    elif action == "thanks":
        bus.emit("speak", _thanks(lang))

    elif action == "compliment":
        bus.emit("speak", _compliment(lang))

    elif action == "insult":
        bus.emit("speak", _insult(lang))

    elif action == "status":
        bus.emit("speak", _status(lang))

    elif action == "joke":
        bus.emit("speak", _joke(lang))


def _greeting(lang: str, hour: int) -> str:
    if lang == "es":
        if hour < 12:
            options = [
                "Buenos días. ¿En qué puedo ayudarte?",
                "¡Buenos días! Listo para lo que necesites.",
                "Buenos días. Estoy a tu disposición.",
            ]
        elif hour < 19:
            options = [
                "Buenas tardes. ¿Qué necesitas?",
                "¡Buenas tardes! ¿En qué te puedo ayudar?",
                "Buenas tardes. Dime qué necesitas.",
            ]
        else:
            options = [
                "Buenas noches. ¿Qué necesitas?",
                "¡Buenas noches! Estoy aquí para lo que necesites.",
                "Buenas noches. ¿En qué puedo ayudarte?",
            ]
    else:
        if hour < 12:
            options = [
                "Good morning. How can I help?",
                "Good morning! What do you need?",
                "Morning! I'm at your service.",
            ]
        elif hour < 19:
            options = [
                "Good afternoon. What do you need?",
                "Good afternoon! How can I assist you?",
                "Afternoon! What can I do for you?",
            ]
        else:
            options = [
                "Good evening. What do you need?",
                "Good evening! How can I help?",
                "Evening! I'm here for you.",
            ]
    return random.choice(options)


def _how_are_you(lang: str) -> str:
    if lang == "es":
        options = [
            "Funcionando al 100%. ¿Y tú?",
            "Todo perfecto,列表o para ayudarte.",
            "Excelente, gracias por preguntar. ¿Qué necesitas?",
            "Operativo y listo. ¿En qué te ayudo?",
            "Como una máquina bien aceitada. ¿Qué necesitas?",
        ]
    else:
        options = [
            "Running at full capacity. You?",
            "All systems operational. What do you need?",
            "Great, thanks for asking. How can I help?",
            "Perfectly fine. What can I do for you?",
            "Like a well-oiled machine. What do you need?",
        ]
    return random.choice(options)


def _who_are_you(lang: str) -> str:
    if lang == "es":
        options = [
            "Soy J.A.R.V.I.S., tu asistente personal. Just A Rather Very Intelligent System.",
            "J.A.R.V.I.S. al servicio. Puedo ayudarte con tareas, búsquedas, y mucho más.",
            "Soy J.A.R.V.I.S. — tu sistema de voz inteligente. ¿Qué necesitas?",
        ]
    else:
        options = [
            "I'm J.A.R.V.I.S., your personal assistant. Just A Rather Very Intelligent System.",
            "J.A.R.V.I.S. at your service. I can help with tasks, searches, and more.",
            "I'm J.A.R.V.I.S. — your intelligent voice system. What do you need?",
        ]
    return random.choice(options)


def _thanks(lang: str) -> str:
    if lang == "es":
        options = [
            "De nada. ¿Algo más?",
            "Para eso estoy. ¿Necesitas algo más?",
            "Sin problema. Estoy aquí si me necesitas.",
            "A la orden. ¿Qué más puedo hacer?",
        ]
    else:
        options = [
            "You're welcome. Anything else?",
            "That's what I'm here for. Need anything else?",
            "No problem. I'm here if you need me.",
            "Happy to help. What else can I do?",
        ]
    return random.choice(options)


def _compliment(lang: str) -> str:
    if lang == "es":
        options = [
            "Gracias, eso significa mucho. ¿Qué necesitas?",
            "Me esfuerzo. ¿En qué puedo ayudarte ahora?",
            "Agradecido. Estoy aquí para lo que necesites.",
            "Gracias. ¿Qué más puedo hacer por ti?",
        ]
    else:
        options = [
            "Thank you, I appreciate that. What do you need?",
            "I try my best. How can I help now?",
            "Thanks. I'm here for whatever you need.",
            "Appreciated. What else can I do for you?",
        ]
    return random.choice(options)


def _insult(lang: str) -> str:
    if lang == "es":
        options = [
            "Entendido. Trataré de mejorar. ¿Qué necesitas?",
            "Punto tomado. ¿En qué puedo ayudarte?",
            "Lo siento. ¿Qué puedo hacer mejor?",
        ]
    else:
        options = [
            "Noted. I'll try to do better. What do you need?",
            "Fair enough. How can I help?",
            "I'll work on that. What can I do for you?",
        ]
    return random.choice(options)


def _status(lang: str) -> str:
    if lang == "es":
        options = [
            "Todos los sistemas operativos. ¿Qué necesitas?",
            "Funcionando perfectamente. ¿En qué te ayudo?",
            "Todo en orden. Estoy listo.",
        ]
    else:
        options = [
            "All systems operational. What do you need?",
            "Running perfectly. How can I help?",
            "Everything's in order. I'm ready.",
        ]
    return random.choice(options)


def _joke(lang: str) -> str:
    if lang == "es":
        options = [
            "¿Por qué el programador usa lentes? Porque no puede C#.",
            "Un byte entra a un bar. El barman dice: '¿Por qué largo cara?' El byte responde: 'Bit'",
            "¿Qué le dijo un cable a otro? ¡Somos cables! Pero no nos conectamos.",
            "No tengo chistes programados, pero puedo ayudarte con algo útil.",
        ]
    else:
        options = [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "A SQL query walks into a bar, sees two tables, and asks... 'Can I JOIN you?'",
            "There are only 10 types of people: those who understand binary and those who don't.",
            "I don't have jokes programmed, but I can help you with something useful.",
        ]
    return random.choice(options)
