from hugchat import hugchat

chatbot = hugchat.ChatBot(cookie_path="engine/cookies.json")
response = chatbot.chat("Hello!")
print(response)
