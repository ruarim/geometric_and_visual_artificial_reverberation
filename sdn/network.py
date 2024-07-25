from .source import Source
from .mic import Mic
from .propigation_line import PropigationLine
from .scattering_junction import ScatteringJunction


class Network:
    def __init__(self, early_reflections, source_location, mic_location, wall_absorption, fs, enable_direct_path):
        self.M = len(early_reflections)
        
        self.source = Source(source_location)
        self.mic = Mic(mic_location)
        
        # create direct path
        self.enable_direct_path = enable_direct_path
        self.direct_path = PropigationLine(start=self.source, end=self.mic, fs=fs)
        self.direct_path.attenuation = min(1 / self.direct_path.distance, 1)
        self.source.add_direct_path(self.direct_path)
        self.mic.add_direct_path(self.direct_path)  
        self.junctions: list[ScatteringJunction] = []
        
        # for each refelection create a scattering junction
        for i in range(self.M):
            junction_loc = early_reflections[i]
            junction = ScatteringJunction(junction_loc, self.source, self.mic, alpha=wall_absorption)
            self.junctions.append(junction)
        
        # connect the scattering junctions with waveguides (bidirectional delay lines)
        for i in range(self.M):   
            # connect source to junction
            source_line = PropigationLine(start=self.source, end=self.junctions[i], fs=fs)
            source_attenuation = 1 / source_line.distance
            source_line.attenuation = min(source_attenuation, 1) # set the gain to 1 if > 1
            self.source.add_to_junction(source_line)
            
            # connect junction to mic
            mic_line = PropigationLine(start=self.junctions[i], end=self.mic, fs=fs, offset=-1)
            mic_attenuation = 1 / (1 + (mic_line.distance / source_line.distance))
            mic_line.attenuation = min(mic_attenuation, 1)
            self.mic.add_from_junction(mic_line)
            
            # connect junctions to all other junctions via propigations lines
            for j in range(self.M):
                # ignore diagonal - dont connect node to itself
                if i == j: continue
                # create the connection: junction i --propigation line--> junction j
                prop_line = PropigationLine(start=self.junctions[i], end=self.junctions[j], fs=fs)
                # append in/out line
                self.junctions[i].add_out(prop_line)
                self.junctions[j].add_in(prop_line)
            
    def process(self, sample_in):
        # add sample to direct path
        self.direct_path.sample_in(sample_in)
        samples_out = [] # use array instead for mic pattern model
            
        for i in range(self.M):
            # push sample to source prop line
            self.source.propigation_lines[i].sample_in(sample_in) 
            # get sample from source propline
            source_sample = self.source.propigation_lines[i].sample_out()
            # apply scattering
            junction_samples, sample_to_mic = self.junctions[i].scatter_in(source_sample)
            self.junctions[i].scatter_out(junction_samples)
            # push scattered sample to microphone prop line
            self.mic.propigation_lines[i].sample_in(sample_to_mic)
            # collect output samples
            mic_sample = self.mic.propigation_lines[i].sample_out()
            samples_out.append(mic_sample)
        
        # model microphone directivity pattern here
        # mic_out = mic.process(samples_out)
        
        output_summed = sum(samples_out) # * (2 / (self.M - 1))
        if(self.enable_direct_path): return output_summed + self.direct_path.sample_out()
        else: return output_summed
        