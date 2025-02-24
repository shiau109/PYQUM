# Numpy
# 
from numpy import linspace, arange
# Numpy array
from numpy import array, append, zeros, ones, where
# Numpy common math function
from numpy import exp, sqrt, arctan2, cos, sin, angle, radians, sign, log, ceil
# Numpy constant
from numpy import pi
from pandas import infer_freq


def gaussianFunc (t, p):
    # p[0]: amp
    # p[1]: sigma
    # p[2]: peak position
    return p[0] *exp( -( (t-p[2]) /p[1] )**2 /2)
def derivativeGaussianFunc (t, p):
    # p[0]: amp
    # p[1]: sigma
    # p[2]: peak position
    if p[1] != 0. :
        return -p[0] / p[1]**2 *(t-p[2]) *exp( -( (t-p[2]) /p[1] )**2 /2)
    else :
        return zeros(len(t))
def constFunc (t, p):
    # p[0]: amp
    return p[0]*ones(len(t))
def linearFunc (t, p):
    # p[0]: amp
    # p[1]: intersection
    return p[0]*t+p[1]

#     def set_QubitRegister():

class PulseBuilder():
    def __init__( self, pts, dt ):
        # self.functionName = functionName
        self.time = pts *dt
        self.timeResolution = dt
        self.operationPts = pts
        self.pulseInfo = {
            "mode": "XY",
            "envelope": {
                "shape": 'gaussian',
                "paras": [1,0.25],
            },
            "phase": 0,
        }
        self.waveform ={
            "t0": 0.,
            "dt": self.timeResolution,
            "data": array([])            
        }
    def arbXYGate( self, p, shape='DRAG' ):
        theta, phi = p
        pulseInfo = {
            "envelope": {
                "mode": "XY",
                "shape": shape,
                "paras": [theta/pi,0.25],
                },
            "phase": phi,
        }
        return self.pulseInfo.update(pulseInfo)

    def rotXY( self, p, shape='fDRAG' ):
        amp, sigmaRatio, dRatio, rotAxis = p
        pulseInfo = {
            "envelope": {
                "mode": "XY",
                "shape": shape,
                "paras": [amp, sigmaRatio, dRatio],
                },
            "phase": rotAxis,
        }
        return self.pulseInfo.update(pulseInfo)

    def idle( self, p, channel="XY" ):
        pulseInfo = {
            "mode": channel,
            "envelope": {
                "shape": 'const',
                "paras": p,
            },
            "phase": 0,
            }
        return self.pulseInfo.update(pulseInfo)

    def purePulse( self, p, channel="i", shape='gaussian' ):
        pulseInfo = {
            "mode": channel,
            "envelope": {
                "shape": shape,
                "paras": p,
            },
            "phase": 0,
            }
        return self.pulseInfo.update(pulseInfo)

    def generate_envelope( self, startTime=None ):
        self.waveform["data"] = zeros( self.operationPts )
        if startTime != None: self.waveform["t0"] = startTime
        self.waveform["dt"] = self.timeResolution
        relativeTime = linspace(0,self.time,self.operationPts,endpoint=False)
        
        amp = self.pulseInfo["envelope"]["paras"][0]
        
        def get_gaussian():
            centerTime = self.time /2
            sigma = self.time *self.pulseInfo["envelope"]["paras"][1]
            p = [amp, sigma, centerTime]
            wfData = gaussianFunc( relativeTime, p )
            return wfData

        def get_halfGaussian():
            sigma = self.time *self.pulseInfo["envelope"]["paras"][1]
            centerTime = 0
            
            if sigma > 0:
                centerTime = self.time
            p = [amp, sigma, centerTime]
            wfData = gaussianFunc( relativeTime, p )
            return wfData

        def get_degaussian():
            centerTime = self.time /2
            sigma = self.time *self.pulseInfo["envelope"]["paras"][1]
            p = [amp, sigma, centerTime]
            wfData = derivativeGaussianFunc( relativeTime, p )
            return wfData

        def get_halfDeGaussian():
            sigma = self.time *self.pulseInfo["envelope"]["paras"][1]
            centerTime = 0
            
            if sigma > 0:
                centerTime = self.time
            p = [amp, sigma, centerTime]
            wfData = derivativeGaussianFunc( relativeTime, p )
            return wfData

        def get_DRAG():
            centerTime = self.time /2
            amp = self.pulseInfo["envelope"]["paras"][0]
            sigma = self.time *self.pulseInfo["envelope"]["paras"][1]

            pGau = [ amp, sigma, centerTime ]

            ampDGau = amp 
            pDGau = [ ampDGau, sigma, centerTime ]
            #wfData = gaussianFunc(relativeTime, pGau )+ -1j/(hardwareInfo.Qubit.anharmonicity/1e3) *derivativeGaussianFunc(relativeTime, pDGau)
            wfData = gaussianFunc(relativeTime, pGau )+ -1j *derivativeGaussianFunc(relativeTime, pDGau)

            return wfData

        def get_flexDRAG():
            centerTime = self.time /2
            amp = self.pulseInfo["envelope"]["paras"][0]
            sigma = self.time *self.pulseInfo["envelope"]["paras"][1]

            pGau = [ amp, sigma, centerTime ]

            ampDGau = amp *self.pulseInfo["envelope"]["paras"][2] 
            pDGau = [ ampDGau, sigma, centerTime ]
            wfData = gaussianFunc(relativeTime, pGau )+ -1j*derivativeGaussianFunc(relativeTime, pDGau)

            return wfData

        def get_const():
            amp = self.pulseInfo["envelope"]["paras"][0]
            p = [ amp ]

            wfData = constFunc( relativeTime, p )

            return wfData
        def get_linear():
            slope = self.pulseInfo["envelope"]["paras"][0]
            intercept = self.pulseInfo["envelope"]["paras"][1]
            p = [ slope, intercept ]

            wfData = linearFunc( relativeTime, p )

            return wfData
        def get_ringUp():
            flatHieght = self.pulseInfo["envelope"]["paras"][0]
            sigmaRatio = self.pulseInfo["envelope"]["paras"][1]
            edgeLength = self.pulseInfo["envelope"]["paras"][2]

            peakLength = edgeLength*2
            flatLength = self.time -peakLength
            peakMultiplier = self.pulseInfo["envelope"]["paras"][3]
            peakSigma = peakLength *sigmaRatio

            startPos = edgeLength

            ringPeak = flatHieght *(peakMultiplier)
            endPos = startPos +flatLength

            ringGauss = [ ringPeak, peakSigma, startPos ]

            highPowerGauss = gaussianFunc(relativeTime, ringGauss)
            startEdge = [ flatHieght, peakSigma, startPos ]
            gaussUp = where( relativeTime<startPos, gaussianFunc(relativeTime, startEdge),0. )
            endEdge = [ flatHieght, peakSigma, endPos ]
            gaussDn = where( relativeTime>endPos, gaussianFunc(relativeTime, endEdge),0. )
            step = where( (relativeTime>=startPos) & (relativeTime<=endPos), constFunc(relativeTime, [flatHieght]),0. )
            wfData = highPowerGauss +gaussUp +step +gaussDn

            return wfData
        pulse = {
            'gaussian': get_gaussian,
            'gaussian_half': get_halfGaussian,
            'degaussian': get_degaussian,
            'degaussian_half': get_halfDeGaussian,
            'DRAG': get_DRAG,
            'fDRAG': get_flexDRAG,
            'const': get_const,
            'linear': get_linear,
            'ringup': get_ringUp,
        }
        phaseShift = exp(1j*self.pulseInfo["phase"])
        self.waveform["data"]= pulse[self.pulseInfo["envelope"]["shape"]]() *phaseShift
        #print(self.waveform)
        return self.waveform

    def convert_XYtoIQ( self, IQMixerChannel=None ):
        envelope = self.waveform["data"] 
        absoluteTime = get_timeAxis(self.waveform)

        if IQMixerChannel != None:
            phaseBalance = IQMixerChannel.phaseBalance
            ampBalance  = IQMixerChannel.ampBalance
            (offsetI, offsetQ) = IQMixerChannel.offset
            if_freq = IQMixerChannel.ifFreq/1e3 # to GHz
            inverse = sign(sin(radians(phaseBalance)))
            #print(self.pulseInfo["mode"])

            if self.pulseInfo["mode"] == "XY":
                envelopeIQ = abs( envelope )
                envelopeI = envelopeIQ /cos(radians(abs(phaseBalance)-90))
                envelopeQ = envelopeI /ampBalance
                phi = arctan2( envelope.imag, envelope.real )
                phiQ = -phi+inverse*pi/2.
                sigI = envelopeI *cos( 2. *pi *if_freq *absoluteTime +phiQ +radians(phaseBalance) +pi) -offsetI
                sigQ = envelopeQ *cos( 2. *pi *if_freq *absoluteTime +phiQ) -offsetQ
                self.waveform["data"] = sigI+ 1j*sigQ
            elif self.pulseInfo["mode"] == "i":
                self.waveform["data"] = envelope*cos( 2. *pi *if_freq *absoluteTime +radians(phaseBalance) +pi) -offsetI
            elif self.pulseInfo["mode"] == "q":
                self.waveform["data"] = 1j*(envelope/ampBalance*cos( 2. *pi *if_freq *absoluteTime) -offsetQ)
        else:
            self.waveform["data"] = envelope

        return self.waveform

