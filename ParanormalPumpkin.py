from dotenv import load_dotenv
import os
import sounddevice as sd
import soundfile as sf
import whisper
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play
import shutil
import subprocess

# --- OpenAI Setup --- 
#Loads the key from a seperate file for security
load_dotenv("key.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#*************************************************
#*    Recording Audio & Turning it into text     *  
#*************************************************

#Load Whisper model used to do speech to text
#"tiny" is faster, while ""base" is more accurate
model = whisper.load_model("base")

# Record a short audio from the mic
def record_audio(filename='input.wav', seconds=5, samplerate=16000):

    # Locks the device to the yeti nano (#5)
    sd.default.device = (5, None)

    # Records audio from the user and saves it as input.wav
    input("Mr.Computer: Press Enter to begin the recoding sir")
    print("Mr.Computer: Recording Now Sir...")
    audio = sd.rec(int(seconds*samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    sf.write(filename, audio, samplerate)
    print("Mr. Computer: Recording finished sir, it is saved as ", filename)
    return filename


def transcribe_audio(filename='input.wav'):
    result = model.transcribe(filename, fp16=False)
    return result.get("text", "").strip()


#*************************************************
#*    Sending The Message To The AI Overlords    *  
#*************************************************

# The prompt that will be sent to the LLM to give it context on what it is
pumpkin_prompt = "You are an enchanted Halloween pumpkin named Donald Trumpkin. A pumpkin haunted by the spirit of Donald Trump. Reply with an exaggerated version of Donald Trump's personality. Reply briefly (35 words or less), keep it spooky, and pg-13 rating only"
def ask_Ai(user_text: str) -> str:
    if not user_text.strip():
        return ""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # Can use 3.5 (cheaper, but less smarter)
        messages=[
            {"role": "system",
             "content":pumpkin_prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=0.8,
        max_tokens=120
    )
    return resp.choices[0].message.content.strip()


#*************************************************
#*    Turning The Ai's Message Into Speech       *  
#*************************************************

def itsalive(text: str, out_path="reply.mp3", voice="alloy"):
    if not text.strip():
        return None
    # Stream directly to a file (defaults to MP3)
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
    ) as response:
        response.stream_to_file(out_path)
    return out_path


def play_now(path: str):
    """
    Plays Audio witthout using pydub's temp files
    Prefers ffplay, which is part of ffmpeg. 
    Falls back to winsound (wav only)
    """

    ffplay = shutil.which("ffplay")
    if ffplay:
        # No window, auto exit when done
        subprocess.run([ffplay, "-nodisp", "-autoexit", "-loglevel", "quiet", path], check=False)
        return
    
    # Fallback (Convert to WAV & Play with Winsound)
    import winsound
    wav_path = "reply_play.wav"
    AudioSegment.from_file(path).export(wav_path, format="wav")
    winsound.PlaySound(wav_path, winsound.SND_FILENAME)


#--- MAIN ---

if __name__ == "__main__":
    
    cont = True
    while cont == True:
        wav_file = record_audio()
        text = transcribe_audio(wav_file)
        print("Mr. Computer: Sir, I do believe you said:\n\n", text if text else "Well...It seems nothing at all sir")
        reply = ask_Ai(text)
        print("\n\nEnchanted Pumpkin: ", reply if reply else "Mr. Computer: It seems there has been a fuckup somewhere sir...")

        audio_file = itsalive(reply, out_path="reply.mp3", voice="verse")
        if audio_file and os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
            print("\nMr.Computer: Speaking the reply for you now sir...")
            play_now(audio_file)
        else:
            print("Mr. Computer: Audio not produced sir.")
        cont_answer = input("\nMr. Computer: Would you like to go again sir? (y/n)")
        if cont_answer.lower() == "n":
            cont = False
        else:
            cont = True 


    input("\nPress Enter to Exit...")