from flask import Flask, request, jsonify
import random
import re
import difflib
from spellchecker import SpellChecker

app = Flask(__name__)

# Memoria de conversación por usuario (usando un diccionario temporal)
user_memory = {}
enlace_apps = 'https://perfil-mt65.onrender.com'

correct_words = [

    "app", "aplicación", "descargar", "instalar", "obtener",
    "enlace", "link", "yape", "bcp", "data", "precio", "plan", "planes", "comprar", "cuánto",
    "iniciar", "sesión", "necesito", "hola", "buen día", "buenas", "como estas", "notificación",
    "notificaciones", "código", "llegó", "qué", "cuáles",

]


def remove_extra_characters(word):
    """Eliminar caracteres repetidos innecesarios en palabras clave"""
    return re.sub(r'(.)\1+', r'\1', word)


def autocorrect1(message):
    spell = SpellChecker(language='es')  # Usamos el diccionario en español
    words = message.split()
    corrected_message = []

    # Correcciones específicas y comunes
    corrections = {
        "por que": "por qué",
        "llaga": "llega",
        "codigooo": "código",
        "codigo": "código",
        "llama": "llega",
    }

    for word in words:
        # Primero, elimina caracteres repetidos en las palabras clave
        word = remove_extra_characters(word)

        # Si la palabra está en el diccionario de correcciones, usa la corrección
        if word.lower() in corrections:
            corrected_message.append(corrections[word.lower()])
        else:
            corrected_message.append(spell.correction(
                word) if spell.correction(word) else word)

    return ' '.join(corrected_message)


def autocorrect(message):
    words = message.split()
    corrected_message = []

    for word in words:
        # Buscar la palabra más cercana en la lista de palabras clave
        closest_matches = difflib.get_close_matches(
            word, correct_words, n=1, cutoff=0.8)  # cutoff ajusta la sensibilidad
        if closest_matches:
            # Reemplaza con la palabra más cercana
            corrected_message.append(closest_matches[0])
        else:
            # Deja la palabra tal cual si no hay coincidencias cercanas
            corrected_message.append(word)

    return "".join(autocorrectTilde(" ".join(corrected_message)))


tilde_corrections = {
    "que": "qué",
    "como": "cómo",
    "donde": "dónde",
    "cuando": "cuándo",
    "quien": "quién",
    "cual": "cuál",
    "cual": "cuál",
    "cuales": "cuáles",
    "por que": "por qué",
    "por que no": "por qué no",
    "para que": "para qué",
    "aun": "aún",
    "este": "éste",
    "esta": "ésta"
}


def autocorrectTilde(message):
    # Convertir todo el mensaje a minúsculas para que las comparaciones no dependan del caso
    corrected_message = message.lower()

    # Reemplazar las palabras sin tilde por las correctas
    for word, correct_word in tilde_corrections.items():
        corrected_message = re.sub(
            r'\b' + word + r'\b', correct_word, corrected_message)

    return corrected_message


