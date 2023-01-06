from config import *
import logging
import queue_families
import frame



class SwapChainSupportDetails:
    def __init__(self):
        self.capabilities = None
        self.formats = None
        self.presentModes = None


class SwapChainBundle:
    def __init__(self):
        self.swapchain = None
        self.frames = []
        self.format = None
        self.extent = None





def query_swapchain_support(instance, physicalDevice, surface, debug):

    support = SwapChainSupportDetails()

    vkGetPhysicalDeviceSurfaceCapabilities = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceCapabilitiesKHR")
    support.capabilities = vkGetPhysicalDeviceSurfaceCapabilities(physicalDevice, surface, None)

    if debug:
        # VkSurfaceCapabilitiesKHR
        # {
        #     uint32_t minImageCount;
        # uint32_t maxImageCount;
        # VkExtent2D currentExtent;
        # VkExtent2D minImageExtent;
        # VkExtent2D maxImageExtent;
        # uint32_t maxImageArrayLayers;
        # VkSurfaceTransformFlagsKHR supportedTransforms;
        # VkSurfaceTransformFlagBitsKHR currentTransform;
        # VkCompositeAlphaFlagsKHR supportedCompositeAlpha;
        # VkImageUsageFlags supportedUsageFlags;
        # }
        print("Swapchain surface capabilities:")
        print(f"\tMin image count: {support.capabilities.minImageCount}")
        print(f"\tMax image count: {support.capabilities.maxImageCount}")

        # VkExtend2D {
        #     uint32_t  width;
        #     uint32_t  height;
        # }
        print("\tCurrent Extent:")
        print(f"\t\twidth: {support.capabilities.currentExtent.width}")
        print(f"\t\twidth: {support.capabilities.currentExtent.height}")

        print(f"\tMin Extent:")
        print(f"\t\twidth: {support.capabilities.minImageExtent.width}")
        print(f"\t\twidth: {support.capabilities.minImageExtent.height}")

        print(f"\tMax Extent:")
        print(f"\t\twidth: {support.capabilities.maxImageExtent.width}")
        print(f"\t\twidth: {support.capabilities.maxImageExtent.height}")


        print(f"\tMax image array layers: {support.capabilities.maxImageArrayLayers}")


        print("\tSupported transforms:")
        stringList = logging.log_transform_bits(support.capabilities.supportedTransforms)
        for line in stringList:
            print(f"\t\t{line}")

        print("\tCurrent transforms:")
        stringList = logging.log_transform_bits(support.capabilities.currentTransform)
        for line in stringList:
            print(f"\t\t{line}")

        print("\tsupported alpha operations:")
        stringList = logging.log_alpha_composite_bits(support.capabilities.supportedCompositeAlpha)
        for line in stringList:
            print(f"\t\t{line}")

        print("\tsupported image usage:")
        stringList = logging.log_image_usage_bits(support.capabilities.supportedUsageFlags)
        for line in stringList:
            print(f"\t\t{line}")

        vkGetPhysicalDeviceSurfaceFormatsKHR = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceFormatsKHR")
        support.formats = vkGetPhysicalDeviceSurfaceFormatsKHR(physicalDevice, surface)

        if debug:
            for supportedFormat in support.formats:
                # VkSurfaceFormatKHR {
                #     VkFormat  format
                #     VkColorSpaceKHR  ColorSpace
                # }

                print(f"Supported pixel format: {logging.format_to_string(supportedFormat.format)}")
                print(f"Supported Color Space: {logging.colorspace_to_string(supportedFormat.colorSpace)}")


        vkGetPhysicalDeviceSurfacePresentModesKHR = vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfacePresentModesKHR")
        support.presentModes = vkGetPhysicalDeviceSurfacePresentModesKHR(physicalDevice, surface)
        if debug:
            for presentMode in support.presentModes:
                print(f"\t{logging.log_present_mode(presentMode)}")


    return support


