import ctypes

# Define constants

INPUT_KEYBOARD = 1

KEYEVENTF_KEYUP = 0x0002

# Define the C structures

PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):

    _fields_ = [("wVk", ctypes.c_ushort),

                ("wScan", ctypes.c_ushort),

                ("dwFlags", ctypes.c_ulong),

                ("time", ctypes.c_ulong),

                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):

    _fields_ = [("uMsg", ctypes.c_ulong),

                ("wParamL", ctypes.c_short),

                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):

    _fields_ = [("dx", ctypes.c_long),

                ("dy", ctypes.c_long),

                ("mouseData", ctypes.c_ulong),

                ("dwFlags", ctypes.c_ulong),

                ("time", ctypes.c_ulong),

                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):

    _fields_ = [("ki", KeyBdInput),

                ("mi", MouseInput),

                ("hi", HardwareInput)]

class Input(ctypes.Structure):

    _fields_ = [("type", ctypes.c_ulong),

                ("ii", Input_I)]

# Get the SendInput function

SendInput = ctypes.windll.user32.SendInput

# Track key states

keyState = {}

def PressKey(hexKeyCode):

    if hexKeyCode in keyState and keyState[hexKeyCode]:

        return False  # already pressed

    keyState[hexKeyCode] = True

    extra = ctypes.c_ulong(0)

    ki = KeyBdInput(

        wVk=0,  # Use 0 if not using a virtual key code

        wScan=hexKeyCode,

        dwFlags=0,  # Press event

        time=20,

        dwExtraInfo=ctypes.pointer(extra)

    )

    ii_ = Input_I()

    ii_.ki = ki

    x = Input(type=INPUT_KEYBOARD, ii=ii_)

    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    return True

def ReleaseKey(hexKeyCode):

    if hexKeyCode in keyState and not keyState[hexKeyCode]:

        return False  # already released

    keyState[hexKeyCode] = False

    extra = ctypes.c_ulong(0)

    ki = KeyBdInput(

        wVk=0,  # Use 0 if not using a virtual key code

        wScan=hexKeyCode,

        dwFlags=KEYEVENTF_KEYUP,  # Release event

        time=0,

        dwExtraInfo=ctypes.pointer(extra)

    )

    ii_ = Input_I()

    ii_.ki = ki

    x = Input(type=INPUT_KEYBOARD, ii=ii_)

    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    return True

# Key codes (for demonstration purposes, make sure these are correct for your use case)

up = 0xC8

left = 0xCB

right = 0xCD

down = 0xD0

nitro = 0x2C  # Example key code, ensure this is correct