def get_response(user_id, message):
    global user_memory
    # Respuestas para descargar aplicaciones
    app_responses = [
        "¡Claro! Aquí tienes el enlace para {app}. Recuerda que solo está disponible para Android: {enlace_apps}. ¡Espero que disfrutes de la app!",
        "Aquí está el enlace para descargar {app}. Solo es compatible con Android: {enlace_apps}. ¡Que lo disfrutes!",
        "Te dejo el enlace para descargar {app}. Recuerda que esta aplicación solo está disponible para Android: {enlace_apps}. ¡Espero que te guste!",
        "¡Por supuesto! Aquí tienes el enlace para {app}, solo para Android: {enlace_apps}. ¡Disfrútala!",
        "Aquí tienes el enlace para descargar {app}. Ten en cuenta que solo está disponible para Android: {enlace_apps}. ¡Ojalá la disfrutes!",
        "Aquí está el enlace para {app}, solo para Android: {enlace_apps}. ¡Espero que te guste mucho!",
        "¡Aquí tienes el enlace para descargar {app}! Solo para Android: {enlace_apps}. ¡Espero que te guste y disfrutes usándola!",
        "¡Con gusto! Puedes descargar {app} desde este enlace, solo para Android: {enlace_apps}. ¡Espero que la disfrutes mucho!",
        "¡Aquí tienes el enlace para descargar {app}, solo para Android! {enlace_apps}. ¡Espero que te guste y disfrutes usándola!"
    ]

    # Respuestas relacionadas con precios o planes
    price_responses = [
        "Dentro de la aplicación podrás ver los precios de los planes. Si deseas comprar alguno, simplemente haz clic en la opción de compra.",
        "Puedes revisar los planes y precios dentro de la aplicación. Si te interesa alguno, solo dale clic en comprar.",
        "Dentro de la app están los precios y si deseas adquirir algún plan, solo selecciona la opción de comprar.",
        "Para ver los precios y planes, solo entra a la aplicación y podrás comprar lo que necesites desde ahí.",
        "Dentro de la app encontrarás los precios y si decides comprar alguno, solo toca en la opción de compra."
    ]

    registration_responses = [
        "Para registrarte correctamente, necesitas completar el formulario dentro de la aplicación. Asegúrate de ingresar un correo electrónico y número telefónico reales, ya que ahí recibirás el código de verificación.",
        "El proceso de registro requiere que llenes el formulario en la app con datos válidos. Es importante que el correo y el número de teléfono sean reales, ya que el código de verificación llegará a ellos.",
        "Para registrarte, llena el formulario dentro de la aplicación. Recuerda que el correo y el número de teléfono deben ser correctos. El número telefónico debe tener una cuenta activa de WhatsApp, ya que allí recibirás el código de verificación.",
        "Debes completar el registro en la aplicación ingresando tu correo electrónico y número de teléfono. Ambos deben ser reales porque ahí recibirás el código de verificación, y el número debe estar vinculado a WhatsApp.",
        "Para registrarte de forma correcta, llena el formulario en la app. Es crucial que el correo y el número telefónico que proporciones sean reales, ya que el código de verificación se enviará por correo o WhatsApp.",
        "El registro en la aplicación se realiza completando un formulario con tus datos. Asegúrate de que el número de teléfono esté asociado a WhatsApp y de que el correo electrónico sea válido para recibir el código de verificación.",
        "Para registrarte, simplemente completa el formulario dentro de la app con un correo válido y un número telefónico real que tenga WhatsApp. El código de verificación llegará a uno de estos medios.",
        "El registro es sencillo: llena el formulario en la app y proporciona un correo electrónico y un número de teléfono reales. El número debe tener una cuenta activa de WhatsApp para recibir el código de verificación.",
        "Regístrate en la app completando el formulario. Es importante que el correo electrónico y el número de teléfono que ingreses sean correctos, ya que el código de verificación se enviará a esos datos.",
        "Para registrarte correctamente, asegúrate de ingresar un correo electrónico válido y un número de teléfono con WhatsApp al completar el formulario en la aplicación. El código de verificación se enviará a uno de ellos."
    ]

    problem_responses = [
        "Parece que has tenido un problema. ¿Podrías indicarnos tu correo electrónico y, si es posible, enviarnos una captura de pantalla del error para poder ayudarte mejor?",
        "Lo siento por los inconvenientes. Para poder ayudarte de forma más eficiente, ¿podrías compartir tu correo electrónico y las capturas de pantalla del error que estás viendo?",
        "Parece que algo no salió bien. Si tienes problemas, ¿puedes darnos tu correo electrónico y enviar una captura de pantalla del error para poder resolverlo rápidamente?",
        "Veo que hubo un problema. Para poder ayudarte mejor, ¿puedes enviarnos tu correo electrónico y capturas de pantalla del error?",
        "Lamentamos que estés teniendo problemas. Por favor, comparte tu correo electrónico y las capturas de pantalla del error para que podamos resolverlo cuanto antes."
    ]

    sms_availability_responses = [
        "Entiendo, solo tenemos notificaciones por SMS, pero por el momento no están disponibles. Te avisaremos cuando estén disponibles nuevamente.",
        "Solo ofrecemos notificaciones por SMS, pero en este momento no están disponibles. Te informaremos cuando vuelvan a estar disponibles.",
        "En este momento, las notificaciones por SMS no están disponibles. Te avisaremos cuando puedan ser activadas nuevamente.",
        "Actualmente, las notificaciones por SMS no están disponibles, pero te notificaremos cuando vuelvan a estar activas.",
        "Solo tenemos notificaciones por SMS, pero por ahora no están disponibles. Te mantendremos informado cuando estén disponibles nuevamente."
    ]

    whatsapp_verification_responses = [
        "El código de verificación fue enviado a tu cuenta de WhatsApp. Si no lo has recibido, por favor revisa allí. Si colocaste mal el número, escribe *cambiar num* para actualizarlo.",
        "Revisa tu cuenta de WhatsApp, ya que el código de verificación fue enviado allí. Si el número es incorrecto, puedes escribir *cambiar num* para modificarlo.",
        "El código de verificación se envió a tu WhatsApp. Si no lo encuentras, revisa tus mensajes. Si el número es incorrecto, escribe *cambiar num* para corregirlo.",
        "Por favor, revisa tu WhatsApp ya que allí se envió el código de verificación. Si cometiste un error al ingresar el número, escribe *cambiar num* para actualizarlo.",
        "El código de verificación se ha enviado a tu WhatsApp. Si no lo recibes, revisa los mensajes en esa cuenta. Si el número es incorrecto, escribe *cambiar num* para actualizarlo."
    ]

    # Saludos iniciales variados
    greetings = [
        "¡Hola! ¿Cómo te va hoy?",
        "¡Buenas! ¿En qué puedo ayudarte?",
        "¡Qué tal! ¿Cómo te encuentras?",
    ]

    # Función para detectar si el mensaje está relacionado con obtener una app
    def is_app_related(message):
        # Definir expresiones regulares para detectar la intención
        corrected_message = autocorrect(message)
        patterns = [
            r"(descargar|instalar|conseguir|obtener|pasar|compartir|enlace|link|bajar|instalación).*(app|aplicación|programa|software)",
            r"cómo.*?(descargo|descargar|instalo|instalar|puedo obtener|puedo conseguir).*(app|aplicación|programa|software)",
            r"(necesito|quiero|busco|requiero|me gustaría|estoy buscando).*(app|aplicación|programa|software)",
            r"(me puedes|podrías|pueden|me podrías).*(dar|enviar|pasar|proporcionar|compartir|mandar).*?(el|un|algún).*?(enlace|link|app|aplicación|programa)",
            r"(dónde|donde|en dónde|por dónde).*?(descargar|encontrar|obtener|comprar|conseguir).*?(app|aplicación|programa|software)",
            r"(qué|cuál|cuáles).*(app|aplicaciones|programas|software).*?(tienes|hay disponibles|recomiendas|existen)",
            r"(quiero|voy a|planeo).*?(descargar|obtener|instalar|usar|bajar).*?(app|aplicación|programa)",
            r"necesito.*?(información|detalles|ayuda).*?(app|aplicación|programa|software)",
            r"(me interesa|quisiera|quiero saber|dime sobre|háblame de).*?(app|aplicación|programa|software)",
            r"existe.*?(alguna|una|otra).*?(app|aplicación|programa).*?(parecida|similar|alternativa|recomendada)",
            r"(puedo|cómo puedo).*?(descargar|obtener|usar|instalar|conseguir).*?(app|aplicación|programa|software)",
            r"(qué app|cuál app).*?(debo|puedo|me recomiendas).*?(usar|descargar|instalar|conseguir|buscar)",
            r"(estoy buscando|necesito encontrar|me urge).*?(app|aplicación|programa|software).*?(específica|similar)",
            r"(puedes|podrías|me ayudas a|ayúdame a).*?(descargar|instalar|encontrar|usar).*?(app|aplicación|programa)",
            r"(cómo funciona|qué hace|cómo se usa).*?(app|aplicación|programa|software)",
            r"(cuál es|cuáles son).*?(la mejor|las mejores).*?(app|aplicaciones|programas|software).*?(para|de).*?(uso específico)",
            r"me.*?(recomiendas|puedes sugerir|puedes hablar).*?(app|aplicación|programa).*?(para|de).*?(uso específico)",
            r"(tienes|hay).*?(enlace|link|acceso).*?(para|a).*?(descargar|instalar|obtener).*?(app|aplicación)",
            r"alguna app.*?(que sirva|para|de).*?(uso específico)",
        ]

        # Iterar sobre cada patrón y verificar si hay coincidencia
        for pattern in patterns:
            if re.search(pattern, corrected_message.lower()):
                return True

        # Si no se encuentra ninguna coincidencia
        return False

    # Función para detectar preguntas sobre precios y planes
    def is_price_related(message):
        # Definir patrones relacionados con precios y compras
        corrected_message = autocorrect(message)
        print('1', corrected_message)
        price_patterns = [
            # Menciones directas de precio o costo
            r"(cuánto|precio|planes|comprar|costar|valor|tarifa|costo|pagar).*?(plan|servicio|producto|crédito|membresía|suscripción)",
            r"(cuáles|qué|dónde).*?(planes|opciones|servicios|productos|suscripciones).*?(disponibles|ofrecen|tienen)?",
            r"(qué|cuánto|cuáles).*?(precio|tarifa|costo|valor|planes).*?(tiene|hay|es|son)?",
            r"(quiero|necesito|me gustaría|busco|estoy buscando).*?(comprar|adquirir|obtener|contratar|información).*?(plan|producto|servicio|suscripción|crédito|opción|paquete|oferta)",
            r"(cómo|dónde).*?(pago|pagar|comprar|adquirir|contratar).*?(plan|servicio|producto|crédito|membresía|suscripción)",
            r"necesito.*?(información|detalles).*?(planes|plan|precios|tarifas|costos|opciones)",
            r"necesito.*(planes|plan|precios|tarifas|costos)",
            r"existe.*?(algún|un|una).*?(plan|opción).*?(económico|barato|accesible)",
            r"me.*?(puedes|podrías|pueden).*?(informar|decir|dar|explicar).*?(precios|planes|tarifas|suscripciones)",
            r"cuáles.*?(son|están).*?(las|los).*?(opciones|planes|precios|tarifas|suscripciones).*?(disponibles|vigentes)?",
            r"(tienen|hay).*?(ofertas|descuento|promociones).*?(en planes|en suscripciones|disponibles)?",
            r"(quiero|voy a|planeo).*?(pagar|comprar|contratar|activar).*?(plan|servicio|suscripción|membresía|cuenta|yape|bcp|crédito|créditos)",
            r"(planes|precios|tarifas|opciones).*?(económicos|asequibles|accesibles|baratos)",
            r"(el|los|la|las).*?(precio|costo|valor|planes).*?(actual|disponible|vigente)",
            r"(suscripción|membresía).*?(mensual|anual|costo|valor|precio|tarifa)",
        ]

        # Iterar sobre cada patrón y verificar si hay coincidencia
        for pattern in price_patterns:
            if re.search(pattern, corrected_message.lower()):
                return True

        return False

    def is_notification_related(message):
        # Corregir el mensaje (si es necesario)
        corrected_message = autocorrect(message)

        # Patrones relacionados con notificaciones
        notification_patterns = [
            # Preguntas generales sobre notificaciones
            r"(tiene|enviar|recibir).*?(notificación|notificaciones)",
            r"(me|pueden|puedo).*?(activar|recibir).*?(notificaciones)",
            r"(cómo|qué).*?(configurar|activar|desactivar).*?(notificaciones)",
            r"(recibo|me llegan|tengo).*?(notificaciones)",
            r"(tienen).*?(notificaciones).*?(sms|push|por correo|de alerta)?",
            r"(puedo|es posible).*?(activar|desactivar).*?(notificaciones|sms)",
            r"(hay|existe).*?(opción|configuración).*?(para|de).*?(notificaciones)",
            r"(cuáles|cómo|dónde).*?(notificaciones).*?(recibir|enviar)?",
            r"(son|sonora|llegan).*?(notificaciones).*?(sms|push|email|alertas)?",
            r"(es|existe).*?(notificación).*?(sms|de alertas|por correo)?",
            r"(es|están).*?(activadas|configuradas).*?(las|las).*?(notificaciones)?",
            r"(recibo).*?(notificaciones).*?(en|por|a través).*?(sms|correo|push)?"
        ]

        # Iterar sobre cada patrón y verificar si hay coincidencia
        for pattern in notification_patterns:
            if re.search(pattern, corrected_message.lower()):
                return True

        return False

    def is_account_issue_related(message):
        corrected_message = autocorrect(message)

        account_issue_patterns = [
            r"(no puedo|no me deja|me da error|tengo problemas).*?(crear|registrar|acceder|entrar|iniciar sesión).*?(cuenta|perfil|app|aplicación)",
            r"(me sale|me aparece|error|problema).*?(al).*?(crear|registrar|entrar|acceder).*?(cuenta|perfil|app|aplicación)",
            r"(no logro|no puedo|me da error).*?(iniciar sesión|entrar|acceder).*?(en|a).*?(mi cuenta|perfil|app)",
            r"(tengo problemas|me sale error).*?(al).*?(ingresar|entrar|acceder|iniciar sesión).*?(cuenta|perfil|app|aplicación)",
        ]

        return any(re.search(pattern, corrected_message.lower()) for pattern in account_issue_patterns)

    def is_registration_related(message):
        # Definir patrones relacionados con el registro o inicio de sesión
        corrected_message = autocorrect(message)

        registration_patterns = [
            r"(necesito|debo|es obligatorio).*?(registrarme|crear una cuenta|registrar una cuenta|inscribirme).*?(para usar|para acceder|para descargar|en la aplicación)?",
            r"(cómo|dónde|qué).*?(registrarme|crear una cuenta|hacer un registro|registrar una cuenta).*?",
            r"(es necesario|hay que).*?(crear una cuenta|registrarme|tener una cuenta|registrarse).*?",
            r"(puedo|es posible).*?(usar|acceder|descargar).*?(sin registrarme|sin una cuenta|sin registro).*?",
            r"(cómo|cuál es el proceso|qué pasos).*?(para registrarme|para crear una cuenta|para registrarse).*?",
            r"(requiere|requiere la aplicación).*?(registro|registrarme|una cuenta|crear una cuenta).*?(para usarla|para acceder)?",
            r"(tengo|necesito).*?(crear|tener|hacer).*?(una cuenta|un registro).*?(para usar la aplicación)?",
            r"(puedo|es posible).*?(registrarme|crear una cuenta).*?(con correo electrónico|con Google|con redes sociales|con Facebook)?",
            r"(cuáles|qué métodos).*?(de registro|de creación de cuenta).*?(ofrecen|están disponibles)?",
            r"(cómo|qué debo).*?(hacer|proceso).*?(para registrarme|para iniciar sesión|para crear una cuenta).*?",
            r"(el registro).*?(es gratuito|tiene costo|es rápido|es seguro|es obligatorio).*?",
            r"(puedo usar).*?(la aplicación).*?(sin registro|sin registrarme|sin crear cuenta)?",
            r"(hay|existe).*?(un proceso fácil|un registro rápido|una opción para registrarme rápidamente).*?",
            r"(puedo cambiar).*?(mis datos de registro|mi correo|mi información personal|mi cuenta).*?",
            r"(qué información|qué datos).*?(son necesarios|se solicitan).*?(para registrarme|en el registro)?",
        ]

        # Iterar sobre cada patrón y verificar si hay coincidencia
        for pattern in registration_patterns:
            if re.search(pattern, corrected_message.lower()):
                return True

        return False

    def is_verification_code_related(message):
        # Definir patrones relacionados con códigos de verificación
        corrected_message = autocorrect1(message)
        print(corrected_message)

        verification_code_patterns = [
            r"(no|nunca|no me|no me llegó).*?(código de verificación|código|código de activación|código de confirmación).*?(\?)?",
            r"(por qué|cómo).*?(no|nunca).*?(recibí|llegó|llegué).*?(el código|el código de verificación).*?(\?)?",
            r"(no|nunca).*?(llegó|recibí|me llegó).*?(mi código|el código de verificación|el código de activación).*?(\?)?",
            r"(dónde|cómo).*?(recibir|obtener|conseguir).*?(el código de verificación|el código).*?(\?)?",
            r"(cuál|qué).*?(es el motivo|puede ser).*?(que no haya llegado).*?(mi código|el código de verificación).*?(\?)?",
            r"(necesito|quiero).*?(mi código|código de verificación).*?(\?)?",
            r"(qué pasa|por qué).*?(no llegó).*?(el código|el código de verificación).*?(\?)?",
            r"(mano|bro|te escribo|te hablo).*?(porque|porque no).*?(me llegó).*?(el código|código de verificación).*?(\?)?",
            r"¿(cómo|por qué).*?(no|no me|me).*?(llegó).*?(el código|código de verificación).*?(\?)?",
        ]

        # Iterar sobre cada patrón y verificar si hay coincidencia
        for pattern in verification_code_patterns:
            if re.search(pattern, corrected_message.lower()):
                return True

        return False

    # Verificar si es la primera interacción del usuario
    if user_id not in user_memory:
        user_memory[user_id] = {"has_interacted": False,
                                "requested_app": False, "app_requested": None}

        # Si el mensaje está relacionado con precios o planes
    if is_price_related(message):
        return random.choice(price_responses)
    # Si el usuario ya ha solicitado una app, y no se menciona otra, dar la respuesta correspondiente
    if user_memory[user_id]["app_requested"] is not None and message.lower() in ["yape", "bcp", "data"]:
        return random.choice(app_responses).format(app=user_memory[user_id]["app_requested"], enlace_apps=enlace_apps)

    # Verificar si el mensaje está relacionado con descargar la app
    if is_app_related(message):
        user_memory[user_id]["requested_app"] = True
        return random.choice([
            "¿Qué aplicación deseas descargar? Tengo Yape, BCP y Data.",
            "¿Qué app te gustaría descargar? Tengo Yape, BCP y Data.",
            "¿Te gustaría descargar alguna aplicación? Puedo ayudarte con Yape, BCP o Data."
        ])

    if is_registration_related(message):
        return random.choice(registration_responses)

    if is_account_issue_related(message):
        return random.choice(problem_responses)

    if is_notification_related(message):
        return random.choice(sms_availability_responses)

    if is_verification_code_related(message):
        return random.choice(whatsapp_verification_responses)

    # Si el usuario menciona una app específica
    if user_memory[user_id]["requested_app"]:
        corrected_message = autocorrect(message).lower()
        if "yape" in corrected_message:
            user_memory[user_id]["app_requested"] = "yape"
            return random.choice(app_responses).format(app=user_memory[user_id]["app_requested"], enlace_apps=enlace_apps)
        elif "bcp" in corrected_message:
            user_memory[user_id]["app_requested"] = "bcp"
            return random.choice(app_responses).format(app=user_memory[user_id]["app_requested"], enlace_apps=enlace_apps)
        elif "data" in corrected_message:
            user_memory[user_id]["app_requested"] = "data"
            return random.choice(app_responses).format(app=user_memory[user_id]["app_requested"], enlace_apps=enlace_apps)

    # Si es la primera interacción, saluda al usuario
    if not user_memory[user_id]["has_interacted"]:
        user_memory[user_id]["has_interacted"] = True
        corrected_message = autocorrect(message).lower()
        if "hola" in corrected_message or "buenas" in corrected_message or "como estas" in corrected_message:
            return random.choice(greetings)

    # Respuesta por defecto para otras preguntas
    default_responses = [
        "Lo siento, no entiendo tu pregunta. ¿Podrías darme más detalles?",
        "No estoy seguro de haber entendido. ¿Puedes explicarlo un poco más?",
        "Mmm, no estoy seguro de qué necesitas. ¿Puedes darme más contexto?"
    ]
    return random.choice(default_responses)


