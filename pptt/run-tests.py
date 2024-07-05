
import argparse
import asyncio
from pathlib import Path
import sys
import os
# Add the parent directory to the path so we can import pptt
sys.path.append(str(Path(__file__).resolve().parents[1]))
from pptt.config import set_psychopy_prefs
set_psychopy_prefs()
from psychopy import logging  # type: ignore
from psychopy.core import Clock  # type: ignore



def parse_args():
    photodiode_locations = ['tl', 'tr', 'bl', 'br']
    parser = argparse.ArgumentParser(description='Run PsychoPy timing tests.')
    parser.add_argument('--list-devices', '-l', action='store_true', help='List available audio devices (speakers and microphones).')
    parser.add_argument('--speaker', '-s', type=int, help='Name of the speaker device to use.')
    parser.add_argument('--speaker-volume', '-v', default=0.5, type=float, help='Volume of the speaker device to use.')
    parser.add_argument('--speaker-sample-rate', '-r', default=44100, type=int, help='Latency of the speaker device to use.')
    parser.add_argument('--microphone', '-m', type=int, help='Name of the microphone device to use.')
    parser.add_argument('--microphone-channels', '-c', type=int, default=1, help='Number of channels of the microphone device to use.')
    parser.add_argument('--microphone-sample-rate', '-z', type=int, default=44100, help='Sample rate of the microphone device to use.')
    parser.add_argument('--num-iter', '-n', type=int, default=10000, help='Number of iterations (~= frames) to run the test.')
    parser.add_argument('--trigger-every', '-t', type=int, default=100, help='Trigger high every N iterations.')
    parser.add_argument('--port-addr', '-p', type=lambda x: int(x, 0), default=0x378, help='Address of the parallel port.')
    parser.add_argument('--screen-res', '-x', type=lambda x: tuple(map(int, x.split(','))), default=(2560, 1440), help='Screen resolution (width, height).')
    parser.add_argument('--out-dir', '-o', type=Path, default=Path('data'), help='Output directory for data files and recordings.')
    parser.add_argument('--photodiode-location', '-d', type=str, default='br', choices=photodiode_locations, help='Location of the photodiode.')

    return parser.parse_args()


async def main():
    

    args = parse_args()
    if args.list_devices:
        from psychopy.hardware.manager import getDeviceManager, DeviceManager  # type: ignore
        device_manager: DeviceManager = getDeviceManager()  # type: ignore
        print('Available audio devices:')
        print('Speakers:')
        for device in device_manager.getAvailableDevices('psychopy.hardware.speaker.SpeakerDevice'):
            print(f'{device["index"]:>10,g}: {device["deviceName"]}')
        print('Microphones:')
        for device in device_manager.getAvailableDevices('psychopy.hardware.microphone.MicrophoneDevice'):
            print(f'{device["index"]:>10,g}: {device["deviceName"]}')
        return

    # add lib dir to DLL search path
    with os.add_dll_directory(str(Path(__file__).resolve().parents[1] / 'lib')):
        from pptt.exps.animated_square import animated_square

        studyClock = Clock()
        logging.root.format="{t} \t{levelname} \t{message}"
        logging.setDefaultClock(studyClock)
        
        logger = logging.LogFile(args.out_dir / 'animated_square.log', level=logging.INFO, filemode='a')
        logging.info('Starting animated square test')
        await animated_square(
            num_iter=args.num_iter,
            trigger_every=args.trigger_every,
            port_addr=args.port_addr,
            speaker_device=args.speaker,
            speaker_volume=args.speaker_volume,
            speaker_sr=args.speaker_sample_rate,
            microphone_device=args.microphone,
            microphone_channels=args.microphone_channels,
            microphone_sr=args.microphone_sample_rate,
            data_dir=args.out_dir,
            res=args.screen_res,
            trigger_square_pos=args.photodiode_location
        )


if __name__ == '__main__':
    asyncio.run(main())
