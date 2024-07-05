# PsychoPy timing and latency test

This python app tests latency of various psychopy features including:

- sound input/output
- mouse clicks
- screen latency
- parallel port triggers

## Required hardware

Right now, the script requires the following (although it is easily adapted to not use any of the components):

- A mic in device
- A parallel port to send triggers (can be adapted to serial)
- A sound output device

For the analysis, it is based on BrainProducts EEG recordings, and expects a StimTrak channel (arbitrary triggers) and a photodiode channel (directly connected to an AUX port).

## How to use

For easiest setup, use an Anaconda / Miniconda environment. You can create one with the following command:

```bash
conda create env -f environment.yml
```

Then, activate the environment:

```bash
conda activate PsychoPy-timings
```

For development, you can install the optional dependencies:

```bash
pip install -r requirements-dev.txt
```

Then, run the script:

```bash
python pptt/run-tests.py --help
```

```text
usage: run-tests.py [-h] [--list-devices] [--speaker SPEAKER] [--speaker-volume SPEAKER_VOLUME] [--speaker-sample-rate SPEAKER_SAMPLE_RATE] [--microphone MICROPHONE] [--microphone-channels MICROPHONE_CHANNELS]
                    [--microphone-sample-rate MICROPHONE_SAMPLE_RATE] [--num-iter NUM_ITER] [--trigger-every TRIGGER_EVERY] [--port-addr PORT_ADDR] [--screen-res SCREEN_RES] [--out-dir OUT_DIR] [--photodiode-location {tl,tr,bl,br}]

Run PsychoPy timing tests.

options:
  -h, --help            show this help message and exit
  --list-devices, -l    List available audio devices (speakers and microphones).
  --speaker SPEAKER, -s SPEAKER
                        Name of the speaker device to use.
  --speaker-volume SPEAKER_VOLUME, -v SPEAKER_VOLUME
                        Volume of the speaker device to use.
  --speaker-sample-rate SPEAKER_SAMPLE_RATE, -r SPEAKER_SAMPLE_RATE
                        Latency of the speaker device to use.
  --microphone MICROPHONE, -m MICROPHONE
                        Name of the microphone device to use.
  --microphone-channels MICROPHONE_CHANNELS, -c MICROPHONE_CHANNELS
                        Number of channels of the microphone device to use.
  --microphone-sample-rate MICROPHONE_SAMPLE_RATE, -z MICROPHONE_SAMPLE_RATE
                        Sample rate of the microphone device to use.
  --num-iter NUM_ITER, -n NUM_ITER
                        Number of iterations (~= frames) to run the test.
  --trigger-every TRIGGER_EVERY, -t TRIGGER_EVERY
                        Trigger high every N iterations.
  --port-addr PORT_ADDR, -p PORT_ADDR
                        Address of the parallel port.
  --screen-res SCREEN_RES, -x SCREEN_RES
                        Screen resolution (width, height).
  --out-dir OUT_DIR, -o OUT_DIR
                        Output directory for data files and recordings.
  --photodiode-location {tl,tr,bl,br}, -d {tl,tr,bl,br}
                        Location of the photodiode.
```

For example, to list available audio devices:

```bash
python pptt/run-tests.py --list-devices
```

Will give you something like:

```text
❯ python .\pptt\run-tests.py -l
Available audio devices:
Speakers:
         8: OUT 1-4 (2- BEHRINGER UMC 204 192k)
         9: OUT 3-4 (2- BEHRINGER UMC 204 192k)
        10: OUT 1-2 (2- BEHRINGER UMC 204 192k)
Microphones:
        11: IN 2 (2- BEHRINGER UMC 204 192k)
        12: IN 1 (2- BEHRINGER UMC 204 192k)
        13: IN 1-2 (2- BEHRINGER UMC 204 192k)
```

Then, you can run the tests with the desired devices:

```bash
python .\pptt\run-tests.py -r 48000 -z 48000 -s 10 -m 12 -p 0x378
```

This will run the tests with a sample rate of 48kHz for both the speaker and the microphone, using the speaker device 10 and the microphone device 12, and sending triggers to the parallel port at address 0x378.

## Data output

The script will output a TSV file with the following columns:

- idx
- core_timestamp_raw
- mouse_click_raw
- mouse_click_trigger_raw
- pin_0_low_raw
- pin_1_low_raw
- pin_2_low_raw
- pin_state_raw
- regular_trigger_raw
- sound_onset_raw
- trial_timestamp_raw
- order

The `*_raw` columns are the raw timestamps in seconds for the particular event.

You will also get a WAV file with the sound that was captured from the microphone.


## Analysis

There's a Jupyter notebook in the `analysis` folder that will help you analyze the data.

There are currently 3 required files to pick in the beginning of the notebook:

- The TSV file with the data
- The EEG file with the triggers
- The WAV file with the sound

For more information see the [get-timings.ipynb notebook](analysis/get-timings.ipynb).

You will get some plots and latency information from the various triggers / tests.

```bash
