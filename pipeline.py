from config import *
import shaders


class InputBundle:
    def __init__(self, device, swapchainImageFormat, swapchainExtent, vertexFilePath, fragmentFilePath):
        self.device = device
        self.swapchainImageFormat = swapchainImageFormat
        self.swapchainExtent = swapchainExtent
        self.vertexFilePath = vertexFilePath
        self.fragmentFilePath = fragmentFilePath



class OutputBundle:
    def __init__(self, pipelineLayout, renderPass, pipeline):
        self.pipelineLayout = pipelineLayout
        self.renderPass = renderPass
        self.pipeline = pipeline


def create_render_pass(device, swapchainImageFormat):

    colorAttachment = VkAttachmentDescription(
        format=swapchainImageFormat,
        samples=VK_SAMPLE_COUNT_1_BIT,

        loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR,
        storeOp=VK_ATTACHMENT_STORE_OP_STORE,

        stencilLoadOp=VK_ATTACHMENT_LOAD_OP_DONT_CARE,
        stencilStoreOp=VK_ATTACHMENT_STORE_OP_DONT_CARE,

        initialLayout=VK_IMAGE_LAYOUT_UNDEFINED,
        finalLayout=VK_IMAGE_LAYOUT_PRESENT_SRC_KHR
    )

    colorAttachmentRef = VkAttachmentReference(
        attachment=0,
        layout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
    )

    subpass = VkSubpassDescription(
        pipelineBindPoint=VK_PIPELINE_BIND_POINT_GRAPHICS,
        colorAttachmentCount=1,
        pColorAttachments=colorAttachmentRef
    )


    renderPassInfo = VkRenderPassCreateInfo(
        attachmentCount=1,
        pAttachments=colorAttachment,
        subpassCount=1,
        pSubpasses=subpass
    )

    return vkCreateRenderPass(device, renderPassInfo, None)


def create_pipeline_layout(device):

    pushConstantInfo = VkPushConstantRange(
        stageFlags=VK_SHADER_STAGE_VERTEX_BIT, offset=0,
        size= 4 * 4 * 4
    )

    pipelineLayoutInfo = VkPipelineLayoutCreateInfo(
        pushConstantRangeCount=1, pPushConstantRanges=[pushConstantInfo],
        setLayoutCount=0
    )

    return vkCreatePipelineLayout(device, pipelineLayoutInfo, None)


def create_graphics_pipeline(inputBundle, debug):

    vertexInputInfo = VkPipelineVertexInputStateCreateInfo(
        vertexBindingDescriptionCount=0,
        vertexAttributeDescriptionCount=0
    )

    if debug:
        print(f"Load shader module: {inputBundle.vertexFilePath}")

    vertexShaderModule = shaders.create_shader_module(inputBundle.device, inputBundle.vertexFilePath)
    vertexShaderStageInfo = VkPipelineShaderStageCreateInfo(
        stage=VK_SHADER_STAGE_VERTEX_BIT,
        module=vertexShaderModule,
        pName="main"
    )

    inputAssembly = VkPipelineInputAssemblyStateCreateInfo(
        topology=VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST
    )

    viewport = VkViewport(
        x=0,
        y=0,
        width=inputBundle.swapchainExtent.width,
        height=inputBundle.swapchainExtent.height
    )

    scissor = VkRect2D(
        offset=[0,0],
        extent = inputBundle.swapchainExtent
    )

    viewPortState = VkPipelineViewportStateCreateInfo(
        viewportCount=1,
        pViewports=viewport,
        scissorCount=1,
        pScissors=scissor
    )


    rasterizer = VkPipelineRasterizationStateCreateInfo(
        depthClampEnable=VK_FALSE,
        rasterizerDiscardEnable=VK_FALSE,
        polygonMode=VK_POLYGON_MODE_FILL,
        lineWidth=1.0,
        cullMode=VK_CULL_MODE_BACK_BIT,
        frontFace=VK_FRONT_FACE_CLOCKWISE,
        depthBiasEnable=VK_FALSE
    )


    multisampling = VkPipelineMultisampleStateCreateInfo(
        sampleShadingEnable=VK_FALSE,
        rasterizationSamples=VK_SAMPLE_COUNT_1_BIT,

    )



    if debug:
        print(f"Load shader module: {inputBundle.fragmentFilePath}")

    fragmentShaderModule = shaders.create_shader_module(inputBundle.device, inputBundle.fragmentFilePath)
    fragmentShaderStageInfo = VkPipelineShaderStageCreateInfo(
        stage=VK_SHADER_STAGE_FRAGMENT_BIT,
        module=fragmentShaderModule,
        pName="main"
    )


    shaderStages = [vertexShaderStageInfo, fragmentShaderStageInfo]

    colorBlendAttachment = VkPipelineColorBlendAttachmentState(
        colorWriteMask=VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT,
        blendEnable=VK_FALSE
    )
    colorBlending = VkPipelineColorBlendStateCreateInfo(
        logicOpEnable=VK_FALSE,
        attachmentCount=1,
        pAttachments=colorBlendAttachment,
        blendConstants=[0.0, 0.0, 0.0, 0.0]
    )

    pipelineLayout = create_pipeline_layout(inputBundle.device)

    renderPass = create_render_pass(inputBundle.device, inputBundle.swapchainImageFormat)

    pipelineInfo = VkGraphicsPipelineCreateInfo(
        stageCount=len(shaderStages),
        pStages=shaderStages,
        pVertexInputState=vertexInputInfo,
        pInputAssemblyState=inputAssembly,
        pViewportState=viewPortState,
        pRasterizationState=rasterizer,
        pMultisampleState=multisampling,
        pColorBlendState=colorBlending,
        layout=pipelineLayout,
        renderPass=renderPass,
        subpass=0
    )


    graphicsPipeline = vkCreateGraphicsPipelines(inputBundle.device, VK_NULL_HANDLE, 1, pipelineInfo, None)[0]

    vkDestroyShaderModule(inputBundle.device, vertexShaderModule, None)
    vkDestroyShaderModule(inputBundle.device, fragmentShaderModule, None)

    return OutputBundle(
        pipelineLayout=pipelineLayout,
        renderPass=renderPass,
        pipeline=graphicsPipeline
    )



