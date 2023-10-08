from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from better_profanity import profanity
from io import BytesIO
import textwrap
# import subprocess
# import ffmpeg


def create_thumbnail(URL='https://www.reddit.com/r/AmItheAsshole/comments/172d1k2/aita_for_insulting_my_sort_of_mil_after_she.json'):

    # width, height = ffmpeg.probe(input_file)['streams'][0]['width'], ffmpeg.probe(
    #     input_file)['streams'][0]['height']

    # if width > 9/16 * height:
    #     w = '9/16*in_h'
    #     h = 'in_h'
    #     x = '1/2*in_w - 0.5*9/16*in_h'
    # else:
    #     w = 'in_w'
    #     h = '16/9 * in_w'
    #     x = '0'

    # command = ["ffmpeg", "-i", input_file, "-ss",
    #            "00:00:01", "-filter:v", f"crop={w}:{h}:{x}:0", "-frames:v", "1", output_file]

    # # Execute the command
    # subprocess.call(command)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }

    response = requests.get(URL, headers=headers)
    res_json = response.json()

    post, comments = res_json
    postData = post['data']['children'][0]['data']

    title = postData['title']
    author = postData['author']
    subreddit = postData['subreddit_name_prefixed']
    score = postData['score']
    text = profanity.censor(postData['selftext'])
    size = (768*2, 325 + 72 * (max(0, len(textwrap.wrap(title, width=36))-2)))

    background = Image.new(
        "RGBA",
        size,
        color=(255, 255, 255, 0))

    if author != "[deleted]":
        with BytesIO() as b:
            author_response = requests.get(
                f"https://www.reddit.com/user/{author}/about.json", headers=headers)
            author_json = author_response.json()
            author = f'u/{author}'
            if author_json['data']['snoovatar_img']:
                avatar_data = BytesIO(requests.get(
                    author_json['data']['snoovatar_img']).content)
            else:
                avatar_data = BytesIO(requests.get(
                    author_json['data']['icon_img']).content)
    else:
        avatar_data = "src/files/default.png"

    img = Image.open(avatar_data)

    back_draw = ImageDraw.Draw(background)
    back_draw.rounded_rectangle(((0, 0), size), 60, fill="white")
    back_draw.rounded_rectangle(
        ((265, 80, 1490, 140)), 4, fill=(252, 222, 222))
    back_draw.fontmode = "L"

    upvote = Image.open('src/files/upvote.png')
    downvote = Image.open('src/files/downvote.png')

    background.paste(upvote, (42, 238), upvote)
    background.paste(downvote, (206, 242), downvote)

    font = ImageFont.truetype(
        "src/files/FreeSansBold.ttf", size=44)
    back_draw.text((270, 16), author, font=font, fill="black")

    back_draw.text((270, 80), subreddit, font=font, fill="gray")

    awards = Image.open('src/files/awards.png')

    awards = awards.resize(
        (int(187*1.5), int(40*1.5)), resample=Image.Resampling.LANCZOS)
    background.paste(awards, (1200, 80), awards)

    font = ImageFont.truetype(
        "src/files/FreeSansBold.ttf", size=72)
    back_draw.text((270, 140), '\n'.join(textwrap.wrap(
        title, width=36)), font=font, fill="black")

    # Create pfp
    bigsize = (img.size[0] * 3, img.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(img.size, resample=Image.Resampling.LANCZOS)
    img.putalpha(mask)
    img = img.resize((220, 220))
    background.paste(img, (20, 10), mask=img)

    background.show()


create_thumbnail()
