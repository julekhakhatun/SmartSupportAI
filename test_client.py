import requests

response = requests.post(
    'http://127.0.0.1:5000/api/ask',
    json={'prompt': 'Tell me a story.'},
    stream=True
)

for line in response.iter_lines(decode_unicode=True):
    if line:
        print(line, end='', flush=True)


