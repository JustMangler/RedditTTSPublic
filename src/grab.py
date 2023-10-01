import requests
import openai
import os
import dotenv
from elevenlabs import Voice, VoiceSettings, generate, play, set_api_key, save

dotenv.load_dotenv()

def grabContent(URL = 'https://www.reddit.com/r/tifu/comments/16uqfkl/tifu_by_stalking_my_husbands_reddit_account.json'):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }

    response = requests.get(URL, headers=headers)
    res_json = response.json()

    post, comments = res_json
    postData = post['data']['children'][0]['data']

    return postData['title'], postData['author'], postData['subreddit_name_prefixed'], postData['score'], postData['selftext'] 

def createTTS(script):
    set_api_key(os.getenv('ELEVEN_API_KEY'))
    
    voice=Voice(
        voice_id='dGD7D9OJ3wnr8yOehJAa',
        settings=VoiceSettings(stability=0.33, similarity_boost=0.5, style=0.17, use_speaker_boost=False)
    )
    audio = generate(text=script,voice=voice, model="eleven_multilingual_v2")
    save(audio, 'src/files/audio.mp3')

createTTS("Hello, my name is Kelly and I am a big fatty.")