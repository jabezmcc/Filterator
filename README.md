# Filterator
A program to simulate the action of a digital electronic filter on a signal. Input signal is specified by size in volts, frequency, and waveform (sine, square or triangle).  Size can be given as amplitude, rms, or peak to peak. Filter is specified by the type (low-pass or high pass, Butterworth or Bessel), corner frequency, and number of poles.  The Bode plot of the filter is shown in the lower left, and the effect on the signal is shown in the lower right.  Amplitude, rms and peak-to-peak outputs are calculated numerically and displayed above the output graph.    
![image](https://user-images.githubusercontent.com/74684073/143722143-2d407326-c696-40a6-9bfe-dc0b9e149253.png)

<h4>Installation and usage</h4>
Download all files and save in an appropriate directory. Run from  command line via <code>python filterator3.py</code>. Program was written and tested under linux using Python 3.9.7. Also works under Windows with Python 3.7.4.
<h5>Required Python modules</h5>
  <ul>
  <li>PyQt5</li>
  <li>numpy</li>
  <li>matplotlib</li>
  <li>scipy</li>
  <li>quantiphy</li>
  
  </ul>      
