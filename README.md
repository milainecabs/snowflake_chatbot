# Chatbot Snowflake Cortex

## Description du projet  
Ce projet implémente un **chatbot intelligent** utilisant **Snowflake Cortex**, intégré dans une application **Streamlit**.  
Le chatbot permet :

- d’envoyer des prompts à un modèle LLM hébergé dans Snowflake,  
- de sélectionner dynamiquement le modèle Cortex,  
- de gérer un historique de conversation stocké dans Snowflake,  
- d’interagir via une interface Streamlit simple et intuitive.

Ce projet a été développé dans le cadre du laboratoire *“Build Your Own Chatbot with Snowflake Cortex”* .

---

## Architecture technique

### **1. Interface utilisateur**
- Application **Streamlit**
- Entrée utilisateur via `st.chat_input`
- Affichage des messages sous forme de chat

### **2. Backend**
- Connexion Snowflake via **Snowpark**
- Appels LLM via :
  ```sql
  SELECT SNOWFLAKE.CORTEX.COMPLETE(model, prompt)
  ```

### **3. Stockage**
- Table Snowflake :  
  ```
  DB_LAB.CHAT_APP.CONVERSATIONS
  ```
- Colonnes :
  - `CONVERSATION_ID`
  - `CREATED_AT`
  - `ROLE`
  - `CONTENT`

### **4. Historique**
- Chaque message est inséré dans la table
- Possibilité de recharger une conversation existante
- Historique injecté dans le prompt pour contextualiser les réponses

### **5. Exécution**
- Fonctionne :
  - dans **Streamlit‑in‑Snowflake**  
  - en **local** via Snowpark + fichier `.env`

---

## Intégration avec Snowflake Cortex

Le chatbot utilise la fonction Cortex :

```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE('<model>', $$ <prompt> $$)
```

Caractéristiques :

- Appel **à 2 paramètres** (modèles Cortex sans paramètres avancés)
- Prompt enrichi avec :
  - un *system prompt*
  - l’historique utilisateur
  - la nouvelle question

---

## Choix du modèle

Les modèles disponibles dans l’interface :

- **mistral-large** — rapide et polyvalent  
- **llama3-70b** — haute qualité  
- **mixtral-8x7b** — équilibré  

L’utilisateur sélectionne le modèle dans la sidebar Streamlit.

---

## Gestion de l’historique

- Chaque message (user/assistant) est stocké dans Snowflake.
- L’historique est reconstruit à chaque requête.
- Possibilité de :
  - créer une nouvelle conversation  
  - recharger une conversation existante  
  - afficher l’historique dans l’UI  

---

## Instructions d’exécution

### **1. Cloner le repository**
```bash
git clone https://github.com/milainecabs/snowflake_chatbot.git
cd snowflake_chatbot
```

### **2. Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### **3. Installer les dépendances**
```bash
pip install -r requirements.txt
```

### **4. Créer un fichier `.env`**
```
SNOWFLAKE_ACCOUNT="account_snowflake"
SNOWFLAKE_USER=<ton_user>
SNOWFLAKE_PASSWORD=<ton_password>
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=DB_LAB
SNOWFLAKE_SCHEMA=CHAT_APP
```

### **5. Lancer l’application**
```bash
streamlit run streamlit_app.py
```

---

## Réponses aux questions de validation du lab

### **1. Le chatbot utilise-t-il Snowflake Cortex ?**  
Oui, via `SNOWFLAKE.CORTEX.COMPLETE`.

### **2. Le modèle est-il sélectionnable ?**  
Oui, via un `selectbox` dans la sidebar.

### **3. L’historique est-il stocké dans Snowflake ?**  
Oui, dans la table `CONVERSATIONS`.

### **4. L’historique est-il réinjecté dans le prompt ?**  
Oui, chaque message est concaténé dans le prompt final.

### **5. Le projet est-il reproductible ?**  
Oui, grâce au README, au requirements.txt et à l’arborescence claire.

---

## Arborescence du repository

```
snowflake_chatbot/
│
├── streamlit_app.py
├── requirements.txt
├── README.md
├── .gitignore

```

---



## Licence
Projet académique — libre d’utilisation dans un cadre pédagogique.

