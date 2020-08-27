"""
Cueing Group Analysis Winter 2019
===============================

"""

###################################################################################################
# Setup
# -----------------------------

# Standard Pythonic imports
import os,sys,glob,numpy as np, pandas as pd
import scipy
from collections import OrderedDict
import warnings
warnings.filterwarnings('ignore')
from matplotlib import pyplot as plt
import matplotlib.patches as patches

# MNE functions
from mne import Epochs, find_events, concatenate_raws
from mne.time_frequency import tfr_morlet

# EEG-Noteooks functions
from eegnb.analysis.utils import load_data,plot_conditions
from eegnb.datasets import fetch_dataset

# sphinx_gallery_thumbnail_number = 1

###################################################################################################
# Load the data
# -----------------------------

eegnb_data_path = os.path.join(os.path.expanduser('~/'),'.eegnb', 'data')
cueing_data_path = os.path.join(eegnb_data_path, 'visual-cueing', 'kylemathlab_dev')

# If dataset hasn't been downloaded yet, download it
if not os.path.isdir(cueing_data_path):
      fetch_dataset(data_dir=eegnb_data_path, experiment='visual-cueing', site='kylemathlab_dev')


###################################################################################################
# Put the data into MNE Epochs
# -----------------------------
#
# Fall 2018
# subs = [101, 102, 103, 104, 105, 106, 108, 109, 110, 111, 112,
#         202, 203, 204, 205, 207, 208, 209, 210, 211, 
#         301, 302, 303, 304, 305, 306, 307, 308, 309]
#
# Winter 2019
subs = [1101, 1102, 1103, 1104, 1105, 1106, 1108, 1109, 1110,
        1202, 1203, 1205, 1206, 1209, 1210, 1211, 1215,
        1301, 1302, 1313, 
        1401, 1402, 1403, 1404, 1405,  1408, 1410, 1411, 1412, 1413, 1413, 1414, 1415, 1416]
#
# Both
# subs = [101, 102, 103, 104, 105, 106, 108, 109, 110, 111, 112,
#         202, 203, 204, 205, 207, 208, 209, 210, 211, 
#         301, 302, 303, 304, 305, 306, 307, 308, 309,
#         1101, 1102, 1103, 1104, 1105, 1106, 1108, 1109, 1110,
#         1202, 1203, 1205, 1206, 1209, 1210, 1211, 1215,
#         1301, 1302, 1313, 
#         1401, 1402, 1403, 1404, 1405,  1408, 1410, 1411, 1412, 1413, 1413, 1414, 1415, 1416]
#
#
# placeholders to add to for each subject
diff_out = []
Ipsi_out = []
Contra_out = []
Ipsi_spectra_out = []
Contra_spectra_out = []
diff_spectra_out = []
ERSP_diff_out = []
ERSP_Ipsi_out = []
ERSP_Contra_out = []

frequencies =  np.linspace(6, 30, 100, endpoint=True)
wave_cycles = 6

# time frequency window for analysis
f_low = 7 # Hz
f_high = 10
f_diff = f_high-f_low
 
t_low = 0 # s
t_high = 1
t_diff = t_high-t_low

bad_subs= [6, 7, 13, 26]
really_bad_subs = [11, 12, 19]
sub_count = 0    
    
    
    
