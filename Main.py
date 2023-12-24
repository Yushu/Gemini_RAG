import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
from PIL import Image
import requests

st.set_page_config(
    page_title="Google Gemini RAG Chatbot",
    page_icon="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png",
    layout="wide",
)
# Path: Main.py
#Author: Ayush Srivastava
#------------------------------------------------------------
#HEADER
st.markdown('''
Powered by Google Gemini <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20">
, Streamlit and Python''', unsafe_allow_html=True)
#st.caption("By Ayush Srivastava")

#------------------------------------------------------------
#LANGUAGE
langcols = st.columns([0.2,0.8])
with langcols[0]:
  lang = st.selectbox('Select your language',
  ('English', 'Español', 'Français', 'Deutsch',
  'Italiano', 'Português', 'Polski', 'Nederlands',
  'Русский', '日本語', '한국어', '中文', 'العربية',
  'हिन्दी', 'Türkçe', 'Tiếng Việt', 'Bahasa Indonesia',
  'ภาษาไทย', 'Română', 'Ελληνικά', 'Magyar', 'Čeština',
  'Svenska', 'Norsk', 'Suomi', 'Dansk', 'हिन्दी', 'हिन्�'),index=0)

if 'lang' not in st.session_state:
    st.session_state.lang = lang
st.divider()

#------------------------------------------------------------
#FUNCTIONS
def extract_graphviz_info(text: str) -> list[str]:
  """
  The function `extract_graphviz_info` takes in a text and returns a list of graphviz code blocks found in the text.

  :param text: The `text` parameter is a string that contains the text from which you want to extract Graphviz information
  :return: a list of strings that contain either the word "graph" or "digraph". These strings are extracted from the input
  text.
  """

  graphviz_info  = text.split('```')

  return [graph for graph in graphviz_info if ('graph' in graph or 'digraph' in graph) and ('{' in graph and '}' in graph)]

def append_message(message: dict) -> None:
    """
    The function appends a message to a chat session.

    :param message: The `message` parameter is a dictionary that represents a chat message. It typically contains
    information such as the user who sent the message and the content of the message
    :type message: dict
    :return: The function is not returning anything.
    """
    st.session_state.chat_session.append({'user': message})
    return

@st.cache_resource
def load_model() -> genai.GenerativeModel:
    """
    The function `load_model()` returns an instance of the `genai.GenerativeModel` class initialized with the model name
    'gemini-pro'.
    :return: an instance of the `genai.GenerativeModel` class.
    """
    model = genai.GenerativeModel('gemini-pro')
    return model

@st.cache_resource
def load_modelvision() -> genai.GenerativeModel:
    """
    The function `load_modelvision` loads a generative model for vision tasks using the `gemini-pro-vision` model.
    :return: an instance of the `genai.GenerativeModel` class.
    """
    model = genai.GenerativeModel('gemini-pro-vision')
    return model



#------------------------------------------------------------
#CONFIGURATION
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = load_model()

vision = load_modelvision()

if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = []

#st.session_state.chat_session

#------------------------------------------------------------
#CHAT

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'welcome' not in st.session_state or lang != st.session_state.lang:
    st.session_state.lang = lang
    welcome  = model.generate_content(f'''
    Het begroet de gebruiker en stelt voor wat hij/zij kan doen.
    (Je kunt afbeeldingen beschrijven, vragen beantwoorden, tekstbestanden en tabellen lezen).
    je bent een chatbot in een chatapplicatie gemaakt in streamlit en python. generate the answer in {lang}''')
    welcome.resolve()
    st.session_state.welcome = welcome

    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)
else:
    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)

if len(st.session_state.chat_session) > 0:
    count = 0
    for message in st.session_state.chat_session:

        if message['user']['role'] == 'model':
            with st.chat_message('ai'):
                st.write(message['user']['parts'])
                graphs = extract_graphviz_info(message['user']['parts'])
                if len(graphs) > 0:
                    for graph in graphs:
                        st.graphviz_chart(graph,use_container_width=False)
                        if lang == 'Español':
                          view = "Ver texto"
                        else:
                          view = "View text"
                        with st.expander(view):
                          st.code(graph, language='dot')
        else:
            with st.chat_message('user'):
                st.write(message['user']['parts'][0])
                if len(message['user']['parts']) > 1:
                    st.image(message['user']['parts'][1], width=200)
        count += 1



