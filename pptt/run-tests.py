import asyncio
from pathlib import Path
import sys
import os
from psychopy import logging  # type: ignore
from psychopy.core import Clock  # type: ignore



async def main():
    # Add the parent directory to the path so we can import pptt
    sys.path.append(str(Path(__file__).resolve().parents[1]))

    # add lib dir to DLL search path
    with os.add_dll_directory(str(Path(__file__).resolve().parents[1] / 'lib')):
        from pptt.exps.animated_square import animated_square

        studyClock = Clock()
        logging.root.format="{t} \t{levelname} \t{message}"
        logging.setDefaultClock(studyClock)
        
        logger = logging.LogFile(f'animated_square.log', level=logging.INFO, filemode='w')
        logging.info('Starting animated square test')
        await animated_square()


if __name__ == '__main__':
    asyncio.run(main())
