# find_port.py

import glob


def find_stm32_port():
    # Check both possible serial device names
    ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")

    if len(ports) == 0:
        raise RuntimeError(
            "No STM32 port found. Check USB connection. "
            "Tried /dev/ttyACM* and /dev/ttyUSB*"
        )

    ports.sort()

    print("Found STM32 ports:", ports)
    print("Using STM32 port:", ports[0])

    return ports[0]