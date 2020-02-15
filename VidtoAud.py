import moviepy.editor as mp

clip = mp.VideoFileClip("videoname.m4v").subclip(0, 50)
clip.audio.write_audiofile("audioname.wav")

# Audio will be in current directory
