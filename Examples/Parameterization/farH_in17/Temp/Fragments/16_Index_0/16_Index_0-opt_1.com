%RWF=/scratch/bdw2292/Gau-16_Index_0-farH_in17/,16.666666666666668GB
%Nosave
%Chk=16_Index_0-opt_1.chk
%Mem=8.333333333333334GB
%Nproc=1
#P opt=(Cartesian,maxcycles=400) MP2/6-31G* MaxDisk=16.666666666666668GB 

16_Index_0 Gaussian OPT Calculation on node44.bme.utexas.edu

0 1
 C    0.907600    0.010000   -0.041700
 N    2.325200    0.076800   -0.091700
 C    0.158600    1.149600    0.168500
 C    0.208500   -1.170800   -0.196600
 C   -1.221000    1.125200    0.223600
 C   -1.177100   -1.196400   -0.141500
 C   -1.916500   -0.055000    0.068600
 H    2.894800    0.011500   -0.960400
 H    0.661300    2.098300    0.295500
 H    0.807700   -2.061000   -0.361400
 H   -1.787800    2.040000    0.390800
 H   -1.698800   -2.132500   -0.265600
 H    2.843600    0.200400    0.803400
 H   -3.006100   -0.096200    0.108700

