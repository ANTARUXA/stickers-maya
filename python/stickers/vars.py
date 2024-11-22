SUPPORTED_FORMATS = [".PNG", ".png"]
MASTER_GROUPS = "masterGroups"

STICKER_MASTER_GROUP = "stickerMaster"
LAYERS_MASTER_GROUP = "layerMaster"
POP_MASTER_GROUP = "popMaster"


STICKER_SYSTEMS = "systems"

SYSTEM_GEOSETUP = "geoSetup"
SYSTEM_MAINCONTROL = "mainControl"
SYSTEM_LOOKATCAMERA = "lookAtCamera"
SYSTEM_GEOPLANE = "geoPlane"
SYSTEM_LAYERS = "stickerLayers"

ATTRIBUTES = "attributes"
STICKER_ATTRIBUTES = "stickerAttributes"
LAYER_ATTRIBUTES = "layerAttributes"

CONTROLS = "controls"
STICKER_CONTROLS = "stickerControls"
LAYER_CONTROLS = "layerControls"

STICKER_FILENODES = "fileNodes"

STICKER_GEOSETUP_DRIVEN_ROOTS = "geoSetupDrivenRoots"

ENUM_NICE_NAME = "_" * 6  # Six underscores
INNIT_ATTR = {
    STICKER_ATTRIBUTES: [
        {
            "type": "enum",
            "longName": "stickerSeparator",
            "niceName": ENUM_NICE_NAME,
            "enumName": "STICKERS:",
            "channelBox": True,
        },
        {
            "type": "float",
            "longName": "offsetProjection",
            "niceName": "Margen de Proyeccion",
        },
        {
            "type": "bool",
            "longName": "lookAtCamera",
            "niceName": "Orientar hacia Camara",
        },
        {
            "type": "bool",
            "longName": "detachPlane",
            "niceName": "Separar Plano"},
        {
            "type": "enum",
            "longName": "layersSeparator",
            "niceName": ENUM_NICE_NAME,
            "enumName": "LAYERS:",
            "channelBox": True,
        },
    ],
    LAYER_ATTRIBUTES: [{
        "type": "long",
        "longName": "{layerName}Texture",
        "niceName": "{LayerName} Texture",
    }],
}
