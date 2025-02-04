from signal_processing.modulation_api import ModulationApi
from signal_processing.demodulation_api import DemodulationApi


class RedPitaya_Standalone:
    def __init__(self):
        
        self.modulationApi = ModulationApi()
        self.demodulationApi = DemodulationApi()
    
    