class QubitOperationSequence():

    def __init__( self, sequencePts, dt ):
        self.dt = dt
        self.operation = []
        self.sequenceTime = sequencePts*dt # ns
        self.sequencePts = sequencePts
        # print("sequenceTime",sequenceTime)
        # print("sequencePts",self.sequencePts)

        self.xywaveform = {
            "t0": 0.,
            "dt": dt,
            "data": array([])
            }
        self.iqwaveform = {
            "t0": 0.,
            "dt": dt,
            "data": array([])
            }
    def set_operation( self, operation  ):

        self.operation = operation
        endPt = int(0)
        for i, op in enumerate(self.operation) :
            operationPts = op.operationPts
            op.waveform["t0"] = endPt*self.dt
            #print("start point",endPt)
            #print("op point",operationPts)
            endPt += operationPts

        if endPt < self.sequencePts:
            op = PulseBuilder(self.sequencePts-endPt,self.dt)
            op.idle([0])
            self.operation.append(op)
            print("Operation sequence haven't full")
        elif endPt == self.sequencePts:
            print("Total operations match operation sequence")
        else:
            op = PulseBuilder(self.sequencePts,self.dt)
            op.idle([0])
            self.operation = [op]
            print("Too much operation, clean all sequense")
            

    
    def generate_sequenceWaveform( self, mixerInfo=None, firstOperationIdx=None ):

        allXYPulse = array([])
        allIQPulse = array([])
        t0 = 0
        if len(self.operation) == 0 : # For the case with only one operation
            firstOperationIdx = 0
        # Convert XY to IQ language
        for op in self.operation:
            newPulse = op.generate_envelope()["data"]
            allXYPulse = append(allXYPulse, newPulse)

        if firstOperationIdx != None :
            t0 = self.operation[firstOperationIdx].waveform["t0"]
        elif len(self.operation) == 0 :
            t0 = 0
        else:
            try: # Old method to get t0
                t0 = self.dt * where(ceil(abs(allXYPulse))==1)[0][0]
                # print(Back.WHITE + Fore.BLUE + "Pulse starting from %s ns" %pulse_starting_time)
            except(IndexError): 
                t0 = 0

        # Convert XY to IQ language        
        for op in self.operation:
            op.waveform["t0"]-=t0
            newPulse = op.convert_XYtoIQ( mixerInfo )["data"]
            allIQPulse = append(allIQPulse, newPulse)

            #print(len(newPulse))

        self.xywaveform.update({"data":allXYPulse})
        self.iqwaveform.update({"data":allIQPulse})

        return self.iqwaveform

