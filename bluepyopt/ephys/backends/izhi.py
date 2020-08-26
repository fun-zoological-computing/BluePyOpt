
from quantities import mV, ms, s, V
import sciunit
from neo import AnalogSignal
import neuronunit.capabilities as cap
import numpy as np
from .base import *
import quantities as qt
#import matplotlib as mpl
try:
    import asciiplotlib as apl
except:
    pass
import numpy
voltage_units = mV

from elephant.spike_train_generation import threshold_detection


from numba import jit
import cython
@jit
def get_vm(C=89.7960714285714, a=0.01, b=15, c=-60, d=10, k=1.6, vPeak=(86.364525297619-65.2261863636364), vr=-65.2261863636364, vt=-50, dt=0.010, Iext=[]):
    '''
    dt determined by
    Apply izhikevich equation as model
    This function can't get too pythonic (functional), it needs to be a simple loop for
    numba/jit to understand it.
    '''
    N = len(Iext)

    v = np.zeros(N)
    u = np.zeros(N)
    v[0] = vr
    for m in range(0,N-1):
        vT = v[m]+ (dt/2) * (k*(v[m] - vr)*(v[m] - vt)-u[m] + Iext[m])/C;
        v[m+1] = vT + (dt/2)  * (k*(v[m] - vr)*(v[m] - vt)-u[m] + Iext[m])/C;
        u[m+1] = u[m] + dt * a*(b*(v[m]-vr)-u[m]);
        u[m+1] = u[m] + dt * a*(b*(v[m+1]-vr)-u[m]);
        if v[m+1]>= vPeak:# % a spike is fired!
            v[m] = vPeak;# % padding the spike amplitude
            v[m+1] = c;# % membrane voltage reset
            u[m+1] = u[m+1] + d;# % recovery variable update


    return v
'''
def get_vm(C=89.7960714285714, a=0.01, b=15, c=-60, d=10, k=1.6, vPeak=(86.364525297619-65.2261863636364), vr=-65.2261863636364, vt=-50, dt=0.010, Iext=[]):

    M = N = len(Iext)
    #N = size(current,1);
    #M = size(current,2);
    delta = 0.5; % resolution of simulation

    #%% Neuron Parameters
    C = 281;# % capacitance in pF ... this is 281*10^(-12) F
    g_L = 30;# % leak conductance in nS
    E_L = -70.6;# % leak reversal potential in mV ... this is -0.0706 V
    delta_T = 2;# % slope factor in mV
    V_T = -50.4;# % spike threshold in mV
    tau_w = 144;# % adaptation time constant in ms
    V_peak = 20;# % when to call action potential in mV
    b = 0.0805;# % spike-triggered adaptation

    #loadPhysicalConstants;

    #%% Init variables
    V = zeros(N,M);
    w = zeros(N,M);

    #%% Boltzmann distributed initial conditions
    sigma_sq = 1/(thermoBeta*(C*10^(-12))); % make sure C is in F
    #% This variance is on the order of 1.5*10^(-11)
    V[1,:] = E_L/1000 + sqrt(sigma_sq)*randn(1,M); % make sure E_L is in V
    V[1,:] = V(1,:)*1000; % convert initial conditions into mV
    w[1,:] = 0; % initial condition is w = 0

    for n in range(0,N-1):

        V[n+1,:] = V[n,:] + (delta/C)*(spiking(V[n,:],g_L,E_L,delta_T,V_T)-w[n,:]+ current[n+1,:]);
        w[n+1,:] = w[n,:] + (delta/tau_w)*(a*(V[n,:]-E_L) - w[n,:]);
        
        #% spiking mechanism
        alreadySpiked = (V[n,:] == V_peak);
        V[n+1,alreadySpiked] = E_L;
        w[n+1,alreadySpiked] = w[n,alreadySpiked] + b;

        justSpiked = (V[n+1,:] > V_peak);
        V[n+1,justSpiked] = V_peak;
 
    return V
'''

