# rtl_dtmf.py
# rtl_dtmf is a Python library that detects and decodes DTMF tones 
# for amateur radio remote telecommand; it requires rtl_fm and an 
# RTL-SDR dongle. It was originally intended for use on a Raspberry Pi.
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

import subprocess
import numpy as np
from datetime import datetime

# These will be used to calculate the FFT
# These ranges could be calculated before the main loop
# of the DTMF tone detector begins; they could also probably
# be narrower, too.
DTMF_FREQ  = [697, 770, 852,  941, 1209, 1336, 1477, 1633]
DTMF_START = [679, 750, 830,  875, 1177, 1301, 1438, 1594]
DTMF_END   = [715, 791, 874, 1008, 1241, 1371, 1516, 1672]

# These data will be used to decode the tones and keys
KEYS = {(697, 1209): '1',
        (697, 1336): '2',
        (697, 1477): '3',
        (697, 1633): 'A',
        (770, 1209): '4',
        (770, 1336): '5',
        (770, 1477): '6',
        (770, 1633): 'B',
        (852, 1209): '7',
        (852, 1336): '8',
        (852, 1477): '9',
        (852, 1633): 'C',
        (941, 1209): '*',
        (941, 1336): '0',
        (941, 1477): '#',
        (941, 1633): 'D'}

class Button(object):
    def __init__(self):
        self.value = ''
        self.status = ''

