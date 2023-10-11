from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import requests
from better_profanity import profanity
from io import BytesIO
import textwrap
# import subprocess
# import ffmpeg


def dropShadow(image, offset=(-8, -8), background=(255, 255, 255, 0), shadow=(0, 0, 0),
               border=8, iterations=10):
    """
    Add a gaussian blur drop shadow to an image.  

    image       - The image to overlay on top of the shadow.
    offset      - Offset of the shadow from the image as an (x,y) tuple.  Can be
                  positive or negative.
    background  - Background colour behind the image.
    shadow      - Shadow colour (darkness).
    border      - Width of the border around the image.  This must be wide
                  enough to account for the blurring of the shadow.
    iterations  - Number of times to apply the filter.  More iterations 
                  produce a more blurred shadow, but increase processing time.
    """

    # Create the backdrop image -- a box in the background colour with a
    # shadow on it.
    back = Image.new(
        image.mode, (image.size[0] + 4*border, image.size[1] + 4 * border), background)

    # Place the shadow, taking into account the offset from the image
    shad = Image.new(
        image.mode, (image.size[0]+4*border, image.size[1] + 4*border))

    back_draw = ImageDraw.Draw(back)
    back_draw.rounded_rectangle(
        ((border*2, border*2), (image.size[0]+2*border, image.size[1]+2*border)), 30, fill=shadow)
    # Apply the filter to blur the edges of the shadow.  Since a small kernel
    # is used, the filter must be applied repeatedly to get a decent blur.
    for _ in range(iterations):
        back = back.filter(ImageFilter.GaussianBlur)

    # Paste the input image onto the shadow backdrop
    back.paste(image, (border*2, border*2), image)
    return back


def create_thumbnail(URL, w, h, part):
    URL = URL.strip("/.json") + ".json"

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

    fontFile = "/Users/vincentzhou/Documents/RedditBot/src/files/font/Helvetica LT Std Bold.otf"

    title = postData['title']
    author = postData['author']
    subreddit = postData['subreddit_name_prefixed']
    score = postData['score']
    text = profanity.censor(postData['selftext'])

    width = 33
    titleWrap = textwrap.wrap(
        title + f' Part {part}', width=width)

    size = (768*2, 365 + 72 *
            (max(0, len(titleWrap))-2))

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
            if 'snoovatar_img' in author_json['data'] and author_json['data']['snoovatar_img'] != '':
                avatar_data = BytesIO(requests.get(
                    author_json['data']['snoovatar_img']).content)
            else:
                avatar_data = "src/files/images/default.png"
    else:
        avatar_data = "src/files/images/default.png"

    img = Image.open(avatar_data)

    back_draw = ImageDraw.Draw(background)
    back_draw.rounded_rectangle(((0, 0), size), 60, fill="white")

    back_draw.rounded_rectangle(
        ((265, 86, 1490, 150)), 4, fill=(152, 206, 237))
    back_draw.fontmode = "L"

    upvote = Image.open('src/files/images/upvote.png').convert("RGBA")
    upvote = upvote.resize((80, 80))
    downvote = Image.open('src/files/images/downvote.png').convert("RGBA")
    downvote = downvote.resize((80, 80))

    # background.paste(upvote, (10, 238), upvote)
    # background.paste(downvote, (170, 238), downvote)

    # font = ImageFont.truetype(fontFile, size=36)
    # back_draw.text((93, 255), str('%.1fK' %
    #                (score / 1000)) if score < 10000 else str('%2dK' %
    #                (score / 1000)), font=font, fill="black")

    font = ImageFont.truetype(fontFile, size=44)
    back_draw.text((270, 26), author, font=font, fill="black")

    font = ImageFont.truetype(fontFile, size=38)
    back_draw.text((1050, 32), '@automatedredditstories',
                   font=font, fill="gray")

    back_draw.text((270, 104), subreddit, font=font, fill="black")

    awards = Image.open('src/files/images/awards.png')

    awards = awards.resize(
        (int(187*1.5), int(40*1.5)), resample=Image.Resampling.LANCZOS)
    background.paste(awards, (1200, 88), awards)

    font = ImageFont.truetype(fontFile, size=72)
    text = textwrap.wrap(
        title + f' Part {part}', width=width)
    for idx, t in enumerate(titleWrap):
        back_draw.text((270, 175 + idx*72), t, font=font, fill="black")

    # Create pfp
    bigsize = (img.size[0] * 3, img.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(img.size, resample=Image.Resampling.LANCZOS)
    img.putalpha(mask)
    img = img.resize((200, 200))
    background.paste(img, (30, 20), mask=img)

    template = Image.new('RGBA', (936, 1664), (200, 255, 255, 0))
    background = background.resize(
        (background.size[0]//2, background.size[1]//2), resample=Image.Resampling.LANCZOS)
    background = dropShadow(background)
    template.paste(background, (82, 717), background)
    template = template.resize(
        (w, h), resample=Image.Resampling.LANCZOS)
    template.save('src/files/images/title.png')

    print("Created Title Image")


# create_thumbnail(
#     'https://www.reddit.com/r/AmItheAsshole/comments/173a3e0/aita_for_giving_my_daughter_a_name_my_grandma/', 1)