def get_timeAxis( waveform ):
    dataPts = len(waveform["data"])
    #print(waveform["t0"], waveform["dt"], dataPts)
    return linspace( waveform["t0"], waveform["t0"]+waveform["dt"]*dataPts, dataPts, endpoint=False)

class IQMixerChannel():
    def __init__ ( self ):
        self.ifFreq = 91. # MHz
        self.ampBalance = 1. # I/Q amp ratio compensation for SSB
        self.offset = (0.,0.)
        self.phaseBalance = -90 # I/Q Quadrature phase difference compensation for SSB


        




if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import scipy.fft as spfft
    dt = 1.
    print("register IQMixerChannel")
    mixerInfo = IQMixerChannel()    

    OPS = QubitOperationSequence(100, 1.)

    print(f"set new operation")
    op1 = PulseBuilder(20,dt)
    op1.arbXYGate([pi,0])
    op2 = PulseBuilder(50,dt)
    op2.rotXY([1,0.25,5,0])
    op3 = PulseBuilder(20,dt)
    op3.idle([0])

    print("register operation to sequence")
    OPS.set_operation([op3, op2])

    print("calculate XY waveform of the sequence")
    OPS.generate_sequenceWaveform(mixerInfo=mixerInfo)
    xyWf = OPS.xywaveform
    print("calculate IQ waveform of the sequence")
    iqWf = OPS.iqwaveform

    plot1 = plt.figure(1)
    timeAxis = get_timeAxis(xyWf)
    plt.plot(timeAxis, xyWf["data"].real)
    plt.plot(timeAxis, xyWf["data"].imag)
    plt.plot(timeAxis, iqWf["data"].real)
    plt.plot(timeAxis, iqWf["data"].imag)
    plot2 = plt.figure(2)
    plt.plot(xyWf["data"].real, xyWf["data"].imag)
    plt.plot(iqWf["data"].real, iqWf["data"].imag)
    #plot3 = plt.figure(3)

    fq = 5e9
    pmixer = mixerInfo.phaseBalance
    fIF = mixerInfo.ifFreq/1e3
    # plt.plot(timeAxis, cos(2*pi*fq*timeAxis) )

    # xymix = xyWf["data"].real*cos(2*pi*fq*timeAxis) +xyWf["data"].imag*cos(2*pi*fq*timeAxis +abs(radians(pmixer)) )
    # plt.plot(timeAxis, xymix)
    # iqmix = iqWf["data"].real*cos(2*pi*(fq+fIF)*timeAxis) +iqWf["data"].imag*cos(2*pi*(fq+fIF)*timeAxis +radians(pmixer) )
    # plt.plot(timeAxis, iqmix)

    # data_points = len(timeAxis)
    # f_points = data_points//2
    # faxis = spfft.fftfreq(data_points,iqWf["dt"])[0:f_points]
    # plot4 = plt.figure(4)
    # xyvector = spfft.fft(xymix)[0:f_points]/len(timeAxis)
    # plt.plot(faxis, abs(xyvector))
    # iqvector = spfft.fft(iqmix)[0:f_points]/len(timeAxis)
    # plt.plot(faxis, 10*log(abs(iqvector)))

    plt.show()


