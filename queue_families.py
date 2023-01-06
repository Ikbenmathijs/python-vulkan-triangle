from config import *


class QueueFamilyIndices:
    def __init__(self):

        self.graphicsFamily = None
        self.presentFamily = None

    def is_complete(self):
        return self.graphicsFamily is not None and self.presentFamily is not None




def find_queue_families(device, instance, surface, debug):

    indices = QueueFamilyIndices()

    surfaceSupport = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceSupportKHR")


    # VkQueueFamilyProperties
    # {
    #     VkQueueFlags  queueFlags;
    #     uint32_t      queueCount;
    #     uint32_t      timestampValidBits;
    #     VkExtent3D    minImageTransferGranularity;
    # }
    # VkQueueFlagBits
    # {
    #       VK_QUEUE_GRAPHICS_BIT = 0x00000001,
    #       VK_QUEUE_COMPUTE_BIT = 0x00000002,
    #       VK_QUEUE_TRANSFER_BIT = 0x00000004,
    #       VK_QUEUE_SPARSE_BINDING_BIT = 0x00000008,
    # }


    # returns list of VkQueueFamilyProperties
    queueFamilies = vkGetPhysicalDeviceQueueFamilyProperties(device)


    if debug:
        print(f"There are {len(queueFamilies)} queue families")

    for i, queueFamily in enumerate(queueFamilies):
        if queueFamily.queueFlags & VK_QUEUE_GRAPHICS_BIT:
            indices.graphicsFamily = i

            if debug:
                print(f"Queue Family {i} is can do graphics")


        if surfaceSupport(device, i, surface):
            indices.presentFamily = i

            if debug:
                print(f"Queue family {i} supports surface")



        if indices.is_complete():
            break

    return indices