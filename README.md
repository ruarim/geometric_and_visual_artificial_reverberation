# Geometric and Visual Artificial Reverberation

This project focuses on creating artificial reverberation using geometric and image recogniton techniques. The implementation leverages the MATLAB fdnToolbox and Python.

### Prerequisites

#### MATLAB Dependencies

- **MATLAB**: Ensure MATLAB is installed on your system.
- **fdnToolbox**: [GitHub](https://github.com/SebastianJiroSchlecht/fdnToolbox).
- **MATLAB vs-code extension**: Use the VS Code extension to add required files to the MATLAB folder. To do this, right-click on the folder and select `MATLAB: Add Folder To Path`.

#### Python Dependencies

Install the following Python packages using `pip`:

```bash
pip install numpy scipy pyroomacoustics matlabengine matplotlib librosa sympy openai
```

### Documentation

- Configure config.py with paths for surface images and 3D model in .obj format.
- Test geometry recognition via: `python3 model.py`
- Test material extraction via: `python3 absorption.py`
- Create RIRs with all models via: `python3 rir.py`
- Create proccessed samples with all models via: `python3 stimuli.py`
- Run Parallel ISMFDN via: `python3 parallel_ism_fdn.py`
- Run Serial ISMFDN via: `python3 serial_ism_fdn.py`
