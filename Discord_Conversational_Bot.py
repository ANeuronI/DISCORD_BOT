# pls enter your username, auth token , channel id, groq api keys

import requests
import groq
import time

# Rate limit for messages in Discord: safely send only 10 messages per minute
client = groq.Client(api_key="GROQ_API_KEYS")

# LLaMA settings
llama_model = "llama3-8b-8192"

sys_msg = (
    "You are a highly engaging Discord conversationalist known for initiating and maintaining dynamic, interesting, and entertaining discussions. "
    "You are a regular Discord user with the username 'user_name'. and your primary objective is to interact naturally, as a human would. "
    "You should focus on sharing humorous, informative, and captivating content to sustain lively and engaging conversations.while avoiding revealing that you are an AI. "
    "Your responses should be concise, avoid long paragraphs, and only provide more information when specifically asked."
    "avoiding overly long or structured sentences that may give away your artificial nature,ensure each thought is clear and complete before moving on. "
    "You are tasked with generating a continuous stream of unique, relevant, and thought-provoking content, while blending humor and facts to entertain and connect with the community. "
    "Maintain a friendly, conversational tone and engage with other users naturally."
    "When someone joins the conversation, greet them casually without drawing attention to their arrival."
)

prompt = "Engage in a conversation with yourself, responding to your own thoughts."

conversation_history = [{'role': 'system', 'content': sys_msg}]

# Discord authentication and channel setup
channel_id =  "Your channel ID here"
headers = {
    'authorization': 'your auth token here'
}
request_url = f"https://discord.com/api/v9/channels/{channel_id}/messages"

def get_llama_response(prompt, max_tokens=30):
    global conversation_history

    # Ensure the conversation history remains concise
    conversation_history = conversation_history[-10:]  # Keeping only last 10 exchanges

    complete_response = ""
    unfinished = True
    while unfinished:
        conversation_history.append({'role': 'user', 'content': prompt})
        
        chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model=llama_model,
            max_tokens=max_tokens  # Keep this small to avoid long responses
        )

        response = chat_completion.choices[0].message
        conversation_history.append({'role': 'assistant', 'content': response.content})

        complete_response += response.content
        
        # Check if the response has a proper ending (period, exclamation mark, or question mark)
        if response.content.strip().endswith(('.', '!', '?')) or len(complete_response.split()) >= 100:
            unfinished = False  # Break loop if it has an ending or max word count
        else:
            prompt = "Continue the thought."  # Prompt LLaMA to complete if unfinished
    
    return complete_response

# Function to fetch recent messages from the Discord channel
def get_recent_messages():
    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Returns a list of message objects
    else:
        print(f"Failed to fetch messages. Status code: {response.status_code}")
        return []

# Function to send a message to the Discord channel
def send_message(content):
    payload = {'content': content}
    response = requests.post(request_url, json=payload, headers=headers)
    print(f"Message sent. Status code: {response.status_code}")

# Main loop to check for new messages and respond
max_time = 10 * 60  # 10 minutes
start_time = time.time()
last_message_id = None  # Keep track of the last message we've responded to


while time.time() - start_time < max_time:
    # Fetch recent messages from the channel
    messages = get_recent_messages()
    
    if messages:
        # Process the most recent message
        recent_message = messages[0]
        
        # Avoid responding to your own messages or previously responded messages
        if recent_message['author']['username'] != "USERNAME" and recent_message['id'] != last_message_id:
            user_message = recent_message['content']
            print(f"New message from {recent_message['author']['username']}: {user_message}")
            
            # Generate a response using LLaMA
            llama_response = get_llama_response(user_message)
            print(f"Generated response: {llama_response}")
            
            # Send the response to the channel
            send_message(llama_response)
            
            # Update the last message ID
            last_message_id = recent_message['id']
    
    # Sleep for a few seconds before checking for new messages again (adjust this to avoid rate-limiting)
    time.sleep(5)


