
# coding: utf-8

# In[1]:

from __future__ import division
from __future__ import print_function

from matplotlib.pylab import *
from numpy import *
from scipy import signal

import warnings

warnings.filterwarnings('ignore')


# In[2]:

def nCr(n,r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)


## Synchronized Swept Sine Definition

# In[3]:

f1 = 10        # start frequency
f2 = 12000       # end frequency
fs = 96000      # sampling frequency
T = 5          # approximative time duration
fade = [48000, 480]   # samlpes to fade-in and fade-out the input signal


# In[4]:

# -- generation of the signal
L = 1/f1 * round(T*f1/log(f2/f1))   # parametre of exp.swept-sine
T_hat = L*log(f2/f1)                # the real time (a little bit different of T due to the synchronisation)

t = arange(0,round(fs*T_hat-1)/fs,1/fs)  # time axis
s = sin(2*pi*f1*L*(exp(t/L)-1))            # generated swept-sine signal


# In[5]:

# fade-in the input signal
if fade[0]>0:
    s[0:fade[0]] = s[0:fade[0]] * ((-cos(arange(fade[0])/fade[0]*pi)+1) / 2)

# fade-out the input signal
if fade[1]>0:
    s[-fade[1]:] = s[-fade[1]:] *  ((cos(arange(fade[1])/fade[1]*pi)+1) / 2)



# In[6]:

_,ax1 = subplots()
ax1.plot(t,s)
ax1.set_title('Excitation Synchronized Swept-Sine signal')
ax1.set_xlabel('time [s]')
ax1.axis(ymin=-1.2, ymax=1.2)
show()


## Nonlinear System Definition

# In[7]:

len_Hammer = 2**12 # Length of the Hammerstein kernels (in samples)


# In[8]:

# the ARMA filters definition (ARMA order = 2, number of filters = N = 4)
A = [[1.0,-1.8996,0.9025],[1.0,-1.9075,0.9409],[1.0,-1.8471,0.8649],[1.0,-1.7642,0.8464]]
B = [[1.0,-1.9027,0.9409],[1.0,-1.8959,0.9025],[0.5,-0.9176,0.4512],[0.1,-0.1836,0.0846]]
N = 4              # order of nonlinearities


# In[9]:

# Computation of the kernels
G_theo = zeros((N,int(len_Hammer/2+1)),dtype=complex128)
for k in range(0,N):
    w,G_theo[k,:] = signal.freqz(B[k],A[k],int(len_Hammer/2+1))



# In[10]:

_,((ax1, ax2), (ax3, ax4)) = subplots(2, 2, figsize=(12,7))

axx = [ax1,ax2,ax3,ax4]
ylimits = [(-15,25),(-15,10),(-15,10),(-40,-10)]
legend_pos = [1,2,1,2]
titles = ['1st','2nd','3rd','4th']


for k in range(4):
    l1 = axx[k].semilogx(w/pi*fs/2,20*log10(abs(G_theo[k,:])), label='Magnitude')
    axx[k].set_title('Hammerstein model - ' + titles[k] + ' order')
    axx[k].set_xlabel('frequency [Hz]')
    axx[k].set_ylabel('Magnitude [dB]', color='b')
    axx[k].set_xlim(100,5000)
    axx[k].set_ylim(ylimits[k])
    for tl in axx[k].get_yticklabels():
        tl.set_color('b')
    axx[k].grid()

    ax12 = axx[k].twinx()
    l2 = ax12.semilogx(w/pi*fs/2,angle(G_theo[0,:]),'g', label='Phase')
    ax12.set_ylabel('Angle [rad]', color='g')
    ax12.set_xlim(100,5000)
    ax12.set_ylim(-pi,pi)
    for tl in ax12.get_yticklabels():
        tl.set_color('g')

    lns = l1 + l2
    labs = [l.get_label() for l in lns]
    axx[k].legend(lns, labs, loc=legend_pos[k])


subplots_adjust(wspace = 0.3, hspace = 0.3)



show()


## Nonlinear system response to the swept sine signal

# In[11]:

# -- Nonlinear System response
y = 0
for n in range(0,N):
    y = y + signal.lfilter(B[n],A[n],append(s**(n+1), zeros((1,len_Hammer-1))))


# In[12]:

t_y = arange(len(y))/fs
_,ax2 = subplots()
ax2.plot(t_y,y)
ax2.set_title('Response of the Nonlinear System to the Sychronized Swept-Sine Signal')
ax2.set_xlabel('time [s]')
show()

## Nonlinear convolution

# In[13]:

y = y - mean(y)   # signal must not contain the mean value


# In[14]:

fft_len = int(2**ceil(log2(len(y))))
Y = fft.rfft(y,fft_len)/fs


# In[15]:

f_osa = linspace(0, fs/2, num=fft_len/2+1) # frequency axis


# In[16]:

# definition of the inferse filter in spectral domain
# (A.Novak IEEE paper "Nonlinear System Identification Using Exponential
# Swept-Sine Signal",  Eq. (30) and (31) leading to Eq. (26) for the amplitude
# and (9) for the phase)
SI = 2*sqrt(f_osa/L)*exp(1j*(2*pi*L*f_osa*(f1/f_osa + log(f_osa/f1) - 1) + pi/4))
SI[0] = 0j


