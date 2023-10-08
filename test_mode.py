# import torch
# from TTS.api import TTS

# # Get device
# device = "cuda" if torch.cuda.is_available() else "cpu"

# # List available 🐸TTS models and choose the first one
# model_name = TTS().list_models()[0]

# print(model_name)
# # Init TTS
# tts = TTS("tts_models/en/vctk/vits").to(device)

# print(tts.speakers)

# # Run TTS
# # ❗ Since this model is multi-speaker and multi-lingual, we must set the target speaker and the language
# # Text to speech with a numpy output

# # Text to speech to a file
# for i in [0, 2, 4, 6, 17, 20, 25, 28, 33, 48, 93]:
#     tts.tts_to_file(text='''Using a throwaway because he probably knows my main and I don't want him to know I know yet. This also technically started a few days ago but it's been stuck in my head since and I need to get my thoughts out. When we met and the entire 3 years we dated before we married, I was always firm about not wanting kids. My husband told me that his stance on kids was along the lines of "kind of undecided, but overall not a good idea". Always said he used to want kids but changed his mind later in life.''',
#                     speaker=tts.speakers[i], file_path=f"out/output_{i}.wav")


from src.grab import CreateTTS

tts = CreateTTS()
tts.createParts()
