"""Free local Kokoro narration, one file per precisely timed visual beat."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.request

os.environ.setdefault('OMP_NUM_THREADS', '4')
import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts' / 'video'
MODELS = OUT / 'models'
BASE = 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/'


class LocalNarrator(Kokoro):
    def _create_audio(self, phonemes, voice, speed):
        # The 0.4.9 wrapper casts speed to int32 for this float-input export.
        # Build the three ONNX inputs explicitly so .96 is never truncated to 0.
        ids = self.tokenizer.tokenize(phonemes)
        assert len(ids) <= 510, 'Split narration into shorter beats'
        feeds = {'input_ids': np.array([[0, *ids, 0]], dtype=np.int64),
                 'style': np.asarray(voice[len(ids)], dtype=np.float32),
                 'speed': np.array([speed], dtype=np.float32)}
        audio = self.sess.run(None, feeds)[0].reshape(-1)
        return audio, 24000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', action='store_true')
    parser.add_argument('--voice', default='af_heart')
    args = parser.parse_args()
    MODELS.mkdir(parents=True, exist_ok=True)
    for name in ['kokoro-v1.0.onnx', 'voices-v1.0.bin']:
        if not (MODELS / name).exists():
            print(f'Downloading {name}', flush=True)
            partial = MODELS / (name + '.partial')
            urllib.request.urlretrieve(BASE + name, partial)
            partial.replace(MODELS / name)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(MODELS / 'kokoro-v1.0.onnx'),
                                   sess_options=options, providers=['CPUExecutionProvider'])
    engine = LocalNarrator.from_session(session, str(MODELS / 'voices-v1.0.bin'))
    target = OUT / ('voice-samples' if args.samples else 'narration-v2')
    target.mkdir(exist_ok=True)
    records = []
    if args.samples:
        work = [(voice, 'One reading. More than one explanation. What should we measure next?', voice, .96)
                for voice in ['af_heart', 'af_bella', 'bf_emma', 'am_fenrir']]
    else:
        story = json.loads((ROOT / 'video' / 'storyboard.json').read_text(encoding='utf-8'))
        work = [(f"{s['id']}-{b['key']}", b['text'], args.voice, b.get('speed', .96))
                for s in story for b in s['beats']]
    for key, text, voice, speed in work:
        signature = hashlib.sha256(json.dumps([text, voice, speed, 'kokoro-1.0']).encode()).hexdigest()
        wav = target / f'{key}.wav'
        stamp = target / f'{key}.json'
        if wav.exists() and stamp.exists() and json.loads(stamp.read_text())['signature'] == signature:
            record = json.loads(stamp.read_text())
        else:
            audio, rate = engine.create(text, voice=voice, speed=speed,
                                        lang='en-gb' if voice.startswith('b') else 'en-us')
            audio = np.asarray(audio)
            assert np.isfinite(audio).all() and len(audio) > rate * .3, key
            assert np.max(np.abs(audio)) > .02, f'Silent speech: {key}'
            sf.write(str(wav), audio, rate, subtype='PCM_16')
            record = {'key': key, 'text': text, 'voice': voice, 'speed': speed,
                      'seconds': len(audio) / rate, 'sample_rate': rate,
                      'signature': signature, 'path': wav.name}
            stamp.write_text(json.dumps(record, indent=2), encoding='utf-8')
        records.append(record)
        print(f"{key}: {record['seconds']:.2f}s ({voice})", flush=True)
    (target / 'manifest.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    provenance = {'engine': 'Kokoro-82M v1.0 / kokoro-onnx 0.4.9', 'voice': args.voice,
                  'inference': 'Local CPU', 'model_license': 'Apache-2.0',
                  'runtime_license': 'MIT', 'model_url': 'https://huggingface.co/hexgrad/Kokoro-82M',
                  'download_base': BASE,
                  'model_files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in MODELS.iterdir() if p.suffix in ('.onnx', '.bin')}}
    (OUT / 'voice-provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
