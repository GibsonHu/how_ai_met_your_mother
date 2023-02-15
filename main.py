#!/usr/bin/env python

import os
import discord
import re
import random
from keep_alive import keep_alive
import subprocess
import settings
from image_generator import generate_image
from text_generator import generate_text
from audio_generator import generate_audio
from threading import Thread
import time

#keep env alive
# keep_alive()


# Declare our intent with the bot and setting the messeage_content to true
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

#CHARACTER VARIABLES
CHARACTER_NAMES = [
  "Barney Stinson", "Ted Mosby", "Robin Scherbatsky", "Lily Aldrin",
  "Marshall Eriksen", "Tracy McConnell"
]
CHARACTER_ACTOR_NAMES = [
  "Neil Patrick Harris", "Josh Radnor", "Cobie Smulders", 'Alyson Hannigan',
  'Jason Segel', 'Cristin Milioti'
]
CHARACTER_GENDER = ["Male", "Male", "Female", "Female", "Male", "Female"]
CHARACTER_TRAITS = [["Manipulative", "Funny", "Sarcastic"],
                    ["Friendly", "Romantic"], ["Pride", "Fickle-Minded"],
                    ["Caring", "Manipulative"], ["Silly", "Quirky"],
                    ["Sarcastic", "Sarcastic"]]
CHARACTER_KEYWORD = [
  '!barney', '!ted', '!robin', '!lily', '!marshall', '!tracy'
]

LOCATION_KEYWORD = "!place"
LOCATION = " bar, "

IMAGE_COMPOSITION = LOCATION + " looking away , portrait photo headshot by mucha, sharp focus, elegant, render, octane, detailed, masterpiece, rim lit, color"

CHARACTER_IMG_PROMPT = []
for i, name in enumerate(CHARACTER_NAMES):
  CHARACTER_IMG_PROMPT.append(CHARACTER_ACTOR_NAMES[i] + " as young " +
                              CHARACTER_NAMES[i])
  #" holding a glass of beer " + IMAGE_COMPOSITION)
  # CHARACTER_IMG_PROMPT.append(CHARACTER_ACTOR_NAMES[i] + "," +
  #                             IMAGE_COMPOSITION)

CHARACTER_INDEX = 0
CONVERSATION_RANGE = [12, 20]
THREAD_RUNNING = False
CHANNEL_ID = ""
MESSAGE_CONTENT = ""
AUTHOR_NAME = ""


async def update_character(help_msg):
  global LOCATION
  img_prompt = CHARACTER_IMG_PROMPT[CHARACTER_INDEX] + " in a " + LOCATION
  await send_msg(CHARACTER_NAMES[CHARACTER_INDEX] + ' is walking into a ' +
                 LOCATION)
  img_url = [None] * 1
  generate_image(img_prompt, img_url, 768, 768)
  await send_image(img_url[0])
  if help_msg != '':
    await send_msg(help_msg)


async def update(message):

  await client.wait_until_ready()

  global THREAD_RUNNING, CHARACTER_INDEX, CHARACTER_KEYWORD, CHARACTER_NAMES, CHARACTER_TRAITS, AUTHOR_NAME, LOCATION, LOCATION_KEYWORD

  THREAD_RUNNING = True
  #print help mesg
  if await print_help(message):
    THREAD_RUNNING = False
    return

  #debug
  print(message)

  #change location
  if LOCATION_KEYWORD in message:
    message = message.replace(LOCATION_KEYWORD, '')
    print('changing location:' + message)
    if message != '':
      LOCATION = message
      help_msg = ''
      await update_character(help_msg)
    THREAD_RUNNING = False
    return

  #character changed
  if any(word in message for word in CHARACTER_KEYWORD):
    character_asked = [word for word in CHARACTER_KEYWORD if word in message]
    print(character_asked)

    #conversation query
    if len(character_asked) > 1:
      print('Starting a Conversation')
      characters_asked_index = []
      for c in character_asked:
        print(c)
        characters_asked_index.append(CHARACTER_KEYWORD.index(c))
      #   message = message.replace(c, '')

      char_list = ['!', ',']
      msg_list = message.split(" ")
      message = [
        ele for ele in msg_list if all(ch not in ele for ch in char_list)
      ]
      message = " ".join(message)

      print(message)

      #await conversation(message, characters_asked_index)
      await scripted_conversation(message, characters_asked_index)
      THREAD_RUNNING = False
      return
    else:
      print('Starting One on One')
      character_asked = character_asked[0]
      previous_index = CHARACTER_INDEX
      CHARACTER_INDEX = CHARACTER_KEYWORD.index(character_asked)
      print(CHARACTER_INDEX)
      if CHARACTER_INDEX != previous_index:
        help_msg = 'Character changed to ' + CHARACTER_NAMES[
          CHARACTER_INDEX] + ', Type something ...'
        await update_character(help_msg)
        THREAD_RUNNING = False
        return

    message = message.strip(character_asked)

  trait_index = random.randint(0, len(CHARACTER_TRAITS[CHARACTER_INDEX]) - 1)

  #Talk To chatbot
  message = AUTHOR_NAME + ': ' + message
  await chat(message, CHARACTER_NAMES[CHARACTER_INDEX],
             CHARACTER_TRAITS[CHARACTER_INDEX][trait_index], "")

  THREAD_RUNNING = False


