# RedditTTS

Python script enabling a user to automatically create, edit, and post videos on Tiktok, Instagram Reels, and YouTube. 
Scrapes Reddit posts to create a script. Uses Amazon Polly to transcribe text and FFmpeg and PIL to create a video based on a given background.
## Setup

We use python poetry for dependency management. Once you install python-poetry just run 

```sh
poetry install
```

To view environment info to add to vscode use

```sh
poetry env info
```

## Running

### Local

```sh
poetry shell
python -m grab
```
