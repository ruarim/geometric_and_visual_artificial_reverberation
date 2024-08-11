import matlab.engine as matlab

def init_matlab_eng():
    matlab_eng = matlab.start_matlab()
    s = matlab_eng.genpath(r'_fdnToolbox')
    matlab_eng.addpath(s, nargout=0)
    s = matlab_eng.genpath(r'_output')
    matlab_eng.addpath(s, nargout=0)
    matlab_eng.cd(r'late_reverberation', nargout=0)
    return matlab_eng # TODO: refactor so functions that need this take it as an argument