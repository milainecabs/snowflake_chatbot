import streamlit as st
from snowflake.snowpark.context import get_active_session
import uuid

# -------------------------------------------------
# INIT
# -------------------------------------------------
# -------------------------------------------------


from snowflake.snowpark import Session
import os
from dotenv import load_dotenv

def create_session():
    load_dotenv()

    connection_parameters = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    }

    return Session.builder.configs(connection_parameters).create()

session = create_session()

#session = get_active_session()

TABLE_NAME = "DB_LAB.CHAT_APP.CONVERSATIONS"

AVAILABLE_MODELS = {
    "Mistral Large (rapide)": "mistral-large",
    "Llama 3 70B (qualité)": "llama3-70b",
    "Mixtral (équilibré)": "mixtral-8x7b"
}

SYSTEM_PROMPT = "Tu es un assistant utile, clair et structuré."

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

# -------------------------------------------------
# BDD HELPERS
# -------------------------------------------------

def save_message(role, content):
    if role == "system":
        return
    query = f"""
    INSERT INTO {TABLE_NAME}
    VALUES (
        '{st.session_state.conversation_id}',
        CURRENT_TIMESTAMP(),
        '{role}',
        $$ {content} $$
    )
    """
    session.sql(query).collect()

def get_conversation_ids():
    try:
        rows = session.sql(f"""
            SELECT DISTINCT CONVERSATION_ID
            FROM {TABLE_NAME}
            ORDER BY CONVERSATION_ID
        """).collect()
        return [row["CONVERSATION_ID"] for row in rows]
    except:
        return []

def load_conversation(conv_id):
    rows = session.sql(f"""
        SELECT ROLE, CONTENT
        FROM {TABLE_NAME}
        WHERE CONVERSATION_ID = '{conv_id}'
        ORDER BY CREATED_AT
    """).collect()

    messages = []
    for row in rows:
        messages.append({"role": row["ROLE"].lower(), "content": row["CONTENT"]})

    st.session_state.messages = messages
    st.session_state.conversation_id = conv_id

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("⚙️ Paramètres IA")

model_label = st.sidebar.selectbox(
    "Choisir le modèle",
    list(AVAILABLE_MODELS.keys())
)
model = AVAILABLE_MODELS[model_label]

temperature = st.sidebar.slider(
    "Température (affichage uniquement)",
    0.0, 1.5, 0.7, step=0.1
)

if st.sidebar.button("🆕 Nouveau chat"):
    st.session_state.messages = []
    st.session_state.conversation_id = str(uuid.uuid4())
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🗂 Historique")

conversation_ids = get_conversation_ids()
if conversation_ids:
    selected_conv = st.sidebar.selectbox(
        "Revenir à une conversation",
        options=conversation_ids
    )
    if st.sidebar.button("📂 Charger cette conversation"):
        load_conversation(selected_conv)
        st.rerun()
else:
    st.sidebar.caption("Aucune conversation enregistrée.")

# -------------------------------------------------
# UI
# -------------------------------------------------

st.title("🤖 Chatbot Cortex Intelligent")
st.caption(
    f"Modèle actif : **{model_label}** | "
    f"Température (UI) : {temperature} | "
    f"Conversation : {st.session_state.conversation_id}"
)

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# PROMPT
# -------------------------------------------------

def build_prompt(user_input):
    history = ""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            history += f"Utilisateur: {msg['content']}\n"
        elif msg["role"] == "assistant":
            history += f"Assistant: {msg['content']}\n"

    prompt = f"""{SYSTEM_PROMPT}

Historique :
{history}

Nouvelle question :
{user_input}

Réponse :
"""
    return prompt

# -------------------------------------------------
# CORTEX CALL (2 arguments uniquement)
# -------------------------------------------------

def call_cortex(prompt, model):
    query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        '{model}',
        $$ {prompt} $$
    ) AS RESPONSE
    """
    result = session.sql(query).collect()
    response = result[0]["RESPONSE"]
    return str(response).strip()

# -------------------------------------------------
# CHAT INPUT
# -------------------------------------------------

user_input = st.chat_input("Pose ta question...")

if user_input:

    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message("user", user_input)

    prompt = build_prompt(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Réflexion..."):
            response = call_cortex(prompt, model)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_message("assistant", response)
