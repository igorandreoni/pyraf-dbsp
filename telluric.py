"""
dbsp.py is a pyraf-based reduction pipeline for spectra taken with the
Palomar 200-inch Double Spectrograph.
"""

# Authors:  Eric Bellm <ebellm@caltech.edu>,
#           Branimir Sesar <bsesar@astro.caltech.edu>
# License: MIT.

from pyraf import iraf
import numpy as np
import os
import subprocess
import shutil
import inspect
import pyfits
from scipy.optimize.minpack import leastsq
import copy
from glob import glob
import cosmics

def tell_corr(imgID):
    #tell_rootname = '%s%04d' % (side, telluric_cal_id)
    #tell_rootname = 'norm_red.std.fits'
    #if not os.path.exists('norm_red.std.fits'):
    #iraf.splot('red')
    iraf.unlearn('telluric')
    rootname='red%04d' %(imgID)
    iraf.telluric.input = rootname + '_flux.spec.fits'
    iraf.telluric.output = rootname+'_flux_cor.spec.fits'
    iraf.telluric.sample = "6277:6288,6860:7000,7584:7678,9252:9842"
    iraf.telluric.interactive = "yes"
    iraf.telluric.cal = 'norm_red.std.fits'
    iraf.telluric.ignoreaps = 'yes'
    iraf.telluric.xcorr = 'yes'
    iraf.telluric.tweakrms = 'yes'
    iraf.telluric.threshold = 0.01
    iraf.telluric()


def cor_coadd(imgID_list, side='red'):
    """Utility for coadding spectra from a single side.
        
        Parameters
        ----------
        imgID_list : list of ints or int
        image id(s) to be coadded.
        side : {'blue' (default), 'red', 'both'}
        'blue' or 'red' to indicate the arm of the spectrograph
        
        """
    assert side in ('blue', 'red', 'both')
    if side == 'both':
        simple_coadd(imgID_list, side='blue')
        simple_coadd(imgID_list, side='red')
        return
    spec_list_fits = ['{}{:04d}_flux_cor.spec.fits'.format(side,id) for id in imgID_list]
    out_name = side + '+'.join(['{:03d}'.format(i) for i in imgID_list]) + '_flux_cor'
    coadd_spectra(spec_list_fits, out_name, scale_spectra=False)
