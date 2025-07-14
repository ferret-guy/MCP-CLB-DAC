import time

import serial
import numpy as np
from pathlib import Path

from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from scipy.io import wavfile
from scipy.signal import resample_poly
from tqdm import tqdm


def pcm_cast(a: np.ndarray, dt: np.dtype) -> np.ndarray:
    if a.dtype == dt:
        return a.copy()
    f = a.astype(np.float32)
    if np.issubdtype(a.dtype, np.signedinteger):
        f /= np.iinfo(a.dtype).max
    f = np.clip(f, -1, 1)
    i = np.iinfo(dt)
    return np.round((f + 1) * (i.max - i.min) / 2 + i.min).astype(dt)

def send_resampled_wav_16bit(
    wav_path: str | Path,
    port: str,
    baud: int = 500_000,
    target_rate: int = 25_000,
    start_sec: float = 0.0,
):
    rate, data = wavfile.read(wav_path)
    
    print(f"Loaded {wav_path} @ {rate:,} Hz, shape={data.shape}, dtype={data.dtype}")

    if data.ndim > 1:
        data = data.mean(axis=1).astype(data.dtype)  # Convert to mono

    # Trim start
    start_index = int(start_sec * rate)
    if start_index >= len(data):
        raise ValueError("start_sec exceeds audio duration")
    data = data[start_index:]

    # Resample
    print(f"Resampling from {rate} to {target_rate}")
    n = int(round(len(data) * target_rate / rate))
    f = interp1d(np.arange(len(data)), data, axis=0, kind='linear')
    resampled = f(np.linspace(0, len(data) - 1, n)).astype(data.dtype)

    resampled = pcm_cast(resampled, np.uint16)
    print(f"Resampled to {len(resampled)} samples")

    byte_data = resampled.byteswap().newbyteorder().tobytes()

    ser = serial.Serial(port=port, baudrate=baud)
    try:
        with tqdm(total=len(byte_data), unit="B", ncols=80, desc="TX") as bar:
            chunk_size = 1024  # bytes
            for i in range(0, len(byte_data), chunk_size):
                chunk = byte_data[i:i + chunk_size]
                ser.write(chunk[::])
                bar.update(len(chunk))
                if len(chunk) >= 2:
                    last_sample = int.from_bytes(chunk[-2:], byteorder='little', signed=True)
                    bar.set_postfix(sample=last_sample)
    finally:
        ser.close()
        print(f"Done: {len(byte_data):,} bytes sent.")

if __name__ == "__main__":
    while True:
        send_resampled_wav_16bit(
            wav_path="Noisestorm - Crab Rave [Monstercat Release] [LDU_Txk06tM].wav",
            port="COM13",
            start_sec=53.0
        )