@client.event
async def on_ready():
  """
  Print a message when the bot is ready
  """
  print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
  global CHARACTER_INDEX, CHANNEL_ID, MESSAGE_CONTENT, AUTHOR_NAME
  """
  Listen to message event
  """

  # ignore messages from the bot itself and messages that don't start with the prefix we have set
  if message.author == client.user:
    return

  if THREAD_RUNNING == False:
    CHANNEL_ID = message.channel.id
    AUTHOR_NAME = message.author.name
    client.loop.create_task(update(message.content))
  else:
    print("Message Still Processing")


async def print_help(message):
  if message == 'help':
    help_msg = 'To change characters type: ' + ', '.join(
      CHARACTER_KEYWORD
    ) + ' \n\nStart a conversaion between characters type: <character_name1> <character_name2> <etc> <topic> \nShow availible characters type: characters\nChange location type: ' + LOCATION_KEYWORD + '\n'
    await send_msg(help_msg)
    return True

  if message == 'characters':
    help_msg = 'Availible Characters: ' + ', '.join(CHARACTER_KEYWORD)
    await send_msg(help_msg)
    return True

  return False


async def send_msg(text):
  global CHANNEL_ID
  text = re.sub('\*.*?\*', '', text)
  text = text.replace('How I Met Your Mother', 'the show')

  print('sending: ' + text)
  try:
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(text)
  except Exception:
    return


async def send_image(image_url):
  global CHANNEL_ID
  try:
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(image_url)
  except Exception:
    return

async def send_audio(audio_file):
  global CHANNEL_ID
  try:
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(file=discord.File(audio_file))
  except Exception:
    return



async def chat(message, character_name, character_trait, topic):

  # create a chat prompt the prompt from the messsage by spliting the command
  query = message
  query += ", respond in a " + character_trait + " tone"
  query += ", respond as the voice of " + character_name
  #query += ' in the style of a late night talk show'
  if topic != "":
    query += ',  stay on the topic of ' + topic

  query += ' pretend to be on the show how i met your mother'

  #send openai query
  chat_response = [None] * 1
  generate_text(query, chat_response)
  chat_response = chat_response[0]
  if chat_response == '':  #empty response
    return

  #Filter Chat Reponse
  chat_response = chat_response[chat_response.find(':') + 1:]
  chat_response = ''.join(chat_response.splitlines())

  audio_url = [None] * 1
  audio_thread = Thread(target=generate_audio, args=(chat_response,character_name, audio_url))
  audio_thread.start()

  #response_text = response_text.replace('Marshall', 'Marshal')  #common mistake
  #response_text = character_name + ": " + response_text
  response_text = character_name + ": " + re.sub(' +', ' ', chat_response)  #remove large spacing

  #send msg to discord
  await send_msg(response_text)

  #WAIT FOR AUDIO THREAD
  audio_thread.join()
  print(audio_url[0])
  await send_audio(audio_url[0])

  return response_text


