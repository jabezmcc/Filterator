from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMessageBox
from PyQt5.uic import loadUiType
print('Finished loading PtQt5...')
import sys, os, platform, subprocess
import numpy as np
from quantiphy import Quantity
Quantity.set_prefs(strip_zeros=False)
print('Finished loading sys, numpy and quaniphy...')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('QT5Agg')
print('Finished loading matplot stuff...')
from scipy import signal
print('Finished loading scipy stuff...')
Ui_MainWindow, QMainWindow = loadUiType('filterator3.ui')
Ui_AboutWindow, QAboutWindow = loadUiType('aboutFilterator.ui')

vers = '0.1'

fact1090 = np.log(0.9)-np.log(0.1)

class About(QAboutWindow, Ui_AboutWindow):
    def __init__(self):
        super(About,self).__init__()
        self.setupUi(self)
        self.versionLabel.setText("Version "+vers)
        self.licenseButt.clicked.connect(self.show_license)
        self.OKButt.clicked.connect(self.closeout)
        self.show()
        
    def show_license(self):
        p = platform.system()
        try:
            if p == 'Linux':
                subprocess.run(['xdg-open', 'LICENSE.txt'],check=True)
            elif p=='Windows':
                os.system('start LICENSE.txt')
            else:
                os.system('open LICENSE.txt')
        except:
             QMessageBox.warning(self,'Error','Unable to open license document')
                
    def closeout(self):
        self.close()

