"""Finds clicks in a wave-file and writes their timestamps, sample index and other data to a CSV file."""
import argparse
import csv
import logging

from pathlib import Path

import numpy as np
from scipy.io import wavfile  # type: ignore
from scipy.signal import find_peaks, butter, filtfilt, stft  # type: ignore

from matplotlib import pyplot as plt


def bandpass_filter(data: np.ndarray, lowcut: float, highcut: float, fs: float, order: int = 5) -> np.ndarray:
    """Applies a bandpass filter to the data.

    Parameters
    ----------
    data : np.ndarray
        The data to filter.
    lowcut : float
        Lowcut frequency for the filter.
    highcut : float
        Highcut frequency for the filter.
    fs : float
        Sampling frequency of the data.
    order : int
        Order of the filter.

    Returns
    -------
    np.ndarray
        The filtered data.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

def find_clicks(
        wav_file: Path,
        threshold: float,
        out_dir: Path,
        distance: int = 50,
        normalize: bool = True,
        filter: bool = True,
        lowcut: float = 3500,
        highcut: float = 16000,
        order: int = 5,
        prominence: float = 8):
    """Finds clicks in a wave-file and writes their timestamps, sample index and other data to a CSV file.

    Parameters
    ----------
    wav_file : str
        Path to the wave-file.
    threshold : float
        Threshold for the click detection.
    out_dir : str
        Path to the output CSV file.
    distance : int
        Minimum distance between peaks.
    normalize : bool
        Whether to normalize the wave-file before finding the clicks.
    filter : bool
        Whether to filter the wave-file before finding the clicks.
    lowcut : float
        Lowcut frequency for the filter.
    highcut : float
        Highcut frequency for the filter.
    order : int
        Order of the filter.
    prominence : float
        Prominence of the peaks.
    """
    # Load the wave-file
    sample_rate, data = wavfile.read(wav_file)

    logging.info(f'Loaded wave-file {wav_file} with sample rate {sample_rate} and {data.shape[0]} samples.')

    # if we have more than one channel, take the average
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    if filter:
        data = bandpass_filter(data, lowcut, highcut, sample_rate, order)

    if normalize:
        data = data / np.max(np.abs(data))
    
    # save the filtered and normalized data
    out_file = out_dir / f'{wav_file.stem}_filtered_normalized.wav'
    wavfile.write(out_file, sample_rate, data)
    # apply short-time Fourier transform
    f, t, Zxx = stft(data, fs=sample_rate, nperseg=int(0.01*sample_rate))

    amp_spec = np.abs(Zxx)

    # plot the amplitude spectrogram
    plt.pcolormesh(t, f, amp_spec, shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.title('Amplitude spectrogram')
    plt.colorbar()
    plt.savefig(out_dir / f'{wav_file.stem}_amp_spec.png')


    print(np.max(amp_spec))
    thresh = threshold * np.max(amp_spec)
    mask = amp_spec > thresh
    ts = np.sum(mask, axis=0)

    logging.info(f'Threshold: {thresh}')

    # Plot the time series
    plt.figure(figsize=(12, 6))
    plt.plot(t, ts, label='Summed Frequency Bins')
    plt.xlabel('Time [sec]')
    plt.ylabel('Summed Magnitude')
    plt.title('Summed Magnitude Time Series')
    plt.savefig(out_dir / f'{wav_file.stem}_time_series.png')

    

    # Find the clicks
    peaks, peak_props = find_peaks(ts, prominence=prominence, distance=distance)
    logging.info(f'Found {len(peaks)} clicks.')

    # Write the clicks to a CSV file
    out_file = out_dir / f'{wav_file.stem}_clicks.csv'
    with open(out_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'sample_index', 'frequency', 'amplitude', 'prominence', 'left_base', 'right_base'])
        for i, peak in enumerate(peaks):
            timestamp = t[peak]
            freq = f[np.argmax(amp_spec[:, peak])]
            amp = np.max(amp_spec[:, peak])
            writer.writerow([timestamp, peak, freq, amp, peak_props['prominences'][i], peak_props['left_bases'][i], peak_props['right_bases'][i]])

    logging.info(f'Wrote clicks to {out_file}.')




def main():
    parser = argparse.ArgumentParser(description='Find clicks in a wave-file and write their timestamps, sample index and other data to a CSV file.')
    parser.add_argument('wav_file', type=Path, help='Path to the wave-file.')
    parser.add_argument('--out-dir', '-o', type=Path, default=Path('./data'), help='Path to the output CSV file.')
    parser.add_argument('--threshold', '-t', type=float, default=0.2, help='Threshold for the click detection.')
    parser.add_argument('--prominence', '-p', type=float, default=10, help='Prominence of the peaks.')
    parser.add_argument('--distance', '-d', type=int, default=50, help='Minimum distance between peaks.')
    parser.add_argument('--lowcut', '-l', type=float, default=5500, help='Lowcut frequency for the filter.')
    parser.add_argument('--highcut', '-u', type=float, default=20000, help='Highcut frequency for the filter.')
    parser.add_argument('--order', '-r', type=int, default=5, help='Order of the filter.')
    parser.add_argument('--no-filter', '-f', action='store_true', default=False, help='Whether to filter the wave-file before finding the clicks.')
    parser.add_argument('--no-normalize', '-n', action='store_true', default=False, help='Whether to normalize the wave-file before finding the clicks.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    normalize = not args.no_normalize
    filter = not args.no_filter

    if not args.wav_file.exists():
        raise FileNotFoundError(f'Wave-file {args.wav_file} not found.')
    
    if not args.out_dir.exists() or not args.out_dir.is_dir():
        raise FileNotFoundError(f'Output directory {args.out_dir} not found.')

    find_clicks(
        args.wav_file,
        args.threshold,
        args.out_dir,
        distance=args.distance,
        normalize=normalize,
        filter=filter,
        lowcut=args.lowcut,
        highcut=args.highcut,
        order=args.order,
        prominence=args.prominence
    )


if __name__ == '__main__':
    main()
