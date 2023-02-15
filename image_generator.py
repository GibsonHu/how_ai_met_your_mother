#!/usr/bin/env python
import os
import replicate
import requests
import json
import io
import base64
from PIL import Image
import settings

import sys
sys.path.insert(1, '../stable-diffusion-webui/tortoise')


def generate_image_local(prompt, img_url, width, height):

  payload = {'prompt': prompt, 'steps': '10', 'width': width, 'height': height}

  try:
    response = requests.post(url=f'http://127.0.0.1:7860/sdapi/v1/txt2img',
                             json=payload)
  except Exception:
    print('Error!')

  data = response.json()

  print(data.keys())

  image_file = 'output.png'
  all_images = []
  for i in data['images']:
    d = i.split(",", 1)[0]
    image = Image.open(io.BytesIO(base64.b64decode(d)))
    image.save(image_file)
    all_images.append(image)

  return image_file


def generate_image(prompt, img_url, width, height):
  print('image prompt: ' + prompt)

  model = replicate.models.get("stability-ai/stable-diffusion")
  version = model.versions.get(
    'f178fa7a1ae43a9a9af01b833b9d2ecf97b1bcb0acfd2dc5dd04895e042863f1')

  # https://replicate.com/stability-ai/stable-diffusion/versions/f178fa7a1ae43a9a9af01b833b9d2ecf97b1bcb0acfd2dc5dd04895e042863f1#input
  inputs = {
    # Input prompt
    # 'prompt': "\"" + prompt + "\"",
    'prompt': prompt,
    # Specify things to not see in the output
    # 'negative_prompt': ...,

    # Width of output image. Maximum size is 1024x768 or 768x1024 because
    # of memory limits
    'width': width,

    # Height of output image. Maximum size is 1024x768 or 768x1024 because
    # of memory limits
    'height': width,

    # Prompt strength when using init image. 1.0 corresponds to full
    # destruction of information in init image
    'prompt_strength': 1.0,

    # Number of images to output.
    # Range: 1 to 4
    'num_outputs': 1,

    # Number of denoising steps
    # Range: 1 to 500
    'num_inference_steps': 40,

    # Scale for classifier-free guidance
    # Range: 1 to 20
    'guidance_scale': 7.5,

    # Choose a scheduler.
    'scheduler': "K_EULER",

    # Random seed. Leave blank to randomize the seed
    # 'seed': ...,
  }
  # https://replicate.com/stability-ai/stable-diffusion/versions/f178fa7a1ae43a9a9af01b833b9d2ecf97b1bcb0acfd2dc5dd04895e042863f1#output-schema
  output = version.predict(**inputs)
  print(output)

  img_url[0] = output[0]
