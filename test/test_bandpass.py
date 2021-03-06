from __future__ import division

import unittest

import numpy as np
from scipy.fftpack import rfft, rfftfreq

from wyrm.types import Data
from wyrm.processing import band_pass
from wyrm.processing import swapaxes

class TestBandpass(unittest.TestCase):

    def setUp(self):
        # create some data
        fs = 100
        dt = 5
        self.freqs = [2, 7, 15]
        amps = [30, 10, 2]
        t = np.linspace(0, dt, fs*dt)
        data = np.sum([a * np.sin(2*np.pi*t*f) for a, f in zip(amps, self.freqs)], axis=0)
        data = data[:, np.newaxis]
        data = np.concatenate([data, data], axis=1)
        channel = np.array(['ch1', 'ch2'])
        self.dat = Data(data, [t, channel], ['time', 'channel'], ['s', '#'])
        self.dat.fs = fs

    def test_band_pass(self):
        """Band pass filtering."""
        # bandpass around the middle frequency
        ans = band_pass(self.dat, 6, 8)
        # the amplitudes
        fourier = np.abs(rfft(ans.data, axis=0) * 2 / self.dat.data.shape[0])
        ffreqs = rfftfreq(ans.data.shape[0], 1/ans.fs)
        # check if the outer freqs are damped close to zero
        # freqs...
        for i in self.freqs[0], self.freqs[-1]:
            # buckets for freqs
            for j in fourier[ffreqs == i]:
                # channels
                for k in j:
                    self.assertAlmostEqual(k, 0., delta=.1)

    def test_band_pass_copy(self):
        """band_pass must not modify argument."""
        cpy = self.dat.copy()
        band_pass(self.dat, 2, 3, timeaxis=0)
        self.assertEqual(cpy, self.dat)

    def test_band_pass_swapaxes(self):
        """band_pass must work with nonstandard timeaxis."""
        dat = band_pass(swapaxes(self.dat, 0, 1), 6, 8, timeaxis=1)
        dat = swapaxes(dat, 0, 1)
        dat2 = band_pass(self.dat, 6, 8)
        self.assertEqual(dat, dat2)


if __name__ == '__main__':
    unittest.main()
