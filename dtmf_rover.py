# dtmf_rover.py
# Controls a Raspberry Pi-based RC vehicle with ham radio DTMF codes.
# See the accompanying PDF file for photographs depicting the physical
# interface with a Dual L9110 Motor Driver Board.
#
# Copyright 2019, 2020 Terence C. Paddack (K5DXD)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# IMPORTANT NOTE: "Remote GPIO" needs to be enabled for pigpio to work
# The pigpio library is used here because it allows for variable motor
# speed control by using Pulse Width Modulation on all GPIO pins.
# To enable the pigpio service daemon, follow these steps:
# Applications Menu > Preferences > Raspberry Pi Configuration
#     Interfaces Tab > Remote GPIO > Enable
# or (in the terminal)
#     sudo systemctl enable pigpiod.service
#     sudo systemctl start pigpiod.service

import pigpio
from rtl_dtmf import DTMF

# Declare some constants for later use
# Motor 1 (Right)
# Pins 17 & 27
MOTOR1_FORWARD = 27
MOTOR1_REVERSE = 17

# Motor 2 (Left)
# Pins 23 & 24
MOTOR2_FORWARD = 24
MOTOR2_REVERSE = 23

# Motor speed values
FORWARD_SPEED = 255
REVERSE_SPEED = 255
TURN_SPEED = 255

def stop():
    """
    Sets the PWM duty cycle of all motor controller
    pins to zero. This stops the motors.
    """
    pi.set_PWM_dutycycle(MOTOR1_FORWARD, 0)
    pi.set_PWM_dutycycle(MOTOR1_REVERSE, 0)
    pi.set_PWM_dutycycle(MOTOR2_FORWARD, 0)
    pi.set_PWM_dutycycle(MOTOR2_REVERSE, 0)

def forward():
    """
    Sets the PWM duty cycle of the forward motor
    controller pins to 255. This runs the motors
    forward at full speed.
    """
    pi.set_PWM_dutycycle(MOTOR1_FORWARD, FORWARD_SPEED)
    pi.set_PWM_dutycycle(MOTOR2_FORWARD, FORWARD_SPEED)

def reverse():
    """
    Sets the PWM duty cycle of the reverse motor
    controller pins to 255. This runs the motors
    in reverse at full speed.
    """
    pi.set_PWM_dutycycle(MOTOR1_REVERSE, REVERSE_SPEED)
    pi.set_PWM_dutycycle(MOTOR2_REVERSE, REVERSE_SPEED)

def left():
    """
    Sets the PWM duty cycle of the left motor's reverse
    pin to 255. This runs the left motor in reverse at
    full speed.
    
    Sets the PWM duty cycle of the right motor's forward
    pin to 255. This runs the right motor forward at 
    full speed.
    
    This causes the vehicle to rotate left (counter-clockwise).
    """
    pi.set_PWM_dutycycle(MOTOR1_FORWARD, TURN_SPEED)
    pi.set_PWM_dutycycle(MOTOR2_REVERSE, TURN_SPEED)

def right():
    """
    Sets the PWM duty cycle of the right motor's reverse
    pin to 255. This runs the right motor in reverse at
    full speed.
    
    Sets the PWM duty cycle of the left motor's forward 
    pin to 255. This runs the left motor forward at 
    full speed.
    
    This causes the vehicle to rotate right (clockwise).
    """
    pi.set_PWM_dutycycle(MOTOR1_REVERSE, TURN_SPEED)
    pi.set_PWM_dutycycle(MOTOR2_FORWARD, TURN_SPEED)

def main():
    """
    This function will be set to run at the end of 
    the DTMF decoder's main loop. It will check the
    DTMF button value and state, then call the 
    appropriate control functions above.
    """
    if dtmf.button.status == 'DOWN':
        # A DTMF button was pressed on the transmitter
        if dtmf.button.value == '2':
            forward()
        elif dtmf.button.value == '6':
            right()
        elif dtmf.button.value == '4':
            left()
        elif dtmf.button.value == '8':
            reverse()
    elif dtmf.button.status == 'UP':
        # A DTMF button was released on the transmitter
        stop()

# Use pigpio library to PWM the motor controller pins
pi = pigpio.pi()

# Initialize the DTMF decoder
dtmf = DTMF()
dtmf.rf_freq = '147.575'
dtmf.chunk_size = 3600
dtmf.snr_threshold = 15

# Over-ride the decoder's main() method to run our code
# at the end of each of its main loop iterations
dtmf.main = main

# Start the DTMF decoder
dtmf.start()