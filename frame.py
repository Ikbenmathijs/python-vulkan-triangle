from config import *



class SwapChainFrame:
    def __init__(self):
        self.image = None
        self.image_view = None
        self.frameBuffer = None
        self.commandBuffer = None
        self.inFlight = None
        self.imageAvailable = None
        self.renderFinished = None