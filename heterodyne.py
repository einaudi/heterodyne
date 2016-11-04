import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

def mean( l ):
    sum = 0.
    for item in l:
        sum += float(item)
    return sum/float(len(l))

# -----DATA READING-----

try:
    with open( './data/C1grey 0deg00000.txt', 'r' ) as f:
        input_data = f.readlines()[5:]
except IOError:
    print 'Could not open the file'
    quit()

try:
    with open( './data/C2grey 0deg00000.txt', 'r' ) as f:
        reference_data = f.readlines()[5:]
except IOError:
    print 'Could not open the file'
    quit()
if not len(reference_data) == len(input_data):
    print 'CH1 and CH2 data length not the same'
    quit()

edge = 0.001
start_point = 0.
T = 2e-6
wdth = 0.4*T
delay = 0.03e-6
flag = True
reference_signal = list()
input_signal = list()
time = list()
time = list()

for i in range( len(input_data) ):
    try:
        line_data = input_data[i].strip().split(',')
        ref_data = reference_data[i].strip().split(',')
    except:
        print 'Wrong data format'
        quit()
    if flag and float(line_data[1]) > edge:
        start_point = float(line_data[0])
        flag = False
    if float( line_data[0] ) >= start_point + delay and float( line_data[0] ) <= start_point + delay + wdth:
        time.append( float(line_data[0])*1e6 ) # tim eunit in this list is us
        input_signal.append( float(line_data[1]) )
        reference_signal.append( float(ref_data[1]) )


sampling = len(time)/( max(time) - min(time) )*1e6
print 'Sampling: \t', int(sampling), 'Hz'

# -----PLOTTING PART 1-----

plt.figure(1)

plt.subplot(311)
plt.plot( time, input_signal, 'b-', linewidth=1.5 )
plt.title( 'Input signal' )
#plt.xlabel( 'Time [s]' )
plt.ylabel( 'Amplitude [AU]' )
plt.margins(0, 0.1)

# -----HIGHPASS FILTER-----
# frequencies in Hz

high_cutoff = 50e6
b, a = signal.butter( 8, 2 * high_cutoff/sampling, btype='high' )
high_signal = signal.filtfilt( b, a, input_signal )
high_ref_signal = signal.filtfilt( b, a, np.asarray(reference_signal) )

norm_sig = max(high_signal)
norm_ref = max(high_ref_signal)

# -----PLOTTING PART 2-----

plt.subplot(312)
plt.plot( time, high_signal, 'b-', linewidth=1.5 )
plt.title( 'High-filtered signal' )
#plt.xlabel( 'Time [us]' )
plt.ylabel( 'Amplitude [AU]' )
plt.margins(0, 0.1)

# -----MIXING AND LOWPASS FILTER-----
# frequencies in Hz

mixed_signal = [ high_signal[i] * high_ref_signal[i]/norm_sig/norm_ref for i in range( len(high_signal ) ) ]

low_cutoff = 100e6
b, a = signal.butter( 8, 2 * low_cutoff/sampling, btype='low' )
output_signal = signal.filtfilt( b, a, mixed_signal)

mean = mean(output_signal)
print 'Mean:\t', round( mean, 2 )
try:
    shift = round( np.arccos( mean ), 2 )
    print 'Phase shift:\t', shift, '=', round( shift/np.pi, 2 ), 'pi'
except RuntimeWarning:
    print 'Mean output signal value not between -1 and 1'
    
# -----PLOTTING PART 3-----

plt.subplot(313)
plt.plot( time, output_signal, 'b-', linewidth=1.5 )
plt.title( 'Output signal' )
plt.xlabel( 'Time [us]' )
plt.ylabel( 'Amplitude [AU]' )
plt.margins(0, 0.1)
plt.plot( (time[0],time[-1]), (mean,mean), 'g-') # draw line y = mean

plt.show()
