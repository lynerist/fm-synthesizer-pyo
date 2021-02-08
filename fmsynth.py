from pyo import *

class Oscillator(PyoObject):
	"""
	A class needed by the FmSynth.
	The oscillators can be summed to each other.
	Mod is the parameter for the optional modulator.
	Idosc is used to give an id to an oscillator.

	:Parent: :py:class:`PyoObject`

    :Args:

      freqs : MToF
          Base frequencies that are played.
      mod : int or PyoObject, optional
          Possible modulation of the modulator.
		  Defaults to 0.
      idosc : str, optional
          Id used to identify the oscillator in the ctrls.
          Defaults to "".
      index : int or PyoObject, optional
          Index of modulation, it defines the ammount of modulation.
          Defaults to 0.
      factor_mod: float or PyoObject, optional
          Frequency of the modulator = factor_mod * base note.
          Defaults to 0.

	>>> s = Server().boot()
	>>> freq = MToF(Sig(60))
    >>> osc = Oscillator(freq)
    >>> signal = Sine(100 + osc)
	>>> osc.ctrl()
	>>> signal.out()
	"""

	def __init__(self, freqs, mod = 0, idosc = "", index = 0, factor_mod = 1):
		super().__init__()
		#Controls
		if not isinstance(freqs, MToF):
			raise TypeError("freq must be a MToF")
		if not isinstance(mod, (int, PyoObject)):
			raise TypeError("mod must be an int or a PyoObject")
		if not isinstance(idosc, str):
			raise TypeError("idosc must be a str")
		if not isinstance(index, (int, PyoObject)):
			raise TypeError("index must be an int or a PyoObject")
		if not isinstance(factor_mod, (int, float, PyoObject)):
			raise TypeError("factor_mod must be a number or a PyoObject")

		#Define istance attributes
		self._freqs = freqs
		self._mod = mod									
		self._idosc = idosc				
		self._index = index				
		self._factor_mod = factor_mod	
		
		#Creation of the sound (50 is a magic number used to have a suitable control of the index of modulation.)
		self._lfo = Sine(freqs * self._factor_mod + self._mod, mul = self._index * 50)
		
		#getting base objects
		self._base_objs = self._lfo.getBaseObjects()

	def ctrl(self, map_list=None, title="", wxnoserver=False):
		self._map_list = [SLMap(0,20, "lin", "index", self._index, res = "int"), 
		SLMap(0,4, "lin", "factor_mod", self._factor_mod, res = "float")]
		super().ctrl(map_list, "Oscillator " + self._idosc, wxnoserver)
	
	def play(self, dur=0, delay=0):
		self._lfo.play()
		return super().play(dur, delay)

	def stop(self):
		self._lfo.stop()
		return super().stop()

	def _setIndex(self, x):
		"""
		Replace the `index` attribute.

		:Args:

			x : int or PyoObject
				New `index` attribute.

		"""
		self._index = x
		self._lfo.mul = x * 50

	def _setFactor_mod(self, x, mod, freqs):
		"""
		Replace the `factor_mod` attribute.

		:Args:

			x : float or PyoObject
				New `factor_mod` attribute.

		"""
		self._factor_mod = x
		self._lfo.freq = freqs * x + mod	

	@property
	def index(self):
		"""int or PyoObject. Index of modulation."""
		return self._index
	@index.setter
	def index(self, x):
		self._setIndex(x)

	@property
	def factor_mod(self):
		"""float or PyoObject. A factor that defines the frequency of the modulator."""
		return self._factor_mod
	@factor_mod.setter
	def factor_mod(self, x):
		self._setFactor_mod(x, self._mod, self._freqs)

class FmSynth(PyoObject):
	"""

	A frequency modulation synth that uses four oscillators.

	The first and the second oscillators modulate the carrier frequency.
	The third one modulates the first while the fourth modulates the second one.

     ____            ____
    |    |          |    |
    | 3  |          |  4 |
    |____|          |____|
      ||              ||
      ||              ||
     _\/_            _\/_
    |    |          |    |
    | 1  |          |  2 |
    |____|          |____|
      ||              ||
      ||______________||
      \______ + _______/
             | |
            _\ /_
            |   |
            | C |
            |___|
             | |
             | |
             \ /
            OUTPUT

	:Parent: :py:class:`PyoObject`

	:Args:		
		pass

    >>> s = Server().boot()
    >>> sy = FmSynth()
    >>> sy.out()
	>>> sy.ctrl()
	"""
	def __init__(self):
		super().__init__()
		# pitches in Hz
		self._notes = Notein()

		#Note pitches andA DSR on note amplitudes
		self._freqs = MToF(self._notes["pitch"])
		self._amps = MidiAdsr(self._notes["velocity"], attack=0.05, decay=0.4, sustain=0.3, release=0.5)

		#Creation of the four oscillators
		self.osc4 = Oscillator(self._freqs, idosc = "4 (2)")
		self.osc3 = Oscillator(self._freqs, idosc = "3 (1)")
		self.osc2 = Oscillator(self._freqs, mod = self.osc4, idosc = "2")
		self.osc1 = Oscillator(self._freqs, mod = self.osc3, idosc = "1")
		
		#The output signal (I added Pan as a last minute thing to have a stereo sound so it's not well documented.)
		self.fm = Pan(Sine(freq = self._freqs + self.osc1 + self.osc2, mul = self._amps))
		
		# Define base objects
		self._base_objs = self.fm.getBaseObjects() 
		
	def ctrl(self, map_list=None, title=None, wxnoserver=False):
		"""
		There are two ctrls for each oscillator one for the index and one for the frequency factor
		"""
		self._notes.keyboard()
		self.osc1.ctrl()
		self.osc2.ctrl()
		self.osc3.ctrl()
		self.osc4.ctrl()

	def ampsCtrl(self):
		"""
		To control the adsr of the output signal.
		"""
		self._amps.ctrl()
	
	def play(self, dur=0, delay=0):
		self.fm.play()
		return super().play(dur, delay)

	def stop(self):
		self.fm.stop()
		return super().stop()

	def out(self, chnl=0, inc=1, dur=0, delay=0):
		self.fm.play()
		return super().out(chnl, inc, dur, delay)

if __name__ == "__main__":
	s = Server().boot()
	s.amps = 0.9
	sy = FmSynth()
	sy.out()
	#sy.ampsCtrl()
	Scope(sy)
	sy.ctrl()
	s.gui(locals())
