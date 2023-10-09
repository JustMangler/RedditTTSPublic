import requests
import ffmpeg
import os
# import dotenv
# from elevenlabs import Voice, VoiceSettings, generate, play, set_api_key, save
from faster_whisper import WhisperModel
import random
import torch
from TTS.api import TTS
from better_profanity import profanity
import sys
import gc


class CreateTTS:

    def __init__(self, URL):
        URL = URL.strip("/.json") + ".json"

        # Set Coqui TTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS("tts_models/en/vctk/vits").to(device)

        # Send Request to get reddit post
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }

        response = requests.get(URL, headers=headers)
        res_json = response.json()

        post, comments = res_json
        postData = post['data']['children'][0]['data']

        self.title = postData['title']
        self.author = postData['author']
        self.subreddit = postData['subreddit_name_prefixed']
        self.score = postData['score']
        self.text = postData['selftext'].replace("&amp;", "")

    # def createTTS(script, audioFile, voice):
    #     set_api_key(os.getenv('ELEVEN_API_KEY'))

    #     voice=Voice(
    #         voice_id=voices[voice],
    #         settings=VoiceSettings(stability=0.33, similarity_boost=0.5, style=0.17, use_speaker_boost=False)
    #     )
    #     audio = generate(text=script,voice=voice, model="eleven_multilingual_v2")
    #     save(audio, audioFile)

    def createTTS(self, script, audioFile):
        self.tts.tts_to_file(
            text=script, speaker=self.tts.speakers[48], file_path=audioFile)

    def getAudioDuration(self, path):
        return float(ffmpeg.probe(path)['format']['duration'])

    def formatVideo(self, inPath, outPath, srtPath, audioFile):
        width, height, duration = ffmpeg.probe(inPath)['streams'][0]['width'], ffmpeg.probe(
            inPath)['streams'][0]['height'], ffmpeg.probe(inPath)['streams'][0]['duration']

        timeStart = random.randint(
            0, int(float(duration) - self.getAudioDuration(audioFile)) - 1)
        timeEnd = timeStart + self.getAudioDuration(audioFile)
        if width > 9/16 * height:
            w = '9/16*in_h'
            h = 'in_h'
            x = '1/2*in_w - 0.5*9/16*in_h'
        else:
            w = 'in_w'
            h = '16/9 * in_w'
            x = '0'

        fonts_dir = "/src/files/Font.otf"
        style = "FontName=Metropolis-Black,FontSize=22,Alignment=10,Outline=1"
        video = (
            ffmpeg
            .input(inPath)
            .filter_('crop', w=w, h=h, x=x, y='0')
            .trim(start=timeStart, end=timeEnd)
            .setpts('PTS-STARTPTS')
            .filter("subtitles", filename=srtPath, fontsdir=fonts_dir, force_style=style)

        )

        video = ffmpeg.filter([video, ffmpeg.input(
            'src/files/title.png')], 'overlay', enable=f"between(t,0,{self.titleLength})")

        audio = ffmpeg.input(audioFile)
        ffmpeg.concat(video, audio, v=1, a=1).output(
            outPath).run(overwrite_output=True)

    def formatSeconds(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        milli = str(int(s * 1000))
        milli = "0"*(5-len(milli)) + milli
        return f'{int(h):02d}:{int(m):02d}:{milli[:2]},{milli[2:]}'

    def createParts(self):
        chars_per_video = 3500
        parts = int(len(self.text) / chars_per_video) + 1
        characters_per_part = int(len(self.text)/parts)

        # self.createTTS(self.title, 'src/files/title.mp3')

        print("Created TTS for Title")
        self.titleLength = self.getAudioDuration('src/files/title.mp3')

        # for part in range(parts):
        #     print(f'Creating Video Part{part}')
        #     self.createTTS(self.text[part*characters_per_part:(part+1) *
        #                              characters_per_part], f'src/files/audio{part}.mp3')

        #     ffmpeg.concat(ffmpeg.input('src/files/title.mp3'), ffmpeg.input(
        #         f'src/files/audio{part}.mp3'), v=0, a=1).output(f'src/files/audio{part}c.mp3').run(overwrite_output=True)

        sys.modules.pop('TTS.api')
        sys.modules.pop('TTS')

        del self.tts
        gc.collect()
        torch.cuda.empty_cache()

        self.model = WhisperModel(
            "medium", device="cpu", compute_type="int8")
        for part in range(parts):
            print(f'Creating Captions Part{part}')
            segments, _ = self.model.transcribe(
                f"src/files/audio{part}c.mp3",
                word_timestamps=True,
            )
            print('after breaking')

            with open(f"src/files/subtitles{part}.srt", "w") as f:
                i = 1
                for segment in segments:
                    for word in segment.words:
                        f.write(
                            f'{i}\n{self.formatSeconds(word.start)} --> {self.formatSeconds(word.end)}\n{profanity.censor(word.word.strip(" "))}\n\n')
                        i += 1

            print(f'Stitching Everything Together Part{part}')
            self.formatVideo('src/files/subwaysurfers3M.mp4',
                             f'src/files/TTS{part}.mp4', f'src/files/subtitles{part}.srt', f'src/files/audio{part}.mp3')