def choose_swapchain_surface_format(formats):

    for v in formats:
        if v.format == VK_FORMAT_B8G8R8A8_UNORM and v.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR:
            return v

    return formats[0]


def choose_swapchain_present_mode(presentModes):

    for presentMode in presentModes:
        if presentMode == VK_PRESENT_MODE_MAILBOX_KHR:
            return presentMode

    return VK_PRESENT_MODE_FIFO_KHR



def choose_swapchain_extent(width, height, capabilities):
    extent = VkExtent2D(width, height)

    extent.width = min(capabilities.maxImageExtent.width, max(capabilities.minImageExtent.width, extent.width))

    extent.height = min(capabilities.maxImageExtent.height, max(capabilities.maxImageExtent.height, extent.height))

    return extent


def create_swapchain(instance, logicalDevice, physicalDevice, surface, width, height, debug):

    support = query_swapchain_support(instance, physicalDevice, surface, debug)

    format = choose_swapchain_surface_format(support.formats)

    presentMode = choose_swapchain_present_mode(support.presentModes)

    extent = choose_swapchain_extent(width, height, support.capabilities)

    imageCount = min(support.capabilities.maxImageCount, support.capabilities.minImageCount + 1)

    indices = queue_families.find_queue_families(physicalDevice, instance, surface, debug)
    queueFamilyIndices = [indices.graphicsFamily, indices.presentFamily]

    if indices.graphicsFamily != indices.presentFamily:
        imageSharingMode = VK_SHARING_MODE_CONCURRENT
        queueFamilyIndexCount = 2
        pQueueFamilyIndices = queueFamilyIndices
    else:
        imageSharingMode = VK_SHARING_MODE_EXCLUSIVE
        queueFamilyIndexCount = 0
        pQueueFamilyIndices = None


    createInfo = VkSwapchainCreateInfoKHR(surface=surface, minImageCount=imageCount, imageFormat=format.format, imageColorSpace=format.colorSpace,
                                          imageExtent=extent, imageArrayLayers=1, imageUsage=VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
                                          imageSharingMode=imageSharingMode, queueFamilyIndexCount=queueFamilyIndexCount, pQueueFamilyIndices=queueFamilyIndices,
                                          preTransform=support.capabilities.currentTransform, compositeAlpha=VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
                                          presentMode=presentMode, clipped=VK_TRUE)

    bundle = SwapChainBundle()

    vkCreateSwapchainKHR = vkGetDeviceProcAddr(logicalDevice, "vkCreateSwapchainKHR")
    bundle.swapchain = vkCreateSwapchainKHR(logicalDevice, createInfo, None)

    vkGetSwapchainImagesKHR = vkGetDeviceProcAddr(logicalDevice, "vkGetSwapchainImagesKHR")

    images = vkGetSwapchainImagesKHR(logicalDevice, bundle.swapchain)

    for image in images:

        components = VkComponentMapping(r=VK_COMPONENT_SWIZZLE_IDENTITY,
                                        g=VK_COMPONENT_SWIZZLE_IDENTITY,
                                        b=VK_COMPONENT_SWIZZLE_IDENTITY,
                                        a=VK_COMPONENT_SWIZZLE_IDENTITY)

        subresourceRange = VkImageSubresourceRange(
            aspectMask=VK_IMAGE_ASPECT_COLOR_BIT,
            baseMipLevel=0, levelCount=1,
            baseArrayLayer=0, layerCount=1
        )

        create_info = VkImageViewCreateInfo(image=image, viewType=VK_IMAGE_VIEW_TYPE_2D, format=format.format,
                                            components=components, subresourceRange=subresourceRange)

        swapchain_frame = frame.SwapChainFrame()
        swapchain_frame.image = image
        swapchain_frame.image_view = vkCreateImageView(device=logicalDevice, pCreateInfo=create_info, pAllocator=None)
        bundle.frames.append(swapchain_frame)




    bundle.format = format.format
    bundle.extent = extent

    return bundle


