from config import *
import logging
import queue_families

"""
    Vulkan separates the concept of physical and logical devices. 
    A physical device usually represents a single complete implementation of Vulkan 
    (excluding instance-level functionality) available to the host, 
    of which there are a finite number. 

    A logical device represents an instance of that implementation 
    with its own state and resources independent of other logical devices.
"""










def choose_physical_device(instance, debug):

    if debug:
        print("Choosing physical device")

    # vkEnumeratePhysicalDevices(instance) -> List(vkPhysicalDevice)

    availableDevices = vkEnumeratePhysicalDevices(instance)

    if debug:
        print(f"{len(availableDevices)} physical devices available")


    # check if a suitable device can be found
    for device in availableDevices:
        if debug:
            log_device_properties(device)
        if is_suitable(device, debug):
            return device


    return None



def log_device_properties(device):

    properties = vkGetPhysicalDeviceProperties(device)

    print(f"Device name: {properties.deviceName}")

    print("Device type: ", end="")

    if properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_CPU:
        print("CPU")
    elif properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU:
        print("Discrete GPU")
    elif properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU:
        print("Integrated GPU")
    elif properties.deviceType == VK_PHYSICAL_DEVICE_TYPE_VIRTUAL_GPU:
        print("Virtual GPU")
    else:
        print("Other")


def is_suitable(device, debug):
    if debug:
        print("Checking if device is suitable")

    requestedExtensions = [
        VK_KHR_SWAPCHAIN_EXTENSION_NAME
    ]

    if debug:
        print("Requesting device extensions:")

        for v in requestedExtensions:
            print(f"\t\"{v}\"")

    if check_device_extension_support(device, requestedExtensions, debug):

        if debug:
            print("Device can support the extensions!")
        return True

    if debug:
        print("Device doesn't support required extensions.")

    return False



def check_device_extension_support(device, requestedExtensions, debug):

    supportedExtensions = [v.extensionName for v in vkEnumerateDeviceExtensionProperties(device, None)]

    if debug:
        print("Device supports following extensions:")

        for v in supportedExtensions:
            print(f"\t\"{v}\"")

    for v in requestedExtensions:
        if v not in supportedExtensions:
            return False

    return True





def create_logical_device(physicalDevice, instance, surface, debug):
    indices = queue_families.find_queue_families(physicalDevice, instance, surface, debug)
    uniqueIndices = [indices.graphicsFamily]
    if indices.graphicsFamily != indices.presentFamily:
        uniqueIndices.append(indices.presentFamily)

    queueCreateInfo = []

    for queueFamilyIndex in uniqueIndices:
        queueCreateInfo.append(VkDeviceQueueCreateInfo(
            queueFamilyIndex=queueFamilyIndex,
            queueCount=1,
            pQueuePriorities=[1.0]
        ))

    deviceFeatures = VkPhysicalDeviceFeatures()

    enabledLayers = []
    if debug:
        enabledLayers.append("VK_LAYER_KHRONOS_validation")


    deviceExtensions = [
        VK_KHR_SWAPCHAIN_EXTENSION_NAME
    ]


    createInfo = VkDeviceCreateInfo(
        queueCreateInfoCount=len(queueCreateInfo),
        pQueueCreateInfos=queueCreateInfo,
        enabledExtensionCount=len(deviceExtensions),
        ppEnabledExtensionNames=deviceExtensions,
        pEnabledFeatures=[deviceFeatures],
        enabledLayerCount=len(enabledLayers),
        ppEnabledLayerNames=enabledLayers
    )

    return vkCreateDevice(physicalDevice=physicalDevice, pCreateInfo=[createInfo], pAllocator=None)


def get_queues(physicalDevice, device, instance, surface, debug):

    indices = queue_families.find_queue_families(physicalDevice, instance, surface, debug)

    return [
        vkGetDeviceQueue(
            device=device,
            queueFamilyIndex=indices.graphicsFamily,
            queueIndex=0
        ),
        vkGetDeviceQueue(
            device=device,
            queueFamilyIndex=indices.presentFamily,
            queueIndex=0
        )]







