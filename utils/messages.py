import random

def response(name: str, message: str):
    #reply to hi hello
    hello_msg = ['hi', 'hello', 'hey']
    user_msg = message.split()

    for msg in user_msg:
        if msg.lower() in hello_msg:
            reply = f"{random.choice(hello_msg).capitalize()} {name}"
            return reply

    #reply to intro
    intro_qn = ['tell me about you', 'can you introduce yourself', 'can i get your intro', 'who are you', 'can i get your introduction']
    intro_msg = message.lower().replace("?", "")
    if intro_msg in intro_qn:
        reply = "I am discord bot made by the one and only Astra! I got a lot of useful commands for your server."
        return reply

    return "I'm sorry! I didn't get you."
