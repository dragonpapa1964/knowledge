# ライブラリをインポート
import requests
import json
import streamlit as st
from streamlit_chat import message

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv()

# JUST.DBのAPIに接続するための情報
API_Endpoint = 'https://sankyu-road-engi.just-db.com/sites/api/services/v1/tables/table_1702423963/records/?limit=100'
API_Key = 'Bearer szemElvTAaVqUCRHkOLw1BNmVuC2Cwv4'

# APIに送信する情報
headers = {'Content-Type': 'application/json', 'Authorization':API_Key}

# API接続の実行
result = requests.get(API_Endpoint, headers=headers)

#JUST.DBから知識ベースを読み込み
knowledge_base=''

json_dict=json.loads(result.text)
#print('読み込み件数：' + str(len(json_dict)))
for jdata in json_dict:
     #print(jdata['record']['field_1702424033'])
     knowledge_base=knowledge_base+jdata['record']['field_1702424033']

knowledge_base=knowledge_base+" これを元に質問に答えてください。"

#プロンプトテンプレートを作成
template = knowledge_base

# 会話のテンプレートを作成
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(template),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}"),
])

#会話の読み込みを行う関数を定義
@st.cache_resource
def load_conversation():
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0
    )
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(
        memory=memory,
        prompt=prompt,
        llm=llm)
    return conversation

# 質問と回答を保存するための空のリストを作成
if "generated" not in st.session_state:
    st.session_state.generated = []
if "past" not in st.session_state:
    st.session_state.past = []

# 送信ボタンがクリックされた後の処理を行う関数を定義
def on_input_change():
    user_message = st.session_state.user_message
    conversation = load_conversation()
    answer = conversation.predict(input=user_message)

    st.session_state.generated.append(answer)
    st.session_state.past.append(user_message)

    st.session_state.user_message = ""

# タイトルやキャプション部分のUI
st.title("SREの知恵袋")
st.caption("SANKYU ROAD ENGINEERING INC.")
st.write("SREの知識ベースに基づいて質問に答えます。")

# 会話履歴を表示するためのスペースを確保
chat_placeholder = st.empty()

# 会話履歴を表示
with chat_placeholder.container():
    for i in range(len(st.session_state.generated)):
        message(st.session_state.past[i],is_user=True)
        message(st.session_state.generated[i])

# 質問入力欄と送信ボタンを設置
with st.container():
    user_message = st.text_input("質問を入力する", key="user_message")
    st.button("送信", on_click=on_input_change)