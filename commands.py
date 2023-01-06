from config import *
import queue_families
import frame




class commandPoolInputChunk:
    def __init__(self):
        self.device = None
        self.physicalDevice = None
        self.surface = None
        self.instance = None


class commandbufferInputChunk:
    def __init__(self):
        self.device = None
        self.commandPool = None
        self.frames = None


def make_command_pool(inputChunk: commandPoolInputChunk, debug):
    queueFamilyIndices = queue_families.find_queue_families(
        device=inputChunk.physicalDevice,
        instance=inputChunk.instance,
        surface=inputChunk.surface,
        debug=debug
    )

    poolInfo = VkCommandPoolCreateInfo(
        flags=VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,
        queueFamilyIndex=queueFamilyIndices.graphicsFamily
    )

    try:
        commandPool = vkCreateCommandPool(inputChunk.device, poolInfo, None)
        if debug: print("Made command pool!")
        return commandPool
    except:
        if debug: print("Failed to create command pool")
        return None

def make_command_buffers(inputChunk: commandbufferInputChunk, debug):
    allocInfo = VkCommandBufferAllocateInfo(
        commandPool=inputChunk.commandPool,
        level=VK_COMMAND_BUFFER_LEVEL_PRIMARY,
        commandBufferCount=1
    )

    for i, frame in enumerate(inputChunk.frames):
        try:
            frame.commandBuffer = vkAllocateCommandBuffers(inputChunk.device, allocInfo)[0]
            if debug: print(f"Allocated command buffer for frame {i}")

        except:
            if debug: print(f"Failed to allocate command buffer for frame {i}")





    try:
        commandBuffer = vkAllocateCommandBuffers(inputChunk.device, allocInfo)[0]
        if debug: print(f"Allocated main command buffer")
        return commandBuffer
    except:
        if debug: print(f"Failed to allocate main command buffer")
        return None