import os
import openai
import settings



def generate_text(query,query_response):

  openai.api_key = settings.OPENAI_API_TOKEN

  # get reponse from openai's text-davinci-003 aka GPT-3
  # You can play around with the filter to get a better result
  # Visit https://beta.openai.com/docs/api-reference/completions/create for more info
  print(query)
  try:
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=query,
      temperature=0.8,
      max_tokens=512,
      top_p=1,
      logprobs=10,
    )
  except Exception as e:
    print(f'Exception : {str(e)}')
    query_response[0] = "Sorry a server has occured!"
    return

  text_response = response["choices"][0]["text"]
  print(text_response)

  query_response[0] = text_response