#Write A Script Between Different Characters
async def scripted_conversation(message, character_indicies):
  global LOCATION

  await send_msg('Script being generated please wait ... \n')

  if len(character_indicies) < 2:
    print('not enough characters to create a conversation < 2')
    return

  topic = message

  conversation_len = random.randint(CONVERSATION_RANGE[0],
                                    CONVERSATION_RANGE[1])

  #SETUP QUERIES
  img_query = ""  #str(len(character_indicies)) + " People talking to each other, "
  for count, name_index in enumerate(character_indicies):
    img_query += CHARACTER_NAMES[
      name_index]  #+ " as " + CHARACTER_NAMES[name_index]
    if count < len(character_indicies) - 1:
      img_query += " and "
  #Image Prompt
  img_query = img_query + " at a " + LOCATION + " talking to each other, sharp focus, elegant, render, octane, detailed, award winning photography, masterpiece, rim lit"

  query = ""
  for count, name_index in enumerate(character_indicies):
    query += CHARACTER_NAMES[name_index]
    if count < len(character_indicies) - 1:
      query += " and "
  #Script Prompt
  query = 'Write a ' + str(conversation_len) + ' line script between ' + query
  query += " about " + topic
  query += " reference things from the show how i met your mother"

  #RUN GENERQATION THREADS
  img_url = [None] * 1
  img_thread = Thread(target=generate_image,
                      args=(img_query, img_url, 768, 1024))
  img_thread.start()

  chat_response = [None] * 1
  chat_thread = Thread(target=generate_text, args=(query, chat_response))
  chat_thread.start()

  #Wait for Threads To Finish
  img_thread.join()
  await send_image(img_url[0])

  chat_thread.join()
  chat_response = chat_response[0]

  print(chat_response)

  #sort reponse
  text_data = chat_response.splitlines()
  print(text_data)
  response_text = ''

  #sort into dictionary
  script_dictionary = []
  for text in text_data:
    if text != '':
      name = text[0:text.find(':')]
      character_names_lower = [x.lower() for x in CHARACTER_NAMES]
      names = [i for i in character_names_lower if name.lower() in i]
      if len(names) > 0:
        name = CHARACTER_NAMES[character_names_lower.index(names[0])]

      script = text[text.find(':') + 1:]
      script_dictionary.append([name, script])

  print(script_dictionary)

  for script in script_dictionary:
    time.sleep(2)
    text = script[0] + ":" + script[1]
    await send_msg(text)

  response_text = ''.join(text_data)
  return response_text

  # if chat_response == '':  #empty response
  #   return response_text

  # response_text = " " + chat_response
  # response_text = ''.join(response_text.splitlines())
  # response_text = re.sub(' +', ' ', response_text)  #remove large spacing
  # await send_msg(response_text)


#Create  A Conversation Between Different Characters
async def conversation(message, character_indicies):
  topic = message
  message = ""

  if len(character_indicies) < 2:
    print('not enough characters to create a conversation < 2')
    return

  #start the conversation
  current_character_index = -1

  conversation_len = random.randint(CONVERSATION_RANGE[0],
                                    CONVERSATION_RANGE[1])
  print(conversation_len)

  #setup all conversations
  character_indices = []
  for count in range(conversation_len):
    current_character_index = random.choice(
      [i for i in character_indicies if i not in [current_character_index]])
    print('chracter speaking: ' + CHARACTER_NAMES[current_character_index])
    print(current_character_index)
    character_indices.append(current_character_index)

  for i, character_index in enumerate(character_indices):
    #determine what gender character is talking to

    #select a random character trait
    trait_index = random.randint(0, len(CHARACTER_TRAITS[character_index]) - 1)

    #next character talking
    message = await chat(message, CHARACTER_NAMES[character_index],
                         CHARACTER_TRAITS[character_index][trait_index], topic)

    await send_msg('\n\n.')

  # #continue the conversation
  # for count in range(conversation_len):
  #   current_character_index = random.choice(
  #     [i for i in characters if i not in [current_character_index]])
  #   print('chracter speaking: ' + CHARACTER_NAMES[current_character_index])
  #   print(current_character_index)

  #   trait_index=0
  #   if CHARACTER_GENDER[current_character_index] == "Female":
  #     trait_index = 1
  #   #next character talking
  #   message.content = await chat(message,
  #                                CHARACTER_NAMES[current_character_index],
  #                                CHARACTER_TRAITS[current_character_index][trait_index])
  #   await send_msg(message, ' +')

  print('end of conversation')
  return


# try:
client.run(settings.DISCORD_TOKEN)
# except Exception:
#   subprocess.Popen('kill 1', shell=True)  #fix for discrod access bug
