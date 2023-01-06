from config import *
import engine
import scene


class App:
    def __init__(self, width, height, debugMode):
        self.build_glfw_window(width, height, debugMode)

        self.graphicsEngine = engine.Engine(width, height, self.window, debugMode)

        self.lastTime = glfw.get_time()
        self.currentTime = glfw.get_time()
        self.numFrames = 0
        self.frameTime = 0

        self.scene = scene.Scene()



    def build_glfw_window(self, width, height, debugMode):

        # init glfw
        glfw.init()

        # no default client api, we'll use vulkan later
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CLIENT_API, GLFW_CONSTANTS.GLFW_NO_API)
        # no resize
        glfw.window_hint(GLFW_CONSTANTS.GLFW_RESIZABLE, GLFW_CONSTANTS.GLFW_FALSE)

        # create the window
        self.window = glfw.create_window(width, height, "Test", None, None)
        if self.window is not None:
            if debugMode: print(f"Made glfw window!")
        else:
            if debugMode: print("Failed to create window!")


    def calculate_framerate(self):

        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:
            framerate = max(1, int(self.numFrames // delta))
            glfw.set_window_title(self.window, f"{framerate} FPS")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = 1000.0 / framerate

        self.numFrames += 1


    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.graphicsEngine.render(self.scene)
            self.calculate_framerate()


    def close(self):
        self.graphicsEngine.close()

