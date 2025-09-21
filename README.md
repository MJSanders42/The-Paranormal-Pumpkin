The Paranormal Pumpkin 

The Pumpkin Records the speech in the mic (WAV) --> Use Whisper to turn it into text --> Send that text to the LLM (OpenAi chat completions) --> Send reply to OpenAI TTS to have it turned into a mp3 --> Play reply.mp3 on speaker

Speech-to-Text: Whisper
LLM: OpenAI Chat Completions
Text-to-Speech: OpenAI TTS

(!Note!)--Currently it is hard coded in to use the microphone at index 5, which on my computer correlates to my external mic, yours will most likely differ and you will have to alter the index number on line #30 to have the audio recorded correcly
