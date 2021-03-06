 # Fluid simulator, based on paper:

# A Simple Fluid Solver based on the FFT
#               Jos Stam
# http://www.dgp.toronto.edu/people/stam/reality/Research/pdf/jgt01.pdf
#Author Jesse Johnson University of Montana
#modifications by Tony Mayer

import numpy as np
from scipy.interpolate import griddata
from scipy.fftpack import fftn,ifftn,fftshift,ifftshift
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import sleep
plt.style.use('dark_background')

class GridVector():
    """
    Simple container class to hold both the x and y components of
    a variable defined on a grid. Makes sense for variables like
    velocity, where the components are referenced as u.x, u.y
    etc.
    """
    def __init__(self,N=52,L=1.,coords=False):
        if coords:
            self.x,self.y = np.meshgrid(np.linspace(-L/2.,L/2.,N,endpoint=True)\
                               ,np.linspace(-L/2.,L/2.,N,endpoint=True))
        else:
            self.x = np.zeros((N,N))
            self.y = np.zeros((N,N))

class FluidSimulator():
    def __init__(self,L=1.,N=52,visc=0.001,dt=0.25):
        self.L    = L
        self.visc = visc
        self.dt   = dt
        self.N    = N

        self.X   = GridVector(self.N,L,coords=True) # coordinates
        self.Xs  = GridVector(self.N,L,coords=True) # staggered coords
        self.U   = GridVector(self.N) # velocity
        self.A   = GridVector(self.N) # acceleration
        self.rho = np.zeros((N,N))    # density
        self.ax = 0
        self.ay = 0
        # convenience for common calculations
        # for interpolation:
        self.flat_grid = np.array([self.X.x.flatten(),self.X.y.flatten()]).T

        # The staggered grid coordinates are needed for the ffts
        # They are the centers of the cells defined by X.x and X.y
        self.Xs.x[:,1:] = (self.Xs.x[:,1:]+self.Xs.x[:,:-1]) / 2.
        self.Xs.y[1:,:] = (self.Xs.y[1:,:]+self.Xs.y[:-1,:]) / 2.
        # Need N x N, not (N-1) x (N-1) - pad with PBC
        self.Xs.x[:,0] = self.Xs.x[:,-1]   # Column 0 = Column N-1 for x
        self.Xs.y[0,:] = self.X.y[-1,:]    # Row 0 = Row N-1 for y
        self.r2s = self.Xs.x**2 + self.Xs.y**2  # staggered radius squared
        self.eta = np.exp(-self.r2s * self.dt * self.visc) # visc. attenuation

    def pbc(self,x):
        # Enforce PBC:
        x[x>self.L/2.] = -self.L/2. + x[x>self.L/2.]%(self.L/2.)
        x[x<-self.L/2.] = self.L/2. - np.abs(x[x<-self.L/2.])%(self.L/2.)
        return x

    def advect(self,x,xp,yp,method='linear'):
        # final step of advection, move the old velocities to the
        # grid points.
        return griddata(self.flat_grid,x.flatten(),\
                (xp,yp),method=method)

    def time_step(self):

        # 1. Accelerate the velocity fields.
        self.U.x += self.A.x * self.dt * self.rho
        self.U.y += self.A.y * self.dt * self.rho

        # 2. Advect the velocity fields with semi-lagrangian method
        # Find where would the particle been at the previous time step
        # and apply periodic boundary conditions.
        xp = self.pbc(self.X.x - self.U.x * self.dt)
        yp = self.pbc(self.X.y - self.U.y * self.dt)

        # Interpolate values at xp,yp back to orignial grid
        self.U.x = self.advect(self.U.x,xp,yp)
        self.U.y = self.advect(self.U.y,xp,yp)
        self.rho = self.advect(self.rho,xp,yp)

        # 3. Move to wave space to apply viscosity and mass conservation
        u = fftshift(fftn(self.U.x))
        v = fftshift(fftn(self.U.y))

        # Mass conservation comes from projecting U in FS onto
        # unit rotational vector (-y,x)/r
        # eta is multiplied in wave space to attenuate high
        # frequency components, this is viscosity

        u_n = self.eta *  (u * (1. - self.Xs.x**2 / self.r2s)\
                - v * self.Xs.x * self.Xs.y / self.r2s)
        v_n = self.eta *  (v * (1. - self.Xs.y**2 / self.r2s)\
                - u * self.Xs.x * self.Xs.y / self.r2s)

        # Return to space
        self.U.x = ifftn(ifftshift(u_n)).real
        self.U.y = ifftn(ifftshift(v_n)).real
        # hack, to prevent a systematic drift in velocity
        self.U.x -= np.mean(self.U.x)
        self.U.y -= np.mean(self.U.y)
        # Another hack to dial back the density, avoids having too much material and
        # saturating the color map
        self.rho *= .995

    def add_particle(self,x0,y0,u0,v0,r):
        """
        To be used heavily, inputs are:
            x0 - x coordinate of center
            y0 - y coordinate of center
            u0 - x velocity of new particle
            v0 - y velocity of new particle
            r  - radius of new particle
        you may have to make changes to this function!
        """
        t = ((np.sqrt((self.X.x-x0)**2\
                 +(self.X.y-y0)**2))<r).astype(float)
        self.U.x += t * u0
        self.U.y += t * v0
        self.rho += t
        return t

    def set_force(self,ax,ay):
        """
        Simple two arguement means of setting acceleration fields.
        Suitable for buyoance, gravity or other simple forces.
        """
        self.A.x = ax
        self.A.y = ay


# There is a bug I haven't tracked that makes certain values of N error out
# 52 and 40 work, and are reasonable responsive. Others can be found by trial
# and error
'''
fs = FluidSimulator(L=1.,N=40,visc=0.001,dt=0.25)
# Buoyancy, negative is up in imshow
fs.set_force(0,-.1)

# For good effect, start by using a counter and every 30 or so
# time steps add a new particle by calling fs.add_particle().
# use random radius between .05 and .25.
# make sure you have a loop that includes a call to fs.time_step()
# After succeeding consider using mouse inputs to generate particles.
# Look into matplot lib animations (maybe?) There are many ways to
# succeed.
'''
