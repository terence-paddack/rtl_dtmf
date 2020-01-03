# demo_print_buffer.py
# Demonstrates how to read the DTMF code-sequence buffer of the 
# rtl_dtmf library. Each time a new DTMF tone is detected, the updated
# buffer is printed.
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

# Import the DTMF class from the library
from rtl_dtmf import DTMF

# Declare a function that will run in each iteration of the main loop
def main():
    if (dtmf.button.status == 'UP'):
        # If a new DTMF code is in the buffer, print the buffer
        print("Code Buffer: " + dtmf.code_buffer)

# Do the following if this is being executed as a stand-alone program
if __name__ == "__main__":
    # Create an instance of the DTMF class
    dtmf = DTMF()
    
    # Set the receive frequency in MHz
    dtmf.rf_freq = '147.575'
    
    # Enable DTMF code-sequence detection
    dtmf.enable_sequence = True
    
    # Set the code buffer timeout in seconds
    dtmf.code_timeout = 5
    
    # Over-ride the decoder's main (placeholder) with our main method
    dtmf.main = main
    
    # Start the dtmf decoder's main loop
    dtmf.start()