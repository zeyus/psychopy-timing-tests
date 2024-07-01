import asyncio
from pathlib import Path
import sys
import os
from psychopy import logging
from psychopy.core import Clock

# Add the parent directory to the path so we can import pptt
sys.path.append(str(Path(__file__).resolve().parents[1]))

# add lib dir to DLL search path
os.add_dll_directory(str(Path(__file__).resolve().parents[1] / 'lib'))

async def main():
    from pptt.exps.animated_square import animated_square

    studyClock = Clock()
    logging.root.format="{t} \t{levelname} \t{message}"
    logging.setDefaultClock(studyClock)
    
    logger = logging.LogFile(f'animated_square.log', level=logging.INFO, filemode='w')
    logging.info('Starting animated square test')
    await animated_square()


if __name__ == '__main__':
    asyncio.run(main())