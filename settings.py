# settings.py
#!/usr/bin/env python

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
print(dotenv_path)
load_dotenv(dotenv_path)

#KEYS
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
REPLICATE_API_TOKEN = os.environ['REPLICATE_API_TOKEN']
OPENAI_API_TOKEN = os.environ['OPENAI_API_KEY']  #
