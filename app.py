from flask import Flask, request, render_template, redirect, url_for, redirect
import openai
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

messages = [{"role": "system", "content": "あなたは助けになるアシスタントです。"}]

@app.route('/chat', methods=['GET'])
def get_chat():
    conn = mysql.connector.connect(user='user', password='password', host='db', database='chat_db')
    cursor = conn.cursor()

    # チャットの履歴を取得
    cursor.execute('SELECT user_message, bot_response FROM chat')
    chat_history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('chat.html', chat_history=chat_history)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    messages.append({'role': 'user', 'content': user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_message = response.choices[0].message['content']
    messages.append({'role': 'assistant', 'content': bot_message})

    conn = mysql.connector.connect(user='user', password='password', host='db', database='chat_db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat (user_message, bot_response) VALUES (%s, %s)', (user_message, bot_message))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('get_chat'))

@app.route('/clear', methods=['POST'])
def clear_chat():
    conn = mysql.connector.connect(user='user', password='password', host='db', database='chat_db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat')
    conn.commit()
    cursor.close()
    conn.close()

    # リセットmessages
    messages.clear()
    # 再度、初期のシステムメッセージを追加
    messages.append({"role": "system", "content": "あなたは助けになるアシスタントです。"})

    return redirect("/chat")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
