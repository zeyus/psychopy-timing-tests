"""General port abstraction class for sending a trigger signal to the EEG system."""

from abc import ABC, abstractmethod
import asyncio
from typing import Literal
from psychopy import parallel  # type: ignore
from serial import Serial  # type: ignore

class Port(ABC):
    """Abstract base class for port abstraction."""
    
    @abstractmethod
    def __init__(self):
        """Initializes the port."""
        pass
    
    @abstractmethod
    async def asend_trigger(self, trigger_code: int):
        """Sends a trigger signal to the EEG system.
        
        Args:
            trigger_code: The trigger code to send.
        """
        pass

    @abstractmethod
    async def send_trigger(self, trigger_code: int):
        """Sends a trigger signal to the EEG system.
        
        Args:
            trigger_code: The trigger code to send.
        """
        pass


class ParallelPort(Port):
    """Port abstraction for sending a trigger signal to the EEG system via a parallel port."""
    
    def __init__(self, port_addr: int = 0x378):
        """Initializes the parallel port.
        
        Args:
            port_addr: The address of the parallel port.
        """
        self.port = parallel.ParallelPort(port_addr)

    def send_trigger(self, trigger_code: int, duration: float = 0.001):
        """Sends a trigger signal to the EEG system.
        
        Args:
            trigger_code: The trigger code to send.
            duration: The duration of the trigger signal.
        """
        self.port.setData(trigger_code)
    
    def set_pin(self, pin: Literal[1, 2, 3, 4, 5, 6, 7, 8], value: Literal[0, 1]):
        """Sets a bit of the parallel port.
        
        Args:
            bit: The bit to set.
            value: The value to set the bit to.
        """
        self.port.setData(self.port.getData() | (value << pin) - 1)
    
    def set_pins(self, pins: list[Literal[0, 1]]):
        """Sets all bits of the parallel port.
        
        Args:
            pins: The values to set the bits to.
        """
        if len(pins) != 8:
            raise ValueError("pins must be a list of 8 bits")
        self.port.setData(int(''.join(map(str, pins)), 2))

    async def asend_trigger(self, trigger_code: int, duration: float = 0.001):
        """Sends a trigger signal to the EEG system.
        
        Args:
            trigger_code: The trigger code to send.
            duration: The duration of the trigger signal.
        """
        
        self.port.setData(trigger_code)
        await asyncio.sleep(duration)
        self.port.setData(0)





class SerialPort(Port):
    """Port abstraction for sending a trigger signal to the EEG system via a serial port."""
    
    def __init__(self, port_addr: str, baudrate: int = 9600, parity: str = 'N', stopbits: int = 1, **kwargs):
        """Initializes the serial port.
        
        Args:
            port_addr: The address of the serial port.
            baudrate: The baudrate of the serial port.
            parity: The parity of the serial port.
            stopbits: The number of stop bits of the serial port.
            kwargs: Additional keyword arguments for the PySerial port initialization.
        """

        self.port = Serial(port_addr, baudrate=baudrate, parity=parity, stopbits=stopbits, **kwargs)

    async def asend_trigger(self, trigger_code: int, duration: float = 0.001):
        """Sends a trigger signal to the EEG system.
        
        Args:
            trigger_code: The trigger code to send.
            duration: The duration of the trigger signal.
        """
        self.port.write(trigger_code.to_bytes(1, byteorder='big'))
        await asyncio.sleep(duration)
        self.port.write(b'\x00')

    def __del__(self):
        """Closes the serial port."""
        self.port.close()