class Main(QMainWindow, Ui_MainWindow):
    bodePlotexists = False
    outputPlotexists = False
    def __init__(self ):
        super(Main,self).__init__()
        self.setupUi(self)
        self.actionExit.triggered.connect(self.quit)
        self.actionAbout.triggered.connect(self.openabout)
        self.vinampl=Quantity('1.0 V')
        self.inputVoltage.setText(str(self.vinampl))
        self.inputfreq = Quantity('1000. Hz')
        self.inputFreq.setText(str(self.inputfreq))
        self.cornerfreq = Quantity('1000. Hz')
        self.cornerFreq.setText(str(self.cornerfreq))
        tau = Quantity(1./(2.*np.pi*self.cornerfreq), 's')
        self.timeConst.setText(str(tau))
        t1090 = Quantity(tau*fact1090,'s')
        self.filterorder = self.polenumCombo.currentIndex() + 1
        dBocttext = str(self.filterorder*6)+' dB/octave;'
        dBdectext = str(self.filterorder*20)+' dB/decade'
        self.dBoctavelabel.setText(dBocttext)
        self.dBdecadelabel.setText(dBdectext)
        
        self.inputVoltage.returnPressed.connect(self.Vchanged)
        self.inputFreq.returnPressed.connect(self.Fchanged)
        self.cornerFreq.returnPressed.connect(self.Cfchanged)
        self.timeConst.returnPressed.connect(self.Tauchanged)
        self.polenumCombo.currentIndexChanged.connect(self.Newpole)
        self.amplitudeRadioButton.toggled.connect(self.Vchanged)
        self.rmsRadioButton.toggled.connect(self.Vchanged)
        self.sineRadioButton.toggled.connect(self.Vchanged)
        self.squareRadioButton.toggled.connect(self.Vchanged)
        self.lopassRadioButton.toggled.connect(self.radio_toggled)
        self.bessRadioButton.toggled.connect(self.radio_toggled)

        self.update_all()
    
    def openabout(self):
        self.aboutwin = About()       
    
    def Vchanged(self):
        if self.amplitudeRadioButton.isChecked():
            try:
                self.vinampl = Quantity(self.inputVoltage.text())
            except:
                return
        elif self.rmsRadioButton.isChecked():
            if self.sineRadioButton.isChecked():
                try:
                    self.vinampl = Quantity(np.sqrt(2)*Quantity(self.inputVoltage.text()),'V')
                except:
                    return
            elif self.squareRadioButton.isChecked():
                try:
                    self.vinampl = Quantity(self.inputVoltage.text())
                except:
                    return
            elif self.triangleRadioButton.isChecked():
                try:
                    self.vinampl = Quantity(np.sqrt(3)*Quantity(self.inputVoltage.text()),'V')
                except:
                    return
            else:
                print('Something bad happened!')
        elif self.p2pRadioButton.isChecked():
            try:
                self.vinampl = Quantity(Quantity(self.inputVoltage.text())/2., 'V')
            except:
                return
        else:
            print('Something bad happened!')  
        try:
            self.update_all()
        except:
            QMessageBox.warning(self,'Error','Please choose more reasonable parameters') 
    
    def Fchanged(self):
        try:
            self.inputfreq = Quantity(self.inputFreq.text())
        except:
            return
        try:
            self.update_all()
        except:
            QMessageBox.warning(self,'Error','Please choose more reasonable parameters') 
        
    def Cfchanged(self):
        try:
            self.cornerfreq = Quantity(self.cornerFreq.text())
        except:
            return
        tau = Quantity(1./(2.*np.pi*self.cornerfreq), 's')
        self.timeConst.setText(str(tau))
        try:
            self.update_all()
        except:
            QMessageBox.warning(self,'Error','Please choose more reasonable parameters') 

    def Tauchanged(self):
        try:
            tau = Quantity(self.timeConst.text(),'s')
        except:
            return
        self.cornerfreq = Quantity(1/(2.*np.pi*tau),'Hz')
        self.cornerFreq.setText(str(self.cornerfreq))
        try:
            self.update_all()
        except:
            QMessageBox.warning(self,'Error','Please choose more reasonable parameters') 
    
    def Newpole(self):
        self.filterorder = self.polenumCombo.currentIndex() + 1
        dBocttext = str(self.filterorder*6)+' dB/octave;'
        dBdectext = str(self.filterorder*20)+' dB/decade'
        self.dBoctavelabel.setText(dBocttext)
        self.dBdecadelabel.setText(dBdectext)
        try:
            self.update_all()
        except:
            QMessageBox.warning(self,'Error','Please choose more reasonable parameters') 
    
    def radio_toggled(self):
        try:
            self.update_all()
        except:
            QMessageBox.warning(self,'Error','Please choose more reasonable parameters') 
    
    def addmpl(self,fig,layout):
        self.canvas = FigureCanvas(fig)
        layout.addWidget(self.canvas)
        self.canvas.draw()

    def update_all(self):
        
        # input voltages
        self.inputAmplitudelabel.setText("Vampl="+str(self.vinampl))
        if self.sineRadioButton.isChecked():
            self.inputRMSlabel.setText("Vrms="+str(Quantity(self.vinampl/np.sqrt(2),"V")))  
            self. inputP2Plabel.setText("Vp-p="+str(Quantity(2.*self.vinampl, "V")))
        if self.squareRadioButton.isChecked():
            self.inputRMSlabel.setText("Vrms="+str(self.vinampl))  
            self. inputP2Plabel.setText("Vp-p="+str(Quantity(2.*self.vinampl,"V")))
        if self.triangleRadioButton.isChecked():
            self.inputRMSlabel.setText("Vrms="+str(Quantity(self.vinampl/np.sqrt(3),"V")))  
            self. inputP2Plabel.setText("Vp-p="+str(Quantity(2.*self.vinampl,"V")))
        #spantext = '<span font-family="Times New Roman"; font-weight=600;><i>f<sub>c</sub></i></span>'
        spantext ='<span style=\"font-family:\'Times New Roman\';font-weight:600;font-style:italic;\">f<sub>c</sub></span>'
        self.label_timeconst.setText('Time const. (1/2\u03C0'+spantext+')')
        
        # set up filter
        
        fsig = self.inputfreq
        ffilter = self.cornerfreq
        n = self.filterorder
        settle_time = n/ffilter
        tmax = settle_time + 3./fsig
        npts = 50000
        plotmin = np.round(np.log10(ffilter),0)-2
        plotmax = plotmin + 4
        fsampsig = npts/tmax
        fsampbode = 10**(plotmax + 1)
        maxfreq = Quantity(min(fsampbode,fsampsig)/2,'Hz')
        if (ffilter >= maxfreq):
            QMessageBox.warning(self,'Error','Filter frequency should be less than {:s}'.format(str(maxfreq))) 
            return
        if self.lopassRadioButton.isChecked():
            p = 'lp'
        else:
            p = 'hp'  
        if self.buttRadioButton.isChecked():
            sossig = signal.butter(n, ffilter, p, fs=fsampsig, output='sos')
            sosbode = signal.butter(n, ffilter, p, fs=fsampbode, output='sos')
        else:
            sossig = signal.bessel(n, ffilter, p, fs=fsampsig, output='sos')
            sosbode = signal.bessel(n, ffilter, p, fs=fsampbode, output='sos')
            
        # frequencies and gain for Bode plot
        
        wn = np.logspace(plotmin,plotmax,num=200)
        w, h = signal.sosfreqz(sosbode, worN=wn,fs=fsampbode)
                
        if self.bodePlotexists:
            self.bodeLayout.removeWidget(self.bodecanvas)
        fig1 = Figure()
        fig1.set_tight_layout(True)
        ax = fig1.add_subplot(111)
        ax.loglog(w,abs(h))
        ax.vlines(fsig,1e-4,10,colors='red',linestyles='dashed')
        ax.tick_params(which='both',axis='both',direction='in',labelsize=10)
        ax.grid(which='both',axis='both')
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Gain")
        ax.set_xlim(10**plotmin,10**plotmax)
        ax.set_ylim(1e-4,10)
        if (self.inputfreq >= 10**plotmin) and (self.inputfreq <= 10**plotmax):
            ax.text(self.inputfreq,20.,"f",color='red',fontstyle='italic',family='Times New Roman',size='large',fontweight='bold',horizontalalignment='center')
        self.bodecanvas = FigureCanvas(fig1)
        self.bodeLayout.addWidget(self.bodecanvas)
        self.bodecanvas.draw()
        self.show()
        self.bodePlotexists = True
  
        # output signal 
         
        t = np.linspace(0.,tmax,npts,endpoint=False)
        if self.sineRadioButton.isChecked():
            sig = self.vinampl*np.sin(2.*np.pi*fsig*t)
        elif self.squareRadioButton.isChecked():
            sig = self.vinampl*signal.square(2.*np.pi*fsig*t)
        else:
            sig = self.vinampl*signal.sawtooth(2.*np.pi*fsig*t,width=0.5)
        filtered = signal.sosfilt(sossig, sig)
        tplot = t[np.where(t>settle_time)]
        tplot = tplot - min(tplot)
        sigplot = filtered[np.where(t>settle_time)]
        yout_p2p = Quantity(max(sigplot)-min(sigplot),"V")
        yout_ampl = Quantity(yout_p2p/2.,"V")
        yout_rms = Quantity(np.std(sigplot),"V")
        self.outputAmplitudelabel.setText("Vampl="+str(yout_ampl))
        self.outputRMSlabel.setText("Vrms="+str(yout_rms))
        self.outputP2Plabel.setText("Vp-p="+str(yout_p2p))
        
        if self.outputPlotexists:
            self.outputLayout.removeWidget(self.outputcanvas)
        fig2 = Figure()
        fig2.set_tight_layout(True)
        ax2 = fig2.add_subplot(111)
        ax2.plot(tplot,sigplot)   
        ax2.axhline(y=0.0,color='black')
        ax2.tick_params(which='both',axis='both',direction='in',labelsize=10)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Amplitude (V)")
        ax2.set_xlim(0,max(tplot))
        ax2.ticklabel_format(axis='x',scilimits=[-3,4])
        self.outputcanvas = FigureCanvas(fig2)
        self.outputLayout.addWidget(self.outputcanvas)
        self.outputcanvas.draw()
        self.show() 
        self.outputPlotexists = True      
        
        # transient analysis
        
        ss = p=='lp'
        transsig = 0*t + 1.0
        filttrans = signal.sosfilt(sossig, transsig)
        try:
            ttrans = str(Quantity(t[np.where(abs(filttrans-ss)>0.1)[0][-1]],'s'))
        except:
            #ttrans = '<span style=\"font-style:italic;\">(n.c.)</span>'
            ttrans = '<not calc.>'
        self.labeltrans.setText('Step transient < 10 %  after '+ttrans)
    
    def quit(self):
        sys.exit()  
    
    def about(self):
        print('About starts here...')

if __name__=="__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    qtRectangle = main.frameGeometry()
    centerPoint = QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    main.move(qtRectangle.topLeft())
    sys.exit(app.exec())
