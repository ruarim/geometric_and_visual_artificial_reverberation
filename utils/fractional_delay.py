# Utility functions for the package
# Copyright (C) 2019  Sidney Barthe, Robin Scheibler, Ivan Dokmanic, Eric Bezzam
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# You should have received a copy of the MIT License along with this program. If
# not, see <https://opensource.org/licenses/MIT>.

import numpy as np

def fractional_delay(t0, N=81):
    """
    Creates a fractional delay filter using a windowed sinc function.
    The length of the filter is fixed by the module wide constant
    `frac_delay_length` (default 81).

    Parameters
    ----------
    t0: float
        The delay in fraction of sample. Typically between -1 and 1.

    Returns
    -------
    numpy array
        A fractional delay filter with specified delay.
    """

    if isinstance(t0, np.ndarray) and t0.ndim == 1:
        t0 = t0[:, None]

    return np.hanning(N) * np.sinc(np.arange(N) - (N - 1) / 2 - t0)