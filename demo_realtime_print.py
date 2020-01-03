# demo_realtime_print.py
# Prints a continuous stream of output that displays the DTMF tones
# as they are detected by the rtl_dtmf library.
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
    # Print the output from the DTMF decoder
    print(dtmf.button.value + ": " + 
          dtmf.button.status +
          " | SNR:" + str(int(dtmf.snr)))

# Do the following if this is being executed as a stand-alone program
if __name__ == "__main__":
    # Create an instance of the DTMF class
    dtmf = DTMF()
    
    # Set the receive frequency in MHz
    dtmf.rf_freq = '147.575'
    
    # Over-ride the decoder's main (placeholder) with our main method
    dtmf.main = main
    
    # Start the dtmf decoder's main loop
    dtmf.start()
