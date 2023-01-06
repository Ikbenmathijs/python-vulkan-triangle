from config import *
import instance
import logging
import device
import swapchain
import swapchain
import frame
import pipeline
import framebuffer
import sync
import commands


class Engine:

    def __init__(self, width, height, window, debugMode):

        self.debugMode = True

        self.window = window

        # window parameters
        self.width = width
        self.height = height

        if (self.debugMode):
            print("Engine init")


        self.make_instance()
        self.make_device()
        self.make_pipeline()
        self.finalise_setup()



    def make_instance(self):
        self.instance = instance.make_instance(self.debugMode, "Test")

        if self.debugMode:
            self.debugMessenger = logging.make_debug_messenger(self.instance)

        surfacePointer = ffi.new("VkSurfaceKHR*")

        if (glfw.create_window_surface(
                instance=self.instance,
                window=self.window,
                allocator=None,
                surface=surfacePointer
        )) != VK_SUCCESS and self.debugMode:
            print("Failed to create window surface")
        elif self.debugMode:
            print("Created window surface")

        self.surface = surfacePointer[0]

    def make_device(self):
        self.physicalDevice = device.choose_physical_device(self.instance, self.debugMode)
        self.device = device.create_logical_device(self.physicalDevice, self.instance, self.surface, self.debugMode)
        (self.graphicsQueue, self.presentQueue) = device.get_queues(self.physicalDevice, self.device, self.instance,
                                                                    self.surface, self.debugMode)
        bundle = swapchain.create_swapchain(self.instance, self.device, self.physicalDevice, self.surface, self.width,
                                            self.height, self.debugMode)
        self.swapchain = bundle.swapchain
        self.swapchainFrames = bundle.frames
        self.swapchainFormat = bundle.format
        self.swapchainExtent = bundle.extent
        self.maxFramesInFlight = len(self.swapchainFrames)
        self.frameNumber = 0

    def make_pipeline(self):
        inputBundle = pipeline.InputBundle(self.device, self.swapchainFormat, self.swapchainExtent, "shaders/vert.spv",
                                           "shaders/frag.spv")

        outputBundle = pipeline.create_graphics_pipeline(inputBundle, self.debugMode)

        self.pipelineLayout = outputBundle.pipelineLayout
        self.renderpass = outputBundle.renderPass
        self.pipeline = outputBundle.pipeline

    def finalise_setup(self):
        framebufferInput = framebuffer.framebufferInput()
        framebufferInput.device = self.device
        framebufferInput.renderpass = self.renderpass
        framebufferInput.swapchainExtent = self.swapchainExtent
        framebuffer.make_framebuffers(framebufferInput, self.swapchainFrames, self.debugMode)

        commandPoolInput = commands.commandPoolInputChunk()
        commandPoolInput.device = self.device
        commandPoolInput.physicalDevice = self.physicalDevice
        commandPoolInput.surface = self.surface
        commandPoolInput.instance = self.instance
        self.commandPool = commands.make_command_pool(commandPoolInput, self.debugMode)

        commandbufferInput = commands.commandbufferInputChunk()
        commandbufferInput.device = self.device
        commandbufferInput.commandPool = self.commandPool
        commandbufferInput.frames = self.swapchainFrames
        self.mainCommandBuffer = commands.make_command_buffers(commandbufferInput, self.debugMode)


        for frame in self.swapchainFrames:
            frame.inFlight = sync.make_fence(self.device, self.debugMode)
            frame.imageAvailable = sync.make_semaphore(self.device, self.debugMode)
            frame.renderFinished = sync.make_semaphore(self.device, self.debugMode)




    def record_draw_command(self, commandBuffer, imageIndex, scene):
        beginInfo = VkCommandBufferBeginInfo()

        try:
            vkBeginCommandBuffer(commandBuffer, beginInfo)
        except:
            if self.debugMode: print("Failed to begin recording command buffer")
        renderpassInfo = VkRenderPassBeginInfo(
            renderPass=self.renderpass,
            framebuffer=self.swapchainFrames[imageIndex].frameBuffer,
            renderArea=[[0,0], self.swapchainExtent],
        )

        clearColor = VkClearValue([[0.27, 0.23, 0.46, 1.0]])
        renderpassInfo.clearValueCount = 1
        renderpassInfo.pClearValues = ffi.addressof(clearColor)

        vkCmdBeginRenderPass(commandBuffer, renderpassInfo, VK_SUBPASS_CONTENTS_INLINE)

        vkCmdBindPipeline(commandBuffer, VK_PIPELINE_BIND_POINT_GRAPHICS, self.pipeline)


        for position in scene.triangle_positions:
            model_transform = pyrr.matrix44.create_from_translation(vec=position, dtype=np.float32)
            objData = ffi.cast("float *", ffi.from_buffer(model_transform))

            vkCmdPushConstants(
                commandBuffer=commandBuffer, layout=self.pipelineLayout,
                stageFlags=VK_SHADER_STAGE_VERTEX_BIT, offset=0,
                size=4*4*4, pValues=objData
            )


            vkCmdDraw(
                commandBuffer=commandBuffer, vertexCount=3,
                instanceCount=1, firstVertex=0, firstInstance=0
            )

        vkCmdEndRenderPass(commandBuffer)


        try:
            vkEndCommandBuffer(commandBuffer)
        except:
            if self.debugMode:
                print("Failed to end command buffer recording")


    def render(self, scene):

        vkAcquireNextImageKHR = vkGetDeviceProcAddr(self.device, "vkAcquireNextImageKHR")
        vkQueuePresentKHR = vkGetDeviceProcAddr(self.device, "vkQueuePresentKHR")

        vkWaitForFences(device=self.device, fenceCount=1, pFences=[self.swapchainFrames[self.frameNumber].inFlight],
                        waitAll=VK_TRUE, timeout=1000000000)

        vkResetFences(device=self.device, fenceCount=1, pFences=[self.swapchainFrames[self.frameNumber].inFlight])

        imageIndex = vkAcquireNextImageKHR(
            device=self.device, swapchain=self.swapchain, timeout=1000000000,
            semaphore=self.swapchainFrames[self.frameNumber].imageAvailable, fence=VK_NULL_HANDLE
        )

        commandBuffer = self.swapchainFrames[imageIndex].commandBuffer
        vkResetCommandBuffer(commandBuffer=commandBuffer, flags=0)
        self.record_draw_command(commandBuffer, imageIndex, scene)
        submitInfo = VkSubmitInfo(
            waitSemaphoreCount=1, pWaitSemaphores=[self.swapchainFrames[self.frameNumber].imageAvailable],
            pWaitDstStageMask=[VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT],
            commandBufferCount=1, pCommandBuffers=[commandBuffer],
            signalSemaphoreCount=1, pSignalSemaphores=[self.swapchainFrames[self.frameNumber].renderFinished]
        )

        try:
            vkQueueSubmit(
                queue=self.graphicsQueue, submitCount=1,
                pSubmits=submitInfo, fence=self.swapchainFrames[self.frameNumber].inFlight
            )
        except:
            if self.debugMode:
                print("Failed to submit draw commands")


        presentInfo = VkPresentInfoKHR(
            waitSemaphoreCount=1, pWaitSemaphores=[self.swapchainFrames[self.frameNumber].renderFinished],
            swapchainCount=1, pSwapchains=[self.swapchain],
            pImageIndices=[imageIndex]
        )

        vkQueuePresentKHR(self.presentQueue, presentInfo)


        self.frameNumber = (self.frameNumber + 1) % self.maxFramesInFlight





    def close(self):

        vkDeviceWaitIdle(self.device)

        if self.debugMode:
            print("Goodbye!")





        vkDestroyCommandPool(self.device, self.commandPool, None)

        vkDestroyPipeline(self.device, self.pipeline, None)
        vkDestroyPipelineLayout(self.device, self.pipelineLayout, None)
        vkDestroyRenderPass(self.device, self.renderpass, None)

        for frame in self.swapchainFrames:
            vkDestroyImageView(device=self.device, imageView=frame.image_view, pAllocator=None)

            vkDestroyFramebuffer(device=self.device, framebuffer=frame.frameBuffer, pAllocator=None)

            vkDestroyFence(self.device, frame.inFlight, None)
            vkDestroySemaphore(self.device, frame.imageAvailable, None)
            vkDestroySemaphore(self.device, frame.renderFinished, None)

        vkDestroySwapchainKHR = vkGetDeviceProcAddr(self.device, "vkDestroySwapchainKHR")
        vkDestroySwapchainKHR(self.device, self.swapchain, pAllocator=None)

        vkDestroyDevice(device=self.device, pAllocator=None)

        if self.debugMode:
            destructionFunction = vkGetInstanceProcAddr(self.instance, "vkDestroyDebugReportCallbackEXT")

            """
                def vkDestroyDebugReportCallbackEXT(
                    instance,
                    callback,
                    pAllocator
                )
            """

            destructionFunction(self.instance, self.debugMessenger, None)

        surfaceDestructionFunction = vkGetInstanceProcAddr(self.instance, "vkDestroySurfaceKHR")
        surfaceDestructionFunction(instance=self.instance, surface=self.surface, pAllocator=None)

        vkDestroyInstance(self.instance, None)

        glfw.terminate()
