#!/usr/bin/env python
import sys
sys.path.insert(1, '../tortoise-tts/tortoise')

import asyncio
from flask import Flask
# !pip install flask flask-restful
from flask_restful import Resource, Api, reqparse
from flask import send_from_directory
import pandas as pd
import ast
import re
import os
from api import TextToSpeech, MODELS_DIR
from utils.audio import load_voices, load_audio
import torch
import torchaudio
from pydub import AudioSegment
import glob


RESULTS_DIR = 'tts_results/'
VOICE_DIR = 'tts_voices/'
SCRIPT_FILENAME = 'script'
AUDIO_SELECTION = 0
SOUND_DBFS = -14
SPEED = 'ultra_fast'
print('initialising tts...')
tts = TextToSpeech()
print('init completed')


async def generate_audio(text,person, audio_url):
   
    print('audio prompt: ' + text)

    try:
        output_path = ''
        voice_samples, conditioning_latents = load_voices([person],[VOICE_DIR])
        print('generating tts module')
        gen, dbg_state = tts.tts_with_preset(text, k=2, voice_samples=voice_samples, conditioning_latents=conditioning_latents,
                                  preset=SPEED, use_deterministic_seed=None, return_deterministic_state=True, cvvp_amount=.0)

        if isinstance(gen, list):
            person = re.sub(r"\s+", '_', person)#remove white spaces
            output_path = os.path.join(RESULTS_DIR, f'{person}.wav')
            print("save " + output_path)
            torchaudio.save(output_path, gen[AUDIO_SELECTION].squeeze(0).cpu(), 24000)

        # if isinstance(gen, list):
        #     for j, g in enumerate(gen):
        #         output_path = os.path.join(RESULTS_DIR, f'{person}_{j}.wav')
        #         print(output_path)
        #         torchaudio.save(output_path, g.squeeze(0).cpu(), 24000)
        #         break
        # else:
        #     print('Error in Saving')
        #     return
                   
        audio_url[0] = output_path

    except Exception:
     return


async def generate_stiched_audio(texts,persons, audio_url):

    #remove all files before stitching
    files = glob.glob(RESULTS_DIR + "*")
    for f in files:
       os.remove(f)

    all_urls=[]
    for i, person in enumerate(persons):
       
       print(person + ": " + texts[i])
       await generate_audio(texts[i],person, audio_url)
       fname = os.path.splitext(audio_url[0])[0]
       renamed = fname + "_" + str(i) + '.wav'
       os.rename(audio_url[0], renamed)
       print(renamed)
       all_urls.append(renamed)

    print(all_urls)
    #stick all urls together

    print('combining: ' + all_urls[0])
    audio_clip = AudioSegment.from_file(all_urls[0], format="wav") + AudioSegment.silent(duration=1000)

    change_in_dBFS = SOUND_DBFS - audio_clip.dBFS
    audio_clip = audio_clip.apply_gain(change_in_dBFS)

    louder = audio_clip + 6

    for i in range(1, len(all_urls)):
         print('combining: ' + all_urls[i])
         new_clip = AudioSegment.from_file(all_urls[i], format="wav") + AudioSegment.silent(duration=1000)
         change_in_dBFS = SOUND_DBFS - new_clip.dBFS
         new_clip = new_clip.apply_gain(change_in_dBFS)
         audio_clip = audio_clip + new_clip

    # persons = '_'.join(persons)
    # persons = re.sub(r"\s+", '_', persons)#remove white spaces

    audio_url[0] = audio_clip.export(os.path.join(RESULTS_DIR, f'{SCRIPT_FILENAME}.wav'), format="wav")     

def generate_audio_callback(text,person, audio_url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(generate_audio(text,person, audio_url))
    loop.close()

def generate_stiched_audio_callback(texts,persons, audio_url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(generate_stiched_audio(texts,persons, audio_url))
    loop.close()