class IZHIBackend(Backend):

    name = 'IZHI'

    def init_backend(self, attrs=None, cell_name='alice',
                     current_src_name='hannah', DTC=None,
                     debug = False):
        super(IZHIBackend,self).init_backend()
        self.model._backend.use_memory_cache = False
        self.current_src_name = current_src_name
        self.cell_name = cell_name
        self.vM = None
        self.attrs = attrs
        self.debug = debug
        self.temp_attrs = None
        self.default_attrs = {'C':89.7960714285714, 'a':0.01, 'b':15, 'c':-60, 'd':10, 'k':1.6, 'vPeak':(86.364525297619-65.2261863636364), 'vr':-65.2261863636364, 'vt':-50, 'dt':0.010, 'Iext':[]}

        if type(attrs) is not type(None):
            self.attrs = attrs
            # set default parameters anyway.
        if type(DTC) is not type(None):
            if type(DTC.attrs) is not type(None):
                self.set_attrs(**DTC.attrs)
            if hasattr(DTC,'current_src_name'):
                self._current_src_name = DTC.current_src_name
            if hasattr(DTC,'cell_name'):
                self.cell_name = DTC.cell_name

    def get_spike_count(self):
        thresh = threshold_detection(self.vM)
        return len(thresh)


    def set_stop_time(self, stop_time = 650*pq.ms):
        """Sets the simulation duration
        stopTimeMs: duration in milliseconds
        """
        self.tstop = float(stop_time.rescale(pq.ms))


    def get_membrane_potential(self):
        """Must return a neo.core.AnalogSignal.
        And must destroy the hoc vectors that comprise it.
        """

        if type(self.vM) is type(None):
            v = get_vm(**self.attrs)

            self.vM = AnalogSignal(v,
                                units=pq.mV,
                                sampling_period=0.01*pq.ms)

        return self.vM

    def set_attrs(self, attrs):
        self.attrs = attrs
        self.model.attrs.update(attrs)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def inject_square_current(self, current):#, section = None, debug=False):
        """Inputs: current : a dictionary with exactly three items, whose keys are: 'amplitude', 'delay', 'duration'
        Example: current = {'amplitude':float*pq.pA, 'delay':float*pq.ms, 'duration':float*pq.ms}}
        where \'pq\' is a physical unit representation, implemented by casting float values to the quanitities \'type\'.
        Description: A parameterized means of applying current injection into defined
        Currently only single section neuronal models are supported, the neurite section is understood to be simply the soma.

        """
        attrs = copy.copy(self.model.attrs)

        if 'injected_square_current' in current.keys():
            c = current['injected_square_current']
        else:
            c = current
        amplitude = float(c['amplitude'])#*10.0#*1000.0 #this needs to be in every backends
        duration = float(c['duration'])#/dt#/dt.rescale('ms')
        delay = float(c['delay'])#/dt#.rescale('ms')
        #if 'sim_length' in c.keys():
        #    sim_length = c['sim_length']#.simplified
        tMax = delay + duration + 200.0#/dt#*pq.ms

        self.set_stop_time(tMax*pq.ms)
        tMax = self.tstop
        """
        if str('dt') in attrs:
            if np.isnan(tMax/attrs['dt']):
                if np.isnan(attrs['dt']):
                   attrs['dt'] = 0.01
                   N = int(tMax/attrs['dt'])

            else:
               N = int(tMax/attrs['dt'])
        else:
        """
        attrs['dt'] = 0.01
        NORMAL = True
        if NORMAL == True:
            N = int(tMax/attrs['dt'])
        else:
            print('adding in larger N seems to artificially dilate the width of neural events')
            N = int(tMax/attrs['dt'])*100

        Iext = np.zeros(N)
        delay_ind = int((delay/tMax)*N)
        duration_ind = int((duration/tMax)*N)

        Iext[0:delay_ind-1] = 0.0
        Iext[delay_ind:delay_ind+duration_ind-1] = amplitude
        Iext[delay_ind+duration_ind::] = 0.0

        attrs['Iext'] = Iext
        self.attrs = attrs

        v = get_vm(**self.attrs)

        self.model.attrs.update(attrs)

        self.vM = AnalogSignal(v,
                            units=pq.mV,
                            sampling_period=0.01*pq.ms)

        #(self.vM.times[-1],c['delay']+c['duration']+200*pq.ms)
        #assert self.vM.times[-1] == (c['delay']+c['duration']+200*pq.ms)

        return self.vM

    def _backend_run(self):
        results = {}
        #print(self.attrs,'is attributes the empty list?')
        if len(self.attrs) > 1:
            v = get_vm(**self.attrs)
        else:
            v = get_vm(self.attrs)

        self.vM = AnalogSignal(v,
                               units = voltage_units,
                               sampling_period = 0.01*pq.ms)
        results['vm'] = self.vM.magnitude
        results['t'] = self.vM.times
        results['run_number'] = results.get('run_number',0) + 1
        return results
