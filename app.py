import os
import torch
import soundfile as sf
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from transformers import AutoProcessor, BarkModel
import uvicorn

# Inizializza il modello e il processore.
# BARK_MODEL permette di scegliere "suno/bark-small" in CI per ridurre tempi/RAM.
model_name = os.environ.get("BARK_MODEL", "suno/bark")
processor = AutoProcessor.from_pretrained(model_name)
model = BarkModel.from_pretrained(model_name)

# Se la GPU è disponibile, usa la GPU, altrimenti usa la CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

app = FastAPI()

# Definisci un modello Pydantic per il corpo della richiesta
class TextRequest(BaseModel):
    text: str

@app.post("/generate-audio/")
async def generate_audio_endpoint(request: TextRequest):
    text = request.text  # Estrai il testo dal corpo della richiesta

    # Imposta il preset della voce
    voice_preset = "v2/it_speaker_1"  # Puoi sostituirlo con il preset in italiano

    # Prepara il testo da convertire in audio
    inputs = processor(text, voice_preset=voice_preset, return_tensors="pt")

    # Sposta gli input sulla GPU (se disponibile)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    try:
        # Genera l'audio usando la GPU (se disponibile)
        audio_array = model.generate(**inputs)

        # Sposta l'audio sulla CPU e convertilo in numpy
        audio_array = audio_array.cpu().numpy().squeeze()

        # Salva l'audio come file .wav
        audio_file = "generated_audio.wav"
        sample_rate = model.generation_config.sample_rate
        sf.write(audio_file, audio_array, sample_rate)

    except Exception as e:
        return {"error": str(e)}

    # Restituisci il file audio generato
    return FileResponse(audio_file, media_type="audio/wav", headers={"Content-Disposition": f"attachment; filename={audio_file.split('/')[-1]}"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)