for sub in subs:
    print(sub)
    
    sub_count += 1

    
    if (sub_count in really_bad_subs):
        rej_thresh_uV = 90
    elif (sub_count in bad_subs):
        rej_thresh_uV = 90
    else:
        rej_thresh_uV = 90

    rej_thresh = rej_thresh_uV*1e-6
    
    
    # Load both sessions
    raw = load_data(sub,1, # subject, session
                    experiment='visual-cueing',site='kylemathlab_dev',device_name='muse2016',
                    data_dir = eegnb_data_path)
                
    raw.append(
          load_data(sub,2, # subject, session
                    experiment='visual-cueing', site='kylemathlab_dev', device_name='muse2016',
                    data_dir = eegnb_data_path))
    

    # Filter Raw Data
    raw.filter(1,30, method='iir')

    #Select Events
    events = find_events(raw)
    event_id = {'LeftCue': 1, 'RightCue': 2}
    epochs = Epochs(raw, events=events, event_id=event_id, 
                    tmin=-1, tmax=2, baseline=(-1, 0), 
                    reject={'eeg':rej_thresh}, preload=True,
                    verbose=False, picks=[0, 3])
    print('Trials Remaining: ' + str(len(epochs.events)) + '.')

    # Compute morlet wavelet
    # Left Cue
    tfr, itc = tfr_morlet(epochs['LeftCue'], freqs=frequencies, 
                          n_cycles=wave_cycles, return_itc=True)
    tfr = tfr.apply_baseline([-1,-.5],mode='mean')
    power_Ipsi_TP9 = tfr.data[0,:,:]
    power_Contra_TP10 = tfr.data[1,:,:]

    # Right Cue
    tfr, itc = tfr_morlet(epochs['RightCue'], freqs=frequencies, 
                          n_cycles=wave_cycles, return_itc=True)
    tfr = tfr.apply_baseline([-1,-.5],mode='mean')
    power_Contra_TP9 = tfr.data[0,:,:]
    power_Ipsi_TP10 = tfr.data[1,:,:]

    # Compute averages Differences
    power_Avg_Ipsi =   (power_Ipsi_TP9+power_Ipsi_TP10)/2;
    power_Avg_Contra = (power_Contra_TP9+power_Contra_TP10)/2;
    power_Avg_Diff = power_Avg_Ipsi-power_Avg_Contra;
    
    #output data into array
    times = epochs.times
    Ipsi_out.append(np.mean(power_Avg_Ipsi[np.argmax(frequencies>f_low):
                                           np.argmax(frequencies>f_high)-1,
                            np.argmax(times>t_low):np.argmax(times>t_high)-1 ]
                           )
                   )            
    Ipsi_spectra_out.append(np.mean(power_Avg_Ipsi[:,np.argmax(times>t_low):
                                                   np.argmax(times>t_high)-1 ],1
                                   )
                           )
        
    Contra_out.append(np.mean(power_Avg_Contra[np.argmax(frequencies>f_low):
                                               np.argmax(frequencies>f_high)-1,
                            np.argmax(times>t_low):np.argmax(times>t_high)-1 ]
                             )
                     )
    
    Contra_spectra_out.append(np.mean(power_Avg_Contra[:,np.argmax(times>t_low):
                                                       np.argmax(times>t_high)-1 ],1))
    
    
    diff_out.append(np.mean(power_Avg_Diff[np.argmax(frequencies>f_low):
                                           np.argmax(frequencies>f_high)-1,
                            np.argmax(times>t_low):np.argmax(times>t_high)-1 ]
                           )
                   )
    diff_spectra_out.append(np.mean(power_Avg_Diff[:,np.argmax(times>t_low):
                                                   np.argmax(times>t_high)-1 ],1
                                   )
                           )
    
    #save the spectrograms to average over after
    ERSP_diff_out.append(power_Avg_Diff)
    ERSP_Ipsi_out.append(power_Avg_Ipsi)
    ERSP_Contra_out.append(power_Avg_Contra)
    
    
###################################################################################################
# Combine subjects
# ----------------------------

#average spectrograms
GrandAvg_diff = np.nanmean(ERSP_diff_out,0)
GrandAvg_Ipsi = np.nanmean(ERSP_Ipsi_out,0)
GrandAvg_Contra = np.nanmean(ERSP_Contra_out,0)

#average spectra
GrandAvg_spec_Ipsi = np.nanmean(Ipsi_spectra_out,0)
GrandAvg_spec_Contra = np.nanmean(Contra_spectra_out,0)
GrandAvg_spec_diff = np.nanmean(diff_spectra_out,0)

#error bars for spectra (standard error)
num_good = len(diff_out) - sum(np.isnan(diff_out))   
GrandAvg_spec_Ipsi_ste = np.nanstd(Ipsi_spectra_out,0)/np.sqrt(num_good)
GrandAvg_spec_Contra_ste = np.nanstd(Contra_spectra_out,0)/np.sqrt(num_good)
GrandAvg_spec_diff_ste = np.nanstd(diff_spectra_out,0)/np.sqrt(num_good)

###################################################################################################

#Plot Spectra error bars
fig, ax = plt.subplots(1)
plt.errorbar(frequencies,GrandAvg_spec_Ipsi,yerr=GrandAvg_spec_Ipsi_ste)
plt.errorbar(frequencies,GrandAvg_spec_Contra,yerr=GrandAvg_spec_Contra_ste)
plt.legend(('Ipsi','Contra'))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power (uV^2)')   
plt.hlines(0,3,33)