class DTMF(object):
    """Class that uses rtl_fm to decode DTMF tones."""
    def __init__(self):
        # Initialize a Button object
        self.button = Button()

        # Initialize some other variables
        self.chunk_size = 3600
        self.sample_rate = 24000
        self.snr = 0
        self.snr_threshold = 9
        
        # rtl_fm variables
        self.rtl_fm = None
        # rtl_fm tuning frequency in MHz
        self.rf_freq = ''

        # Code sequence recognition variables
        self.code_timeout = 10
        self.code_buffer = ''
        self.code_terminator = ''
        self.code = ''
        self.last_keypress = datetime.now()
        self.kill_code = ''
        self.kill = False
    
        # Disable sequence recongition by default
        self.enable_sequence = False
    
    def main(self):
        """ This method executes in the main loop of the DTMF class."""
        print("Subclass and over-ride this method.")
    
    def update_buffer(self):
        """This method updates the buffer that is used for code
        sequence recognition. If DTMF.enable_sequence is True, it runs
        during each iteration of the main loop in DTMF.start()
        """
        # Get the current time
        current_time = datetime.now()
        
        # Find the difference between current time and last keypress
        diff = current_time - self.last_keypress
        
        # Clear any previous codes
        self.code = ''
        
        # Check for a timeout
        if diff.total_seconds() <= self.code_timeout:
            # Timeout has not expired; check for key
            if self.button.status == 'UP':
                # a key was pressed; update last_keypress
                self.last_keypress = current_time
                # Update the buffer
                self.code_buffer += self.button.value
                # Check for a terminator character
                if self.button.value == self.code_terminator:
                    # Terminator detected; update self.code
                    self.code = self.code_buffer[0: len(self.code_buffer) - 1]
                    # Clear the buffer
                    self.code_buffer = ''
        else:
            # Timeout has expired; clear the buffer
            self.code_buffer = ''
            # Reset last_keypress
            self.last_keypress = current_time
    
    def stop(self):
        """Kills rtl_fm and sets a flag that exits the main loop.
        This method is called from the main loop of DTMF.start
        It is only called when:
            DTMF.enable_sequence = True
                AND
            DTMF.kill_code is detected
        """
        subprocess.Popen.kill(self.rtl_fm)
        self.kill = True
    
    def start(self):
        """ Starts the main loop of the DTMF class."""
        # Determine the frequency bins to be returned by FFT
        fft_freqs = np.fft.rfftfreq(self.chunk_size // 2,
                                    d=1.0 / self.sample_rate)
        
        # Create lists of start & end indices for each DTMF frequency
        start = [0] * len(DTMF_FREQ)
        end = [0] * len(DTMF_FREQ)

        # Create cmd line argument to set rtl_fm frequency
        str_freq = '-f ' + self.rf_freq + 'M'
        
        # Start rtl_fm as a subprocess and capture output
        self.rtl_fm = subprocess.Popen(['rtl_fm',
                                        str_freq,
                                        '-o 4',
                                        '-'], stdout=subprocess.PIPE,)
        
        # Populate the lists with bin indices from the FFT frequencies
        # This is where we determine the frequency ranges to scan
        # for the appropriate audio tones.
        for dtmf_index in range(len(DTMF_FREQ)):
            # Make a list of all fft bins within a given DTMF range
            temp = []
            for fft_index in range(len(fft_freqs)):
                # If an FFT bin corresponds to a frequency within the
                # given DTMF range, 
                if (fft_freqs[fft_index] >= DTMF_START[dtmf_index]) \
                    and (fft_freqs[fft_index] <= DTMF_END[dtmf_index]):
                    # Append that bin index to the temporary list
                    temp.append(fft_index)
                # If the FFT bin corresponds to a frequency higher than
                # the given DTMF range,
                elif (fft_freqs[fft_index] > DTMF_END[dtmf_index]):
                    # Assign the start and end FFT bin indices to lists
                    # use them later to find dominant tones in the FFT
                    start[dtmf_index] = temp[0]
                    end[dtmf_index] = temp[len(temp) - 1]
                    # Exit the internal loop to start looking for 
                    # FFT bins that correspond to the next DTMF range
                    break
        
        # Main loop of the DTMF.start method
        # Executes indefinitely until a kill code is detected
        #     Kill code will only work if DTMF.enable_sequence is True
        while True:
            # Set full flag to false
            bln_full = False

            # Read standard output from rtl_fm
            try:
                data = self.rtl_fm.stdout.read(self.chunk_size)
                bln_full = True
            except:
                #print("FAIL!")
                bln_full = False
                    
            # If buffer is full, proceed with decoding the signal
            if bln_full == True:
                # Load the data into a numpy array
                #   FYI: rtl_fm outputs samples as 16-bit,
                #   signed, little-endian, integers
                audio = np.frombuffer(data, dtype=np.int16)
                
                # Perform a (Real) Fast Fourier Transform on audio data
                fft = np.fft.rfft(audio)
                    
                # Populate the array with its absolute values
                fft = np.abs(fft)
                
                # Get amplitudes of relevant audio frequencies by bin
                # Use numpy.amax to examine slices of fft array
                tone_intensity = np.array([0] * len(DTMF_FREQ))
                for i in range(len(DTMF_FREQ)):
                    tone_intensity[i] = np.amax(fft[start[i]:end[i]])
                
                # Determine the dominant of the lowest 4 tones
                tone1_level = np.amax(tone_intensity[0:4])
                tone1_index = np.argmax(tone_intensity[0:4])
                tone1 = DTMF_FREQ[tone1_index]
                                
                # Determine the dominant of the highest 4 tones
                tone2_level = np.amax(tone_intensity[4:8])
                tone2_index = np.argmax(tone_intensity[4:8])
                tone2 = DTMF_FREQ[tone2_index + 4]
                                
                # Calculate average signal strength
                signal = (tone1_level + tone2_level) / 2 
                                
                # Calculate average noise level
                noise = (tone_intensity.sum() - (signal * 2)) / 6
                
                # Calculate the singal-to-noise ratio
                self.snr = signal // noise
                
                # A valid signal is detected if SNR exceeds threshold
                if self.snr >= self.snr_threshold:
                    # Determine which button was pressed
                    key = KEYS.get((tone1, tone2), None)
                    # If a new button is pressed
                    if key != None:
                        if self.button.value != key:
                            self.button.value = key
                            self.button.status = 'DOWN'
                        # If the button is being held
                        elif self.button.value == key:
                            self.button.value = key
                            self.button.status = 'HELD'
                else:
                    # If a button was previously released
                    if self.button.status == 'UP':
                        self.button.value = ''
                        self.button.status = ''
                    # If a button was in any other meaningful state
                    elif self.button.status != '':
                        self.button.status = 'UP'
                    # Otherwise
                    else:
                        self.button.value = ''
                        self.button.status = ''
            
            # Only get a DTMF key sequence if feature is enabled
            if self.enable_sequence == True:
                self.update_buffer()
                # Check to see if a termination code is detected
                if (self.code == self.kill_code) and \
                   (self.kill_code != ''):
                    self.stop()
            
            # Call the main function to do something with the data
            self.main()
            
            # Conditionally kill rtl_fm and stop decoding signals
            if self.kill == True:
                print("Kill code detected...exiting.")
                break