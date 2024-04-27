import tempfile
from typing import Generator

import click
import numpy as np
import pydub
import pytube
import torch
from whisper import load_model, transcribe

print("Loading model...")

SAMPLE_RATE = 16000
CHUNK_DURATION = 6
CHUNKSIZE = SAMPLE_RATE * CHUNK_DURATION
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL = "large" if torch.cuda.is_available() else "small"
model = load_model(MODEL).to(DEVICE)

print(f"Using model: {MODEL} on device: {DEVICE}")


def transcribe_youtube(url: str) -> Generator[str, None, None]:
    yt = pytube.YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    with tempfile.TemporaryDirectory() as tmpdir:
        stream.download(output_path=tmpdir)
        audio_file_path = f"{tmpdir}/{stream.default_filename}"
        audio = pydub.AudioSegment.from_file(audio_file_path)
        audio = audio.set_channels(1).set_frame_rate(SAMPLE_RATE)
        audio_samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / (
            2**15
        )
        for i in range(0, len(audio_samples), CHUNKSIZE):
            chunk = audio_samples[i : i + CHUNKSIZE]

            if len(chunk) < CHUNKSIZE:
                chunk = np.pad(chunk, (0, CHUNKSIZE - len(chunk)), mode="constant")
            text = transcribe(model, chunk)  # type: ignore
            yield text["text"]  # type: ignore


@click.group()
def cli():
    pass


@cli.command()
@click.argument("url")
def main(url: str) -> None:
    for i in transcribe_youtube(url):
        print(i, end="", flush=True)


if __name__ == "__main__":
    cli()
