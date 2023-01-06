from config import *



def supported(extentions: list, layers: list, debug: bool):


    supportedExtensions = [extention.extensionName for extention in vkEnumerateInstanceExtensionProperties(None)]
    

    if debug:
        print("Supported extensions:")
        for v in supportedExtensions:
            print(f"\t\"{v}\"")

    for v in extentions:
        if v in supportedExtensions:
            if debug:
                print(f"Extension \"{v}\" supported")
        else:
            if debug:
                print(f"Extension \"{v}\" not supported!!")
            return False

    supportedLayers = [layer.layerName for layer in vkEnumerateInstanceLayerProperties()]

    if debug:
        print("Supported layers:")
        for v in supportedLayers:
            print(f"\t\"{v}\"")
    
    for v in layers:
        if v in supportedLayers:
            if debug:
                print(f"Layer \"{v}\" supported")
        else:
            if debug:
                print(f"Layer \"{v}\" not supported!!")
            return False
    
    return True





def make_instance(debug, appName):

    if debug: print("Making vulkan instance")

    #version = vkEnumerateInstanceVersion()

    #if debug:
    #    print(f"Variant: {version >> 29}\nMajor: {VK_VERSION_MAJOR(version)}\nMinor: {VK_VERSION_MINOR(version)}\n Patch: {VK_VERSION_PATCH(version)}")
    

    version = VK_MAKE_VERSION(1, 0, 0)

    """
    def VkApplicationInfo(
        sType=VK_STRUCTURE_TYPE_APPLICATION_INFO,
        pNext=None,               # pointer to next application if you want multiple applications
        pApplicationName=None,    # app name
        applicationVersion=None,  # app version
        pEngineName=None,         # engine name
        engineVersion=None,       # engine version
        apiVersion=None,          # api version
        ):
    
    """

    appInfo = VkApplicationInfo(
        pApplicationName = appName,
        applicationVersion = version,
        pEngineName = "a",
        engineVersion = version,
        apiVersion = version
    )

    # A lot of things in vulkan are "opt-in", so you have to add the extentions of features you want to use yourself

    extentions = glfw.get_required_instance_extensions()

    if debug:
        extentions.append(VK_EXT_DEBUG_REPORT_EXTENSION_NAME)


    if debug:
        print(f"Extentions to be requested for glfw:")

        for v in extentions:
            print(f"\"{v}\"")

    layers = []
    if debug:
        layers.append("VK_LAYER_KHRONOS_validation")

    supported(extentions, layers, debug)

    

    """
        from _vulkan.py:
        def VkInstanceCreateInfo(
            sType=VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pNext=None,
            flags=None,
            pApplicationInfo=None,
            enabledLayerCount=None,ppEnabledLayerNames=None,
            enabledExtensionCount=None,ppEnabledExtensionNames=None,
        )
    """

    createInfo = VkInstanceCreateInfo(
        pApplicationInfo = appInfo,
        enabledLayerCount = len(layers), ppEnabledLayerNames = layers,
        enabledExtensionCount = len(extentions), ppEnabledExtensionNames = extentions
    )


    """
        def vkCreateInstance(
            pCreateInfo,
            pAllocator,
            pInstance=None,
        )
        
        throws exception on failure
    """



    try:
        return vkCreateInstance(createInfo, None)
    except:
        if debug:
            print("Failed to create instance!")
        
        return None

