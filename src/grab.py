import requests
import ffmpeg
import os
import dotenv
from elevenlabs import Voice, VoiceSettings, generate, play, set_api_key, save
from faster_whisper import WhisperModel

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

def getAudioDuration(path):
    return float(ffmpeg.probe(path)['format']['duration'])

def formatVideo(inPath, outPath, srtPath, start, end):
    if os.path.exists(outPath):
        os.remove(outPath)
    input_file = ffmpeg.input(inPath)
    fonts_dir = "/src/files/Font.otf"
    style = "FontName=FONTSPRINGDEMO-ModicaBlackRegular,FontSize=22,Alignment=10,Outline=2"
    output_file = ffmpeg.output(input_file.filter_('crop', w='9/16*in_h', h='in_h', x='1/2*in_w - 0.5*9/16*in_h', y='0').filter("subtitles",filename=srtPath,fontsdir=fonts_dir,force_style=style).trim(start=start, end=end).setpts('PTS-STARTPTS'), outPath).global_args("-an")
    output_file.run()

def formatSeconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    milli = str(int(s * 1000))
    milli = "0"*(5-len(milli)) + milli
    return f'{int(h):02d}:{int(m):02d}:{milli[:2]},{milli[2:]}'


createTTS('''Using a throwaway because he probably knows my main and I don't want him to know I know yet. This also technically started a few days ago but it's been stuck in my head since and I need to get my thoughts out.

When we met and the entire 3 years we dated before we married, I was always firm about not wanting kids. My husband told me that his stance on kids was along the lines of "kind of undecided, but overall not a good idea". Always said he used to want kids but changed his mind later in life.

I wholeheartedly believed him until I decided to snoop. We're both pretty avid reddit users and he wanted to brag to me about how many upvotes one of his comments had. I watched him as he clicked on his profile to find it, and I caught his username and a glimpse of another comment where it looked like he was talking about me. We've never tried hiding each other's accounts from one another so it's not like his was secret, but I still feel a little bad for letting curiosity get the best of me. I looked up his username later in the day to check out what he had to say about me.

To his credit, he was gushing about me and it was really sweet. But, quite a few of his other comments also talked about how he wishes he could have children of his own and that the only thing stopping him is me. Talks about how his desire to be with me outmatches his desire to have kids, but he's still heartbroken that he can't have both.

I still don't know what to make of it. On the one hand, I'm hurt that in the almost 10 years we've been together he's never talked to me about this and Instead lied to make it seem like we were on the same page. I feel immense guilt that I've taken such a choice away from him, especially after reading about just how badly he wants it.
''')
model_size = "small"
model = WhisperModel(model_size, device="cpu", compute_type="int8")
segments, _ = model.transcribe(
    "src/files/audio.mp3", 
    word_timestamps=True, 
    # vad_filter=True, 
    # vad_parameters=dict(min_silence_duraton_ms=500),
    )

with open("src/files/subtitles.srt","w") as f:
    i = 1
    for segment in segments:
        for word in segment.words:
            f.write(f'{i}\n{formatSeconds(word.start)} --> {formatSeconds(word.end)}\n{word.word.strip(" .,")}\n\n')
            i += 1

formatVideo('src/files/parkour.mp4','src/files/map1.mp4','src/files/subtitles.srt',0,80)
# formatVideo('src/files/parkour.mp4','src/files/map2.mp4',81,141)
# formatVideo('src/files/parkour.mp4','src/files/map3.mp4',142,195)
# formatVideo('src/files/parkour.mp4','src/files/map4.mp4',196,274)