# In[17]:

# first Nyquist zone
H = Y*SI;

# ifft
h = fft.irfft(H)


# In[18]:

plot_shift = -50000
t_h = -(arange(len(h),0,-1)+plot_shift)/fs
_,(ax1, ax2) = subplots(1, 2,figsize=(12,5),sharey=True)

ax1.plot(t_h,roll(h,plot_shift))
ax1.set_title('Output of the Nonlinear Convolution')
ax1.set_xlabel('time [s]')
ax1.autoscale(enable=True, axis='x', tight=True)

ax2.plot(-(arange(600,0,-1)-500)/fs*1000,roll(h,-500)[-600:])
ax2.set_title('Zoom to the linear kernel')
ax2.set_xlabel('time [ms]')
ax2.autoscale(enable=True, axis='x', tight=True)

show()


# In[19]:

dt = L*log(arange(1,N+1))*fs  # positions of higher orders up to N
dt_rem = dt - around(dt) # The time lags may be non-integer in samples, the non integer delay must be applied later


# In[20]:

posun = round(len_Hammer/2)          # number of samples to make an artificail delay
h_pos = hstack((h, h[0:posun + len_Hammer - 1]))  # periodic impulse response


# In[21]:

# separation of higher orders
hs = zeros((N,len_Hammer))

axe_w = linspace(0, pi, num=len_Hammer/2+1); # frequency axis
for k in range(N):
    hs[k,:] = h_pos[len(h)-round(dt[k])-posun-1:len(h)-round(dt[k])-posun+len_Hammer-1]
    H_temp = fft.rfft(hs[k,:])

    # Non integer delay application
    H_temp = H_temp * exp(-1j*dt_rem[k]*axe_w)
    hs[k,:] = fft.irfft(H_temp)

# Higher Harmonics
Hs = fft.rfft(hs)


# In[22]:

_,ax1 = subplots(figsize=(5,3.5))
ax1.semilogx(axe_w/(pi)*fs/2,20*log10(abs(Hs.transpose())))
ax1.set_title('Higher Harmonics')
ax1.set_xlabel('frequency [Hz]')
ax1.set_xlim(100,5000)
ax1.set_ylim(-80,40)
ax1.legend(('1st harmonic','2nd harmonic','3rd harmonic','4th harmonic'),loc=3)
ax1.grid()
show()



## Conversion to Hammerstein model

# In[23]:

# Harmonics to Hammerstein Matrix generation
C = zeros((N,N),dtype=complex128)
for n in range(N):
    for m in range(N):
        if ( (n>=m) and ((n+m)%2==0) ):
            C[m,n] = (((-1 + 0j)**(2*(n+1)-m/2))/(2**n)) * nCr((n+1),(n-m)/2)

Gs = dot(linalg.inv(C),Hs) # conversion
gs = zeros((N,len_Hammer))

# complex matrix C ... conversion to real kernels
for k in range(N):
    gs[k,:] = fft.irfft(Gs[k,:])

# kernels into frequency domain with phase shift
Gs = fft.rfft(roll(gs,-int(len_Hammer/2+1),axis=1))


# In[24]:

_,((ax1, ax2), (ax3, ax4)) = subplots(2, 2, figsize=(12,7))

axx = [ax1,ax2,ax3,ax4]
ylimits = [(-15,25),(-15,15),(-15,15),(-40,-10)]
legend_pos = [1,2,1,2]
titles = ['1st','2nd','3rd','4th']

for k in range(4):
    l1 = axx[k].semilogx(axe_w/pi*fs/2,20*log10(abs(Gs[k,:])), label='Estimated (magnitude)')
    l2 = axx[k].semilogx(axe_w/pi*fs/2,20*log10(abs(G_theo[k,:])),'r--', label='Theoretical (magnitude)')
    axx[k].set_title('Hammerstein model - ' + titles[k] + ' order')
    axx[k].set_xlabel('frequency [Hz]')
    axx[k].set_ylabel('Magnitude [dB]', color='b')
    axx[k].set_xlim(100,10000)
    axx[k].set_ylim(ylimits[k])
    for tl in axx[k].get_yticklabels():
        tl.set_color('b')
    axx[k].grid()

    ax12 = axx[k].twinx()
    l3 = ax12.semilogx(axe_w/pi*fs/2,angle(Gs[0,:]),'g', label='Estimated (phase)')
    l4 = ax12.semilogx(axe_w/pi*fs/2,angle(G_theo[0,:]),'k--', label='Theoretical (phase)')
    ax12.set_ylabel('Angle [rad]', color='g')
    ax12.set_xlim(100,10000)
    ax12.set_ylim(-pi,pi)
    for tl in ax12.get_yticklabels():
        tl.set_color('g')

    lns = l1 + l2 + l3 + l4
    labs = [l.get_label() for l in lns]
    axx[k].legend(lns, labs, loc=legend_pos[k])


subplots_adjust(wspace = 0.3, hspace = 0.3)



show()
