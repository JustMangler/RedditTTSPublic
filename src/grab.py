import requests
import ffmpeg
# import dotenv
import os
from faster_whisper import WhisperModel
import random
from better_profanity import profanity
from create_post import create_thumbnail
import boto3
import time
from io import BytesIO
from tiktok_uploader.upload import upload_video, upload_videos
from tiktok_uploader.auth import AuthBackend


class CreateTTS:

    def __init__(self, URL):
        self.URL = URL.strip("/.json") + ".json"
        self.accountID = 17841462676420553
        self.accessToken = 'EAAmVIPsZBZBg8BO66gu7uCamiP2Dp5jYc1yLqts0OZBl5vfmm009uQE88cYYyHd7kvSpgc6Y3UvZCTFxYVKClEEB4dZBqpKv3HmHoaMiGwrJwhmT1qeR6ZAZAWYPE2ftKe4liCeCa3BOvyeYZAiRvp56AThMfnQELVSXBpcmiY4k1SBZC7Dyc4NNCKFyjmMNaAH6f'

        self.client = boto3.client('polly')
        self.s3_client = boto3.client('s3')

        self.model = WhisperModel(
            "large-v2", device="cpu", compute_type="int8")

        # Send Request to get reddit post
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }

        response = requests.get(self.URL, headers=headers)
        res_json = response.json()

        post, comments = res_json
        postData = post['data']['children'][0]['data']

        self.title = postData['title']
        self.author = postData['author']
        self.subreddit = postData['subreddit_name_prefixed']
        self.score = postData['score']
        self.text = postData['selftext'].replace(
            "&amp;", "").replace("#x200B", "").replace(";", ".").replace(":", ".").replace("shit", "shite").replace("fuck", "fudge").replace("sex", "seggs").replace("cum", "coom")

    def createTTS(self, script, audioFile):
        response = self.client.synthesize_speech(
            Engine='standard',
            LanguageCode='en-US',
            OutputFormat='mp3',
            Text=script,
            TextType='text',
            VoiceId='Matthew'
        )

        process = (
            ffmpeg
            .input('pipe:')
            .output(audioFile)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
        process.communicate(input=BytesIO(
            response.get("AudioStream")._raw_stream.data).getbuffer())

    def getAudioDuration(self, path):
        return float(ffmpeg.probe(path)['format']['duration'])

    def formatVideo(self, inPath, outPath, srtPath, audioFile, part):
        width, height, duration = ffmpeg.probe(inPath)['streams'][0]['width'], ffmpeg.probe(
            inPath)['streams'][0]['height'], ffmpeg.probe(inPath)['streams'][0]['duration']

        timeStart = random.randint(
            0, int(float(duration) - self.getAudioDuration(audioFile)) - 1)
        timeEnd = timeStart + self.getAudioDuration(audioFile)
        if width > 9/16 * height:
            w = '9/16*in_h'
            h = 'in_h'
            x = '1/2*in_w - 0.5*9/16*in_h'
            width = 9/16 * height
        else:
            w = 'in_w'
            h = '16/9 * in_w'
            x = '0'
            height = 16/9 * width

        fonts_dir = "/src/files/font/Font.otf"
        style = "FontName=Metropolis-Black,FontSize=16,Alignment=10,Outline=1"
        video = (
            ffmpeg
            .input(inPath)
            .filter_('crop', w=w, h=h, x=x, y='0')
            .trim(start=timeStart, end=timeEnd)
            .setpts('PTS-STARTPTS')
            .filter("subtitles", filename=srtPath, fontsdir=fonts_dir, force_style=style)

        )

        create_thumbnail(self.URL, int(width), int(height), part)

        video = ffmpeg.filter([video, ffmpeg.input(
            'src/files/images/title.png')], 'overlay', enable=f"between(t,0,{self.titleLength})")

        audio = ffmpeg.input(audioFile)
        ffmpeg.concat(video, audio, v=1, a=1).output(
            outPath).run(overwrite_output=True)

    def formatSeconds(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        milli = str(int(s * 1000))
        milli = "0"*(5-len(milli)) + milli
        return f'{int(h):02d}:{int(m):02d}:{milli[:2]},{milli[2:]}'

    def removeExtraneousTTS(self):
        path = '/Users/vincentzhou/Documents/RedditBot/'
        for filename in os.listdir(f'{path}src/files'):
            file_path = os.path.join(f'{path}src/files', filename)
            if os.path.isfile(file_path) and os.path.splitext(filename)[0][:3] == 'TTS' and os.path.splitext(filename)[-1].lower() == '.mp4':
                os.remove(file_path)
        if 'Contents' in self.s3_client.list_objects(Bucket='wwz4-polly-bucket', Prefix='TTS/'):
            for filename in self.s3_client.list_objects(Bucket='wwz4-polly-bucket', Prefix='TTS/')['Contents']:
                self.s3_client.delete_object(
                    Bucket='wwz4-polly-bucket', Key=filename['Key'])

    def post_reel(self, file):

        graph_url = 'https://graph.facebook.com/v18.0/'

        url = graph_url + str(self.accountID) + '/media'
        param = dict()
        param['access_token'] = self.accessToken
        param['caption'] = '''Best Reddit Stories #aita #reddit #amitheasshole #yta #nta #esh #redditstories #redditposts #redditmeme #rslash #redditadvice #advice #EM #daily #redditopinions'''
        param['media_type'] = 'REELS'
        param['share_to_feed'] = 'true'
        param['thumb_offset'] = '2000'
        param['video_url'] = f'https://wwz4-polly-bucket.s3.amazonaws.com/TTS/{file}'
        response = requests.post(url, params=param)
        print("\n response", response.content)
        response = response.json()
        contentID = response["id"]

        param = dict()
        param['access_token'] = self.accessToken
        param['fields'] = 'status_code'
        url = graph_url + str(contentID)
        while requests.get(url, params=param).json()['status_code'] != 'FINISHED':
            time.sleep(5)

        # wait for reel to finish upploading
        time.sleep(8)
        url = graph_url + str(self.accountID) + '/media_publish'
        param = dict()
        param['access_token'] = self.accessToken
        param['creation_id'] = contentID
        requests.post(URL, params=param)

    def uploadVideos(self, path='/Users/vincentzhou/Documents/RedditBot/'):
        vids = []
        for filename in os.listdir(f'{path}src/files'):
            file_path = os.path.join(f'{path}src/files', filename)
            if os.path.isfile(file_path) and os.path.splitext(filename)[0][:3] == 'TTS' and os.path.splitext(filename)[-1].lower() == '.mp4':
                vids.append({'path': f'src/files/{filename}',
                            'description': self.title + " #fyp #reddit #redditstories #redditreadings #aita #tifu #subwaysurfers #askreddit #minecraftparkour"})
                # self.s3_client.upload_file(
                #     f'src/files/{filename}', 'wwz4-polly-bucket', f'TTS/{filename}')

                # waiter = self.s3_client.get_waiter('object_exists')
                # waiter.wait(
                #     Bucket='wwz4-polly-bucket',
                #     Key=f'TTS/{filename}')
                # self.post_reel(filename)

        auth = AuthBackend(cookies='src/cookies.txt')
        upload_videos(videos=vids, auth=auth, headless=True)

    def createParts(self):
        chars_per_video = 3000
        parts = int(len(self.text) / chars_per_video) + 1
        characters_per_part = int(len(self.text)/parts)

        # self.createTTS(self.title, 'src/files/TTS/title.mp3')
        print("Created TTS for Title")
        self.titleLength = self.getAudioDuration('src/files/TTS/title.mp3')

        # for part in range(parts):
        #     print(f'Creating Audio Part{part}')
        #     self.createTTS(self.text[part*characters_per_part:(part+1) *
        #                              characters_per_part], f'src/files/TTS/audio{part}.mp3')

        #     ffmpeg.concat(ffmpeg.input('src/files/TTS/title.mp3'), ffmpeg.input(
        #         f'src/files/TTS/audio{part}.mp3'), v=0, a=1).output(f'src/files/TTS/audio{part}c.mp3').run(overwrite_output=True)

        for part in range(parts):
            # print(f'Creating Captions Part{part}')
            # segments, _ = self.model.transcribe(
            #     f"src/files/TTS/audio{part}c.mp3",
            #     word_timestamps=True,
            # )
            # print('after breaking')

            # with open(f"src/files/subtitles/subtitles{part}.srt", "w") as f:
            #     words = []
            #     for segment in segments:
            #         for word in segment.words:
            #             if word.start >= self.titleLength:
            #                 if not words or words[-1][1] - words[-1][0] >= 0.5:
            #                     words.append(
            #                         [word.start, word.end, [profanity.censor(word.word.strip(" "))]])
            #                 else:
            #                     words[-1][1] = word.end
            #                     words[-1][2].append(
            #                         profanity.censor(word.word.strip(" ")))
            #     for i, phrase in enumerate(words):
            #         f.write(
            #             f'{i+1}\n{self.formatSeconds(max(0,phrase[0] - 0.2))} --> {self.formatSeconds(phrase[1]-0.2)}\n{" ".join(phrase[2])}\n\n')

            print(f'Stitching Everything Together Part{part}')
            self.formatVideo('src/files/background/parkour.mp4',
                             f'src/files/TTS{part}.mp4', f'src/files/subtitles/subtitles{part}.srt', f'src/files/TTS/audio{part}c.mp3', part+1)


URL = 'https://www.reddit.com/r/pettyrevenge/comments/qr60h1/you_dont_like_your_boyfriend_seeing_me_braless_in/'
h = CreateTTS(URL)
part = 0
# h.removeExtraneousTTS()
h.createParts()
# h.uploadVideos()