#st.session_state.chat.history

cols=st.columns(4)

with cols[0]:
    if lang == 'Nederlands':
      image_atachment = st.toggle("Afbeelding bijvoegen", value=False, help="Activeer deze modus om een afbeelding bij te voegen en laat de chatbot deze lezen")
    else:
      image_atachment = st.toggle("Attach image", value=False, help="Activate this mode to attach an image and let the chatbot read it")

with cols[1]:
    if lang == 'Nederlands':
      txt_atachment = st.toggle("Tekstbestand bijvoegen", value=False, help="Activeer deze modus om een tekstbestand bij te voegen en laat de chatbot het lezen")
    else:
      txt_atachment = st.toggle("Attach text file", value=False, help="Activate this mode to attach a text file and let the chatbot read it")
with cols[2]:
    if lang == 'Nederlands':
      csv_excel_atachment = st.toggle("CSV of Excel bijvoegen", value=False, help="Activeer deze modus om een CSV- of Excel-bestand bij te voegen en laat de chatbot het lezen")
    else:
      csv_excel_atachment = st.toggle("Attach CSV or Excel", value=False, help="Activate this mode to attach a CSV or Excel file and let the chatbot read it")
if image_atachment:
    if lang == 'Nederlands':
      image = st.file_uploader("Upload je afbeelding", type=['png', 'jpg', 'jpeg'])
      url = st.text_input("Of plak je afbeeldings url")
    else:
      image = st.file_uploader("Upload your image", type=['png', 'jpg', 'jpeg'])
      url = st.text_input("Or paste your image url")
else:
    image = None
    url = ''



if txt_atachment:
    if lang == 'Nederlands':
      txtattachment = st.file_uploader("Upload uw tekstbestand", type=['txt'])
    else:
      txtattachment = st.file_uploader("Upload your text file", type=['txt'])
else:
    txtattachment = None

if csv_excel_atachment:
    if lang == 'Nederlands':
      csvexcelattachment = st.file_uploader("CSV- of Excel-bestand uploaden", type=['csv', 'xlsx'])
    else:
      csvexcelattachment = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx'])
else:
    csvexcelattachment = None
if lang == 'Nederlands':
  prompt = st.chat_input("Schrijf je bericht")
else:
  prompt = st.chat_input("Write your message")

if prompt:
    txt = ''
    if txtattachment:
        txt = txtattachment.getvalue().decode("utf-8")
        if lang == 'Nederlands':
          txt = '   Tekst bestand:: \n' + txt
        else:
          txt = '   Text file: \n' + txt

    if csvexcelattachment:
        try:
            df = pd.read_csv(csvexcelattachment)
        except:
            df = pd.read_excel(csvexcelattachment)
        txt += '   Dataframe: \n' + str(df)

    if len(txt) > 5000:
        txt = txt[:5000] + '...'
    if image or url != '':
        if url != '':
            img = Image.open(requests.get(url, stream=True).raw)
        else:
            img = Image.open(image)
        prmt  = {'role': 'user', 'parts':[prompt+txt, img]}
    else:
        prmt  = {'role': 'user', 'parts':[prompt+txt]}

    append_message(prmt)

    if lang == 'Nederlands':
      spinertxt = 'Wacht even, ik denk...'
    else:
      spinertxt = 'Please wait a moment, I am thinking...'
    with st.spinner(spinertxt):
        if len(prmt['parts']) > 1:
            response = vision.generate_content(prmt['parts'],stream=True,safety_settings=[
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
    ]
)
            response.resolve()
        else:
            response = st.session_state.chat.send_message(prmt['parts'][0])

        try:
          append_message({'role': 'model', 'parts':response.text})
        except Exception as e:
          append_message({'role': 'model', 'parts':f'{type(e).__name__}: {e}'})


        st.rerun()

#st.session_state.chat_session
