import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("voiceClienteValen1")
client1.on_message = on_message

st.title("INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ - COCINA")
image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

# 
st.markdown("### Comandos disponibles:")
st.markdown("""
- 🌅 **"comienza la mañana"** → Enciende la luz
- 🌙 **"cierra la cocina"** → Apaga la luz  
- 🚪 **"pasa al comedor"** → Abre la puerta
- 🔒 **"cocina cerrada"** → Cierra la puerta
""")

st.write("Toca el botón y habla uno de los comandos")

stt_button = Button(label=" Inicio ", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'es-ES';

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)


comandos_validos = [
    "comienza la mañana",
    "cierra la cocina",
    "pasa al comedor",
    "cocina cerrada"
]

if result:
    if "GET_TEXT" in result:
        texto_recibido = result.get("GET_TEXT").strip().lower()
        st.write(f"Escuché: **{texto_recibido}**")

       
        if texto_recibido in comandos_validos:
            st.success(f"✅ Comando reconocido: '{texto_recibido}'")
            client1.on_publish = on_publish
            client1.connect(broker, port)
            message = json.dumps({"Act1": texto_recibido})
            ret = client1.publish("voicevalen", message)
        else:
            st.warning(f"⚠️ Comando no reconocido. Intenta con uno de los comandos de la lista.")

    try:
        os.mkdir("temp")
    except:
        pass
