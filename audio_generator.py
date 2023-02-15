#!/usr/bin/env python
import sys
sys.path.insert(1, '../tortoise-tts/tortoise')

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


RESULTS_DIR = 'tts_results/'
AUDIO_SELECTION = 0
SPEED = 'ultra_fast'
print('initialising tts...')
tts = TextToSpeech()
print('init completed')


def generate_audio(text,person, audio_url):
   
    print('audio prompt: ' + text)

    try:
        output_path = ''
        voice_samples, conditioning_latents = load_voices([person])
        print('generating tts module')
        gen, dbg_state = tts.tts_with_preset(text, k=3, voice_samples=voice_samples, conditioning_latents=conditioning_latents,
                                  preset=SPEED, use_deterministic_seed=None, return_deterministic_state=True, cvvp_amount=.0)

        if isinstance(gen, list):
            person = re.sub(r"\s+", '_', person)#remove white spaces
            output_path = os.path.join(RESULTS_DIR, f'{person}.wav')
            print(output_path)
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
                   
        # audio_url[0] = output_path

    except Exception:
     return


def generate_stiched_audio(texts,persons, audio_url):
    
    all_urls=[]
    for person in persons:
       generate_audio(text,person, audio_url):
       all_urls.append(audio_url)

    print(all_urls)
    #stick all urls together

    audio_clip = AudioSegment.from_file(all_urls[0], format="wav")

    louder = audio_clip + 6

    for i in range(1, len(all_urls)):
         new_clip = AudioSegment.from_file(all_urls[i], format="wav")
         audio_clip += new_clip

    persons = '_'.join(persons)
    persons = re.sub(r"\s+", '_', persons)#remove white spaces

    audio_url[0] = combined.export(os.path.join(RESULTS_DIR, f'{persons}.wav'), format="wav")     