###################################################################################################

#Plot Spectra Diff error bars
fig, ax = plt.subplots(1)
plt.errorbar(frequencies,GrandAvg_spec_diff,yerr=GrandAvg_spec_diff_ste)
plt.legend('Ipsi-Contra')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power (uV^2)')   
plt.hlines(0,3,33)

###################################################################################################
#
# Grand Average Ipsi
plot_max = np.max([np.max(np.abs(GrandAvg_Ipsi)), np.max(np.abs(GrandAvg_Contra))])  
fig, ax = plt.subplots(1)
im = plt.imshow(GrandAvg_Ipsi,
           extent=[times[0], times[-1], frequencies[0], frequencies[-1]],
           aspect='auto', origin='lower', cmap='coolwarm', vmin=-plot_max, vmax=plot_max)
plt.xlabel('Time (sec)')
plt.ylabel('Frequency (Hz)')
plt.title('Power Ipsi')
cb = fig.colorbar(im)
cb.set_label('Power')
# Create a Rectangle patch
rect = patches.Rectangle((t_low,f_low),t_diff,f_diff,linewidth=1,edgecolor='k',facecolor='none')
# Add the patch to the Axes
ax.add_patch(rect)
#
##e#################################################################################################
#
# Grand Average Contra
#
fig, ax = plt.subplots(1)
im = plt.imshow(GrandAvg_Contra,
           extent=[times[0], times[-1], frequencies[0], frequencies[-1]],
           aspect='auto', origin='lower', cmap='coolwarm', vmin=-plot_max, vmax=plot_max)
plt.xlabel('Time (sec)')
plt.ylabel('Frequency (Hz)')
plt.title('Power Contra')
cb = fig.colorbar(im)
cb.set_label('Power')
# Create a Rectangle patch
rect = patches.Rectangle((t_low,f_low),t_diff,f_diff,linewidth=1,edgecolor='k',facecolor='none')
# Add the patch to the Axes
ax.add_patch(rect)
#
###################################################################################################
#
# Grand Average Ipsi-Contra Difference
#
plot_max_diff = np.max(np.abs(GrandAvg_diff))
fig, ax = plt.subplots(1)
im = plt.imshow(GrandAvg_diff,
           extent=[times[0], times[-1], frequencies[0], frequencies[-1]],
           aspect='auto', origin='lower', cmap='coolwarm', vmin=-plot_max_diff, vmax=plot_max_diff)
plt.xlabel('Time (sec)')
plt.ylabel('Frequency (Hz)')
plt.title('Power Difference Ipsi-Contra')
cb = fig.colorbar(im)
cb.set_label('Ipsi-Contra Power')
# Create a Rectangle patch
rect = patches.Rectangle((t_low,f_low),t_diff,f_diff,linewidth=1,edgecolor='k',facecolor='none')
# Add the patch to the Axes
ax.add_patch(rect)

###################################################################################################
# Compute t test
# ----------------------------

num_good = len(diff_out) - sum(np.isnan(diff_out))

[tstat, pval] = scipy.stats.ttest_ind(diff_out,np.zeros(len(diff_out)),nan_policy='omit')
print('Ipsi Mean: '+  str(np.nanmean(Ipsi_out))) 
print('Contra Mean: '+  str(np.nanmean(Contra_out))) 
print('Mean Diff: '+  str(np.nanmean(diff_out))) 
print('t(' + str(num_good-1) + ') = ' + str(round(tstat,3)))
print('p = ' + str(round(pval,3)))

###################################################################################################
# Save average powers ipsi and contra
# ----------------------------

print(diff_out)
raw_data = {'Ipsi Power': Ipsi_out, 
        'Contra Power': Contra_out}
df = pd.DataFrame(raw_data, columns = ['Ipsi Power', 'Contra Power'])
print(df)
df.to_csv('375CueingEEG.csv')
print('Saved subject averages for each condition to 375CueingEEG.csv file in present directory')

###################################################################################################
# Save spectra
# ----------------------------

df = pd.DataFrame(Ipsi_spectra_out,columns=frequencies)
print(df)
df.to_csv('375CueingIpsiSpec.csv')

df = pd.DataFrame(Contra_spectra_out,columns=frequencies)
df.to_csv('375CueingContraSpec.csv')
print('Saved Spectra to 375CueingContraSpec.csv file in present directory')


