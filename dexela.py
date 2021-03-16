

import os
import ophyd
from hxntools.detectors.dexela import (DexelaDetector, DexelaTiffPlugin)
from ophyd import (AreaDetector, CamBase, TIFFPlugin, Component as Cpt,
                    HDF5Plugin, Device, StatsPlugin, ProcessPlugin,
                    ROIPlugin, EpicsSignal)
from databroker.assets.handlers import HandlerBase
from ophyd.areadetector.filestore_mixins import (FileStoreTIFFIterativeWrite,
                                                 FileStoreHDF5IterativeWrite,
                                                 FileStoreTIFFSquashing,
                                                 FileStoreTIFF,
                                                 FileStoreHDF5, new_short_uid,
                                                 FileStoreBase
                                                 )
from ophyd.areadetector import (AreaDetector, PixiradDetectorCam, ImagePlugin,
                                TIFFPlugin, StatsPlugin, HDF5Plugin,
                                ProcessPlugin, ROIPlugin, TransformPlugin,
                                OverlayPlugin)
from ophyd.areadetector.trigger_mixins import SingleTrigger
from enum import Enum
from nslsii.ad33 import StatsPluginV33
from ophyd import Component as Cpt, Signal

from ophyd.areadetector import (EpicsSignalWithRBV as SignalWithRBV)

import time


# monkey patch for trailing slash problem
def _ensure_trailing_slash(path):
    """
    'a/b/c' -> 'a/b/c/'
    EPICS adds the trailing slash itself if we do not, so in order for the
    setpoint filepath to match the readback filepath, we need to add the
    trailing slash ourselves.
    """
    newpath = os.path.join(path, '')
    if newpath[0] != '/' and newpath[-1] == '/':
        # make it a windows slash
        newpath = newpath[:-1]
    return newpath
ophyd.areadetector.filestore_mixins._ensure_trailing_slash = _ensure_trailing_slash




class XPDDMode(Enum):
    step = 1
    fly = 2


class XPDDDexelaTiffPlugin(TIFFPlugin, FileStoreTIFFIterativeWrite ):
    pass



# wait_for_plugins = EpicsSignal('XF:28IDD-ES:2{Det:DEX}cam1:WaitForPlugins', name='wait_for_plugins')





class DexelaDetectorCam(CamBase):
    acquire_gain = Cpt(EpicsSignal, 'DEXAcquireGain')
    acquire_offset = Cpt(EpicsSignal, 'DEXAcquireOffset')
    binning_mode = Cpt(SignalWithRBV, 'DEXBinningMode')
    corrections_dir = Cpt(EpicsSignal, 'DEXCorrectionsDir', string=True)
    current_gain_frame = Cpt(EpicsSignal, 'DEXCurrentGainFrame')
    current_offset_frame = Cpt(EpicsSignal, 'DEXCurrentOffsetFrame')
    defect_map_available = Cpt(EpicsSignal, 'DEXDefectMapAvailable')
    defect_map_file = Cpt(EpicsSignal, 'DEXDefectMapFile', string=True)
    full_well_mode = Cpt(SignalWithRBV, 'DEXFullWellMode')
    gain_available = Cpt(EpicsSignal, 'DEXGainAvailable')
    gain_file = Cpt(EpicsSignal, 'DEXGainFile', string=True)
    load_defect_map_file = Cpt(EpicsSignal, 'DEXLoadDefectMapFile')
    load_gain_file = Cpt(EpicsSignal, 'DEXLoadGainFile')
    load_offset_file = Cpt(EpicsSignal, 'DEXLoadOffsetFile')
    num_gain_frames = Cpt(EpicsSignal, 'DEXNumGainFrames')
    num_offset_frames = Cpt(EpicsSignal, 'DEXNumOffsetFrames')
    offset_available = Cpt(EpicsSignal, 'DEXOffsetAvailable')
    offset_constant = Cpt(SignalWithRBV, 'DEXOffsetConstant')
    offset_file = Cpt(EpicsSignal, 'DEXOffsetFile', string=True)
    save_gain_file = Cpt(EpicsSignal, 'DEXSaveGainFile')
    save_offset_file = Cpt(EpicsSignal, 'DEXSaveOffsetFile')
    serial_number = Cpt(EpicsSignal, 'DEXSerialNumber')
    software_trigger = Cpt(EpicsSignal, 'DEXSoftwareTrigger')
    use_defect_map = Cpt(EpicsSignal, 'DEXUseDefectMap')
    use_gain = Cpt(EpicsSignal, 'DEXUseGain')
    use_offset = Cpt(EpicsSignal, 'DEXUseOffset')


class DexelaDetector(AreaDetector):
    cam = Cpt(DexelaDetectorCam, 'cam1:',
              read_attrs=[],
              configuration_attrs=['image_mode', 'trigger_mode',
                                   'acquire_time', 'acquire_period'],
              )
# dexela.cam.use_offset.value




class XPDDDexelaDetector(SingleTrigger, DexelaDetector):
    total_points = Cpt(Signal, value=1, doc="The total number of points to be taken")
    stats1 = Cpt(StatsPluginV33, 'Stats1:')
    tiff = Cpt(XPDDDexelaTiffPlugin, 'TIFF1:',
               read_attrs=[],
               configuration_attrs=[],
               write_path_template='S:\\dexela\\', 
               read_path_template='/data/st/dexela/', 
               root='/data/st/',) 
    
#    wait_for_plugins = Cpt(EpicsSignal, '')

    detector_type=Cpt(Signal, value='Dexela 2923', kind='config')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mode = XPDDMode.step
#        wait_for_plugins.put(1)
        
        self.cam.stage_sigs['image_mode'] = 'Single'
        self.cam.stage_sigs['trigger_mode'] = 'Int. Software'
            
    def stage(self, *args, **kwargs):
        return super().stage(*args, **kwargs)

    def unstage(self):
        try:
            ret = super().unstage()
        finally:
            self._mode = XPDDMode.step
        return ret

    
    
    

    
#dexela = XPDDDexelaDetector('XF:28IDD-ES:2{Det:DEX}', name='dexela')
#dexela.detector_type.kind='config'
#dexela.read_attrs = ['tiff']
#dexela.stats1.kind = 'hinted'
#dexela.stats1.total.kind = 'hinted'     
    
    
"""
dexela = XPDDDexelaDetector('XF:28IDD-ES:2{Det:DEX}', name='dexela')
dexela.detector_type.kind='config'
dexela.read_attrs = ['tiff']

save_to = 'dummy'
os.makedirs('/data/dex_data/%s'%(save_to),exist_ok=True)
dexela.tiff.write_path_template = 'Z:\\%s\\'%(save_to)
dexela.tiff.read_path_template = '/data/dex_data/%s/'%(save_to)

dexela.stats1.kind = 'hinted'
dexela.stats1.total.kind = 'hinted' 

dexela.stage()
""";




