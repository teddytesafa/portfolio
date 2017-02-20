"""""""""""""""""""""""""""""""""""
 STOCHASTIC PATH GENERATION
 Written by: Tewodros T Belay
"""""""""""""""""""""""""""""""""""
# Import python math libraries
from __future__ import division
import matplotlib.pyplot as plt
import pylab
import numpy as np
import random


class StochasticPath(object):
    """
    Defines a stochastic path type
    """
    def __init__(self, nPaths, nSteps):
        """
        Initialize a path instance with the various parameters
        nPaths: Number of paths to be generated
        nSteps: Number of steps to be generated
        stdev: Standard deviation
        initialPrice: The initial price of the underlying asset
        """
        assert type(nPaths) is int, 'nPaths needs to be a number!'
        assert type(nSteps) is int, 'nSteps needs to be a number!'
        self.nPaths = nPaths
        self.nSteps = nSteps
        self.rateOfReturn = None
        self.stdev = None
        self.initialPrice = None

    def getNPaths(self):
        """ Returns the number of paths simulated"""
        return self.nPaths

    def getNSteps(self):
        """ Returns the number of steps """
        return self.nSteps

    def setStat(self, rAndSigma):
        """
        rAndSigma is a tuple consisting of
        the rate of return and
        standard deviation as (r, sigma) of
        the underlying path
        """
        assert type(rAndSigma) is tuple, 'rAndSigma is not tuple'
        assert isinstance(rAndSigma[0], (int, float)), (
               'rAndSigma values need to be numbers.')
        assert isinstance(rAndSigma[1], (int, float)), (
               'rAndSigma values need to be numbers.')
        self.rateOfReturn = rAndSigma[0]
        self.stdev = rAndSigma[1]

    def setInitialPrice(self, initialPrice):
        assert isinstance(initialPrice, (int, float)), (
               'Initial price needs to be a number.')
        self.initialPrice = initialPrice

    def drift(self):
        r = self.rateOfReturn
        sigma = self.stdev
        try:
            drift = r-0.5*(sigma**2)
            return drift
        except ValueError:
            return 'Check the values in rAndSigma!'

    def plot(self, S):
        x = pylab.linspace(0, pylab.size(S, 1)-1, pylab.size(S, 1))
        for i in range(pylab.size(S, 0)):
            y = S[i, :]
            plt.plot(x, y)
        plt.show()


class GeometricBrownianMotion(StochasticPath):
    """
    Defines a Geometric Brownian Motion stochastic path type
    """
    def __init__(self, nPaths, nSteps):
        StochasticPath.__init__(self, nPaths, nSteps)
        """Initialize parameters"""

    def generatePath(self, T):
        """
        T: time period
        r: rate of return
        sigma: standard deviation
        dt: time steps
        drift: mean movement price
        zn: array of random numbers with dimension(nPaths, nSteps)
        """
        assert (T > 0), 'Time needs to be a positive number'
        try:
            S0 = self.initialPrice
            r = self.rateOfReturn
            sigma = self.stdev
            nPaths = self.nPaths
            nSteps = self.nSteps
            dt = T/float(nSteps)
            drift = r-0.5*(sigma**2)
            zn = pylab.randn(nPaths, nSteps)
            zn = np.vstack((zn, -zn))
            S = pylab.zeros((nPaths, nSteps))
            start = S0*pylab.ones((2*nPaths, 1))
            next = S0*pylab.cumprod(pylab.exp(drift*dt +
                                    sigma*pylab.sqrt(dt)*zn), 1)
        except ValueError:
            return 'Please check the value of the initial parameters.'
        return pylab.hstack((start, next))

    def __str__(self):
        """Generates a Geometric Brownian Motion path"""
        return 'Path generated with: r =' + str(self.rateOfReturn) + \
               ', and sigma =' + str(self.stdev)


class MertonJumpDiffusion(StochasticPath):
    def __init__(self, nPaths, nSteps):
        StochasticPath.__init__(self, nPaths, nSteps)
        """Initialize parameters"""
        self.jumpParameters = None

    def setJumpParameters(self, jumpParameters):
        """
        jumpParameters: is a list like:
        [l-lambda, a-drift rate, d-standard deviation]
        """
        assert isinstance(jumpParameters[0], (int, float)), (
               'jumpParameter values need to be numbers.')
        assert isinstance(jumpParameters[1], (int, float)), (
               'jumpParameter values need to be numbers.')
        assert isinstance(jumpParameters[2], (int, float)), (
               'jumpParameter values need to be numbers.')
        self.jumpParameters = jumpParameters

    def generatePath(self, T):
        """
        r: rate of return
        sigma: standard deviation
        dt: time steps
        drift: mean movement price
        zn: array of random numbers with dimension(nPaths,nSteps)
        ld: poisson arrival rate
        a: mean drift of jump
        d: standard deviation of jump
        k: expected value of jump

        """
        assert (T > 0), 'Time needs to be a positive number'
        try:
            S0 = self.initialPrice
            r = self.rateOfReturn
            sigma = self.stdev
            ld = self.jumpParameters[0]
            a = self.jumpParameters[1]
            d = self.jumpParameters[2]
            k = pylab.exp(a+0.5*(d**2))-1
            nPaths = self.nPaths
            nSteps = self.nSteps
            dt = T/float(nSteps)
            drift = r-ld*k-0.5*(sigma**2)
            zn = pylab.randn(nPaths, nSteps)
            zn = np.vstack((zn, -zn))
            zp = pylab.randn(nPaths, nSteps)
            zp = np.vstack((zp, -zp))
            S = pylab.zeros((2*nPaths, nSteps))
            p = pylab.poisson(ld*dt, (2*nPaths, nSteps))
            j = a*p+d*pylab.sqrt(p)*zp
            start = S0*pylab.ones((2*nPaths, 1))
            next = S0*pylab.cumprod(pylab.exp(drift*dt +
                                              sigma*pylab.sqrt(dt)*zn + j), 1)
        except ValueError:
            return 'Please check the value' + \
                   'of the properties.'
        return pylab.hstack((start, next))

    def __str__(self):
        """Generates a Merton Jump Diffusion path"""
        return 'Path generated with: r =' + str(self.rateOfReturn) + \
               ', sigma =' + str(self.stdev) + \
               ', and lambda =' + str(self.jumpParameters[0])