default_responses = [
    "Lo siento, no entiendo tu pregunta. ¿Podrías darme más detalles?",
    "No estoy seguro de haber entendido. ¿Puedes explicarlo un poco más?",
    "Mmm, no estoy seguro de qué necesitas. ¿Puedes darme más contexto?"
]


def obtener_respuesta_default():
    return random.choice(default_responses)

@app.route("/consultar", methods=["POST"])
def main():
   data = request.json
   usuario = data.get("usuario", "")  # Obtener el identificador del usuario
   pregunta = data.get("pregunta", "")
   if not pregunta:
       respuesta = obtener_respuesta_default()
   else:
       respuesta = get_response(usuario, pregunta)
   return jsonify({"respuesta": respuesta})
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000)
   
   
@app.route("/", methods=["GET"])
def hello_world():
    return "Hola desde Flask en Render"
#def main():
#    print("Bienvenido al chatbot. Escribe 'salir' para terminar la conversación.")
#    user_id = "usuario_terminal"
#
#    while True:
#        message = input("Tú: ")
#        if message.lower() == "salir":
#            print("Chatbot: Hasta luego. ¡Que tengas un buen día!")
#            break
#
#        response = get_response(user_id, message)
#        print(f"Chatbot: {response}")
#
#
#if __name__ == "__main__":
#    main()
