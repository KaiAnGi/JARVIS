"""help plugin - Interactive help by category."""

from core.language import get_lang, resp


CATEGORIES_ES = {
    "hora": "Puedo decirte la hora y la fecha. Di: qué hora es, qué fecha hay hoy.",
    "calculadora": "Puedo hacer cálculos. Di: calcula cinco más tres.",
    "aplicaciones": "Puedo abrir apps. Di: abre notepad, abre chrome, abre el explorador.",
    "ventanas": "Puedo controlar ventanas. Di: minimizar, maximizar, cierra ventana.",
    "explorador de archivos": "Puedo abrir el explorador de archivos. Di: abre el explorador.",
    "navegador": "Puedo buscar en Google y YouTube. Di: busca recetas en Google, reproduce música en YouTube.",
    "pestañas": "Puedo controlar pestañas del navegador. Di: cierra pestaña, nueva pestaña, duplica pestaña.",
    "git": "Puedo ejecutar comandos git. Di: git status, git commit, git push, git pull.",
    "visual studio code": "Puedo abrir VS Code y proyectos. Di: abre visual studio code, abre proyecto.",
    "correos": "Puedo leer tus correos de Gmail. Di: cuántos correos, revisa correo, lee correo.",
    "calendario": "Puedo ver tus eventos. Di: qué hay en mi calendario, qué sigue.",
    "idioma": "Puedo cambiar el idioma. Di: cambiar idioma, habla español, habla inglés.",
    "historial": "Puedo consultar comandos pasados. Di: último comando, historial de comandos.",
    "salir": "Puedo cerrar la sesión. Di: adiós jarvis.",
}

CATEGORIES_EN = {
    "time": "I can tell you the time and date. Say: what time is it, what's the date.",
    "calculator": "I can do math. Say: calculate five plus three.",
    "apps": "I can open apps. Say: open notepad, open chrome, open explorer.",
    "windows": "I can control windows. Say: minimize, maximize, close window.",
    "file explorer": "I can open file explorer. Say: open explorer.",
    "browser": "I can search Google and YouTube. Say: search recipes on Google, play music on YouTube.",
    "tabs": "I can control browser tabs. Say: close tab, new tab, duplicate tab.",
    "git": "I can run git commands. Say: git status, git commit, git push, git pull.",
    "visual studio code": "I can open VS Code and projects. Say: open visual studio code, open project.",
    "email": "I can read your Gmail. Say: how many emails, check email, read email.",
    "calendar": "I can check your events. Say: what's on my calendar, what's next.",
    "language": "I can switch language. Say: switch language, speak Spanish, speak English.",
    "history": "I can check past commands. Say: last command, command history.",
    "exit": "I can end the session. Say: goodbye jarvis.",
}


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "help":
        categories = CATEGORIES_ES if get_lang() == "es" else CATEGORIES_EN
        category_list = ", ".join(categories.keys())
        bus.emit("speak", resp("help_list", categories=category_list))

    elif action == "help_category":
        categories = CATEGORIES_ES if get_lang() == "es" else CATEGORIES_EN
        text_lower = text.lower()
        
        for key, info in categories.items():
            if key in text_lower:
                bus.emit("speak", info)
                return
        
        bus.emit("speak", resp("help_not_found"))
