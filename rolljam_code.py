"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import time


class blk(gr.sync_block):

  def __init__(self, first_sink="signal.raw", second_sink="signal2.raw"):
    gr.sync_block.__init__(
      self,
      name='Embedded Python Block',
      in_sig=[np.complex64, np.complex64, np.float32],
      out_sig=[np.complex64]
    )
    self.first_signal = None
    self.second_signal = None
    self.first_sink = open(first_sink, 'w+b')
    self.second_sink = open(second_sink, 'w+b')
    self.first_signal_captured = False
    self.detected = False
    self.transmit = False
    self.finished = False
    self.timer = 0

  def work(self, input_items, output_items):
    input_jam = input_items[0] # Jamming signal
    input_sig = input_items[1] # Captured signal
    input_detect = input_items[2] # Signal detection

    if not self.finished:
      output_items[0][:] = input_jam
      if self.detected:
        if not self.first_signal_captured:
          self.first_signal = np.concatenate((self.first_signal, input_sig))
        else:
          self.second_signal = np.concatenate((self.second_signal, input_sig))
        if int(round(time.time() * 1000)) - self.timer >= 1000:
          print('Signal captured')
          if self.first_signal_captured:
            self.second_sink.write(bytearray(self.second_signal))
            self.first_sink.close()
            self.second_sink.close()
            self.finished = True
          else:
              self.first_sink.write(bytearray(self.first_signal))
              self.first_sink.close()
          self.detected = False
          self.first_signal_captured = True					
      elif 1 in input_detect:
        if not self.first_signal_captured:
          self.first_signal = input_sig
        else:
          self.second_signal = input_sig
          self.transmit = True
        self.timer = int(round(time.time() * 1000))
        self.detected = True

    # Trasmit the first signal
    elif len(self.first_signal) > 0:
      self.first_signal = self.send_signal(self.first_signal, output_items)

    return len(output_items[0])
  
  def send_signal(self, signal, output_items):
    if(len(signal) < len(output_items[0])):
      output_items[0][:len(signal)] = signal
      signal = []
    else:
      output_items[0][:] = signal[:len(output_items[0])]
      signal = signal[len(output_items[0]):]
    return signal