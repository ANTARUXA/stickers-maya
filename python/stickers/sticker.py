#!/usr/bin/env pyth
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Antaruxa S.L - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by:
# Andrés Méndez del Río <andres.mendez@antaruxa.com>, 2023
# Cristina Fernandez Gomez <cristina.fernandez@antaruxa.com>, 2023
# pylint: disable=[consider-using-f-string]
import re

from . import parser
from .vars import *  # pylint: disable=[ unused-wildcard-import, wildcard-import]


class Sticker:  # pylint: disable=too-many-instance-attributes
    """Objeto para manejar la creacion y almacenaje de informacion de un sticker del sistema facial
    Contiene multiples variables como su nombre, localizacion(Flag), indice,
    las capas que posee, la geometria a la que va anclado
    Posee todos los metodos para su creacion y manejo de datos.
    """

    def __init__(self, name, layers=None, geometry=None, maps=None, file_path=None, is_sequence=0):
        self.parser = parser.Parser()
        self.file_path = file_path
        self.name = name
        self.layers = layers if layers else []
        self.texture_maps = maps if maps else []
        self.geometry = geometry if geometry else ""
        self.geo_mesh = self.geometry.split(".")[0]
        self.root_name = "{name}_{description}".format(description="sticker", name=name)
        self.is_sequence = is_sequence

        self.sticker_data = {
            "self": self,
            CONTROLS: {STICKER_CONTROLS: [], LAYER_CONTROLS: []},
            MASTER_GROUPS: {
                STICKER_MASTER_GROUP: {},
                LAYERS_MASTER_GROUP: {},
                POP_MASTER_GROUP: {},
            },
            STICKER_SYSTEMS: {
                SYSTEM_GEOSETUP: {},
                SYSTEM_MAINCONTROL: {},
                SYSTEM_LOOKATCAMERA: {},
                SYSTEM_GEOPLANE: {},
                SYSTEM_LAYERS: {},
            },
            ATTRIBUTES: {STICKER_ATTRIBUTES: {}, LAYER_ATTRIBUTES: {}},
            "materials": {
                "aiMatte": {},
            },
            "files": {},
            "projections": {},
            "constraints": {},
            STICKER_GEOSETUP_DRIVEN_ROOTS: [],
        }

    def create(self):
        """Construye el sticker en el programa DCC

        Crea los nodos principales del sticker:
        (grupo maestro, transform con point_on_poly_constraint y grupo maestro de capas)
        Crea los sistemas principales del sticker para su funcionamiento
        Crea cada capa definida en el sticker
        Crea los atributos que controlan diferentes funcionalidades del sticker
        Crea los constraints y dependencias del sticker
        """

        # Create top groups of the sticker
        self.create_sticker_top_groups()

        self.create_sticker_systems()

        for layer in self.layers:
            self.create_layer(
                self.root_name,
                layer.get("layerName"),
                self.sticker_data.get(MASTER_GROUPS).get(LAYERS_MASTER_GROUP),
            )
        self.create_layer_controls()

        self.create_attributes()
        self.create_constraints()
        self.create_offset_projection_subsystems()
        self.create_layer_shading_nodes()
        self.apply_to_material()

    def create_sticker_top_groups(self):
        """Crea los grupos principales del sticker

        El grupo maestro, el que recibe el pointOnPoly Constraint y el grupo maestro de capas
        """
        # Create sticker's master group
        sticker_master_group = self.parser.create_group(self.root_name)
        # Update sticker_data with master root
        self.sticker_data[MASTER_GROUPS].update(
            {STICKER_MASTER_GROUP: sticker_master_group}
        )

        # Creates PointOnPoly group, it will recieve the information of the pointOnPoly Constraint
        pop_root = self.parser.create_group(
            self.root_name + "_POP",
            parent=sticker_master_group,
        )
        self.sticker_data[MASTER_GROUPS].update({POP_MASTER_GROUP: pop_root})

        # Creates Layer's root group
        layers_master_group = self.parser.create_group(
            self.root_name + "_layers",
            parent=pop_root,
        )
        self.sticker_data[MASTER_GROUPS].update(
            {LAYERS_MASTER_GROUP: layers_master_group}
        )

        self.sticker_data[STICKER_GEOSETUP_DRIVEN_ROOTS].append(layers_master_group)

    def create_sticker_systems(self):
        """Llama a las funciones que crean los sistemas principales del sticker

        Geo setup, main control, geometry plane, look at camera.
        """
        # Obtenemos el grupo anclado a la geometria (pointOnPolyConstraint),
        # todos los sistemas iran emparentados a este grupo
        point_on_poly_root = self.sticker_data.get(MASTER_GROUPS).get(POP_MASTER_GROUP)

        self.create_geo_setup(self.root_name, point_on_poly_root)
        self.create_main_control(self.root_name, point_on_poly_root)
        self.create_geo_plane(self.root_name, point_on_poly_root)
        self.create_look_at_camera(self.root_name, point_on_poly_root)

    def create_layer(self, sticker_name_string, layer_name, chain_parent):
        """Crea una layer

        Args:
            sticker_name_string (str): Base Name Pattern
            layer_name (str): Name of the layer to create.
            chain_parent (PyNode): Parent node of the resulting system

        Returns:
            list: List of layer's nodes
        """
        chain_name, chain_transforms = self.parser.create_system(
            sticker_name_string, layer_name, ["grp", "root", "cns", "ctl"]
        )
        self.sticker_data[CONTROLS][LAYER_CONTROLS].append(chain_transforms[-1])
        self.parser.hierarchy_parent(chain_transforms, chain_parent)
        chain_transforms[1].translateZ.set(1)

        layer_proyection_root = self.parser.create_group(
            chain_name + "_translateOffset", parent=chain_transforms[0]
        )

        ik_start = self.parser.create_joint(
            chain_name + "_ik", parent=layer_proyection_root
        )

        ik_end = self.parser.create_joint(
            chain_name + "_ikEnd", position=[0, 0, 1], parent=ik_start
        )
        ik_handle, _effector = self.parser.create_ik_handles(
            name=chain_name, start_joint=ik_start, end_effector=ik_end
        )

        self.parser.parent_nodes(ik_handle, chain_transforms[-1])

        layer_proyection_grp = self.parser.create_group(
            chain_name + "_scaleOffset", parent=ik_start
        )
        layer_3d_texture = self.parser.create_3d_texture(
            "place3dTexture",
            name=chain_name + "_place3dTexture",
            parent=layer_proyection_grp,
            translate=[0, 0, 1],
            scale=[-1, 1, -1],
        )
        self.sticker_data[STICKER_SYSTEMS][SYSTEM_LAYERS].update(
            {
                layer_name: {
                    "chain_transforms": chain_transforms,
                    "joints": [ik_start, ik_end],
                    "layerCtlRoot": chain_transforms[1],
                    "transOffset": layer_proyection_root,
                    "scaleOffset": layer_proyection_grp,
                    "place3dTexture": layer_3d_texture,
                }
            }
        )
        return chain_transforms

    def create_attributes(self):
        """Create All sticker and layer attributes inside the sticker mainControl."""
        # Get main Control node
        main_control = self.sticker_data[CONTROLS][STICKER_CONTROLS][1]

        # Runs the definition of the sticker only attributes to create
        for attr_definition in INNIT_ATTR[STICKER_ATTRIBUTES]:
            # Runs the parser and returns the created attribute
            created_attr = self.parser.create_attribute(main_control, **attr_definition)
            # Updates sticker data attributes dictionary with the created attribute
            self.sticker_data[ATTRIBUTES][STICKER_ATTRIBUTES].update(created_attr)

        # Runs loop for each layer to create.
        for layer in self.layers:
            # Runs the definition of the layer only attributes to create
            for attr_definition in INNIT_ATTR[LAYER_ATTRIBUTES]:
                # Formats any string inside the Layer's attribute definitions
                # with the equivalent value and creates a new formatted dictionary definition
                attr_definition = {
                    key: (
                        value.format(
                            layerName=layer.get("layerName"),
                            LayerName=layer.get("layerName").capitalize(),
                        )
                        if isinstance(value, str)
                        else value
                    )
                    for key, value in attr_definition.items()
                }

                if self.is_sequence == 2:
                    attr_definition.update({"keyable":True,"channelBox":True})

                # Runs the parser and returns the created attribute
                created_attr = self.parser.create_attribute(
                    main_control, **attr_definition
                )
                # Updates sticker data attributes dictionary with the created attribute
                self.sticker_data[ATTRIBUTES][LAYER_ATTRIBUTES].update(created_attr)

    def create_constraints(self):
        """Master function used to create all the constraints necessary
        to make the system function correctly. It calls every other helper function
        to create specific constraints, each with its own parameters.
        """
        geo_setup_cns = self.create_cns_geo_setup()
        main_control_cns = self.createo_cns_main_control()
        # geoPlaneCns = self.create_cns_geo_setup()
        self.sticker_data.get("constraints").update(
            {SYSTEM_GEOSETUP: geo_setup_cns, SYSTEM_MAINCONTROL: main_control_cns}
        )
        # self.connect_constraint_weights(main_control_cns)
        # Parent constraint every root group to geoSetup ik

    def create_geo_setup(self, sticker_name_string, chain_parent):
        """Crea el sistema principal geoSetup

        Args:
            sticker_name_string (string): Nombre del sticker
            chain_parent (string): Nodo al que ira emparentado el sistema creado

        Returns:
            list: Lista de transforms creados del sistema geoSetup
        """
        # List of all geoSetup formatted names
        chain_name, chain_transforms = self.parser.create_system(
            sticker_name_string,
            SYSTEM_GEOSETUP,
            ["surface", "normalVector", "detach", "offset"],
        )

        self.parser.hierarchy_parent(chain_transforms, chain_parent)
        # self.create_constraints(chain_transforms)
        base_joint = self.parser.create_joint(
            chain_name + "_ik", parent=chain_transforms[-1]
        )
        end_joint = self.parser.create_joint(
            chain_name + "_ikEnd",
            position=[0, 0, 1],
            parent=base_joint,
        )

        ik_handle, effector = self.parser.create_ik_handles(
            name=chain_name,
            start_joint=base_joint,
            end_effector=end_joint,
            solver="ikSCsolver",
        )

        self.sticker_data[STICKER_SYSTEMS].update(
            {
                SYSTEM_GEOSETUP: {
                    "chain_transforms": chain_transforms,
                    "joints": [base_joint, end_joint],
                    "ikHandle": ik_handle,
                    "effector": effector,
                }
            }
        )
        chain_transforms[-1].translateZ.set(-1)
        return chain_transforms

    def create_look_at_camera(self, sticker_name_string, chain_parent):
        """Creates lookAtCamera system

        Args:
            sticker_name_string (str): Base Name Pattern
            chain_parent (PyNode): Parent node of the resulting system

        Returns:
            list: List of lookAtCamera's nodes
        """
        _chain_name, chain_transforms = self.parser.create_system(
            sticker_name_string, "lookAtCamera", ["root", "cns", "aimSticker"]
        )
        self.parser.hierarchy_parent(chain_transforms[:-1], chain_parent)
        self.sticker_data[STICKER_SYSTEMS].update(
            {
                "lookAtCamera": {
                    "chain_transforms": chain_transforms,
                    "cns": chain_transforms[-2],
                    "aimSticker": chain_transforms[-1],
                }
            }
        )
        self.parser.parent_nodes(chain_transforms[-1], chain_transforms[0])
        self.parser.parent_nodes(
            self.sticker_data[STICKER_SYSTEMS][SYSTEM_GEOSETUP]["ikHandle"],
            chain_transforms[1],
        )
        return chain_transforms

    def create_geo_plane(self, sticker_name_string, chain_parent, _scale=2.0):
        """Crea el sistema del geoPlane

        Args:
            sticker_name_string (str): Base Name Pattern
            chain_parent (PyNode): Parent node of the resulting system
            scale (float, optional): polyPlane creation scale. Defaults to 2.0.

        Returns:
            list: List of geoPlane's nodes
        """
        chain_name, chain_transforms = self.parser.create_system(
            sticker_name_string, "geoPlane", ["root", "cns"]
        )
        self.sticker_data[STICKER_GEOSETUP_DRIVEN_ROOTS].append(chain_transforms[0])
        self.parser.hierarchy_parent(chain_transforms, chain_parent)
        bind_joint = self.parser.create_joint(
            chain_name + "_bind", parent=chain_transforms[-1]
        )
        plane, plane_shape = self.parser.create_plane(
            chain_name + "_geoPlane", axis=[0, 0, 1]
        )

        # pm.matchTransform(plane,self.sticker_data[MASTER_GROUPS][POP_MASTER_GROUP])
        self.sticker_data[STICKER_SYSTEMS].update(
            {
                "geoPlane": {
                    "chain_transforms": chain_transforms,
                    "geometry": plane,
                    "planeShape": plane_shape,
                    "joint": bind_joint,
                }
            }
        )
        return chain_transforms

    def create_main_control(self, sticker_name_string, chain_parent):
        """Crea el sistema mainControl

        Args:
            sticker_name_string (str): Base Name Pattern
            chain_parent (PyNode): Parent node of the resulting system

        Returns:
            list: List of mainControl's nodes
        """
        _chain_name, chain_transforms = self.parser.create_system(
            sticker_name_string,
            "mainControl",
            ["root", "surfaceCtl", "npo", "cns", "ctl", "scaleInit"],
        )
        self.parser.hierarchy_parent(chain_transforms[:-1], chain_parent)
        self.parser.parent_nodes(chain_transforms[-1], chain_transforms[-4])
        self.sticker_data[STICKER_SYSTEMS].update(
            {
                "mainControl": {
                    "chain_transforms": chain_transforms,
                    "ctl": chain_transforms[4],
                    "surfaceCtl": chain_transforms[1],
                    "scaleInit": chain_transforms[-1],
                }
            }
        )
        self.sticker_data[CONTROLS][STICKER_CONTROLS].extend(
            [chain_transforms[1], chain_transforms[4]]
        )
        self.create_sticker_controls()
        return chain_transforms

    def create_cns_geo_setup(self):
        """Creates all constraints needed for the geoSetup System.

        Returns:
            dict: Dictionary containing all the constraints created
        """
        # Creates a Point On Poly Constraint, driver is the vertex the system is attached on,
        # the driven is the POP_root group of the sticker
        cns = self.parser.point_on_poly_constraint(
            self.sticker_data[MASTER_GROUPS][POP_MASTER_GROUP] + "Constraint",
            driver=self.geometry,
            driven=self.sticker_data[MASTER_GROUPS][POP_MASTER_GROUP],
        )

        # Geometry Constraint appplied to the first group of the geoSetup chain (Surface group)
        surface_cns = self.parser.apply_constraint(
            "geometryConstraint",
            self.geometry,
            self.sticker_data[STICKER_SYSTEMS][SYSTEM_GEOSETUP]["chain_transforms"][0],
            name="{0}_geoConstraint".format(self.root_name),
        )

        # Normal Constraint applied to the second group of the geoSetup chain (normalVector)
        normal_cns = self.parser.apply_constraint(
            "normalConstraint",
            self.geometry,
            self.sticker_data[STICKER_SYSTEMS][SYSTEM_GEOSETUP]["chain_transforms"][1],
            aimVector=[0, 0, 1],
            name="{0}_normalConstraint".format(self.root_name),
        )
        # Apply Main Control Constraints to geoSetup surface and detach
        geo_setup_roots = []
        for root in self.sticker_data[STICKER_GEOSETUP_DRIVEN_ROOTS]:
            geo_setup_roots.append(
                self.parser.apply_constraint(
                    "parentConstraint",
                    self.sticker_data[STICKER_SYSTEMS][SYSTEM_GEOSETUP]["joints"][0],
                    root,
                    name="{0}_parentConstraint".format(root),
                )
            )
        return {
            "POP": cns,
            "surface": surface_cns,
            "normal": normal_cns,
            "geoSetupRoots": geo_setup_roots,
        }

    def createo_cns_main_control(self):
        """Creates all constraints needed for the mainControl System.

        Returns:
            dict: Dictionary containing all the constraints created
        """
        surface_ctl_geo_constraint = self.parser.apply_constraint(
            "geometryConstraint",
            self.geometry,
            self.sticker_data[STICKER_SYSTEMS]["mainControl"]["surfaceCtl"],
            name="{0}_geoCns".format(
                self.sticker_data[STICKER_SYSTEMS]["mainControl"]["surfaceCtl"]
            ),
        )
        surface_ctl_normal_constraint = self.parser.apply_constraint(
            "normalConstraint",
            self.geometry,
            self.sticker_data[STICKER_SYSTEMS]["mainControl"]["surfaceCtl"],
            aimVector=[0, 0, 1],
            name="{0}_normalCns".format(
                self.sticker_data[STICKER_SYSTEMS]["mainControl"]["surfaceCtl"]
            ),
        )

        drive_geo_setup = self.parser.apply_constraint(
            "pointConstraint",
            self.sticker_data[STICKER_SYSTEMS]["mainControl"]["ctl"],
            self.sticker_data[STICKER_SYSTEMS][SYSTEM_GEOSETUP]["chain_transforms"][0],
            name="{0}_pointConstraint".format(
                self.sticker_data[STICKER_SYSTEMS]["mainControl"]["ctl"]
            ),
        )
        # Creates Parent constraint from the main control ctl to the ik system in geoSetup.
        detach_cns_connections = {
            "attribute": self.sticker_data[ATTRIBUTES][STICKER_ATTRIBUTES].get(
                "detachPlane"
            ),
            "weights": {
                "{0}W0".format(self.sticker_data[CONTROLS][STICKER_CONTROLS][1]): True
            },
            "reverseNode": False,
        }

        detach_cns = self.parser.apply_constraint(
            "parentConstraint",
            self.sticker_data[STICKER_SYSTEMS]["mainControl"]["ctl"],
            self.sticker_data[STICKER_SYSTEMS][SYSTEM_GEOSETUP]["chain_transforms"][2],
            name="{0}_detachConstraint".format(
                self.sticker_data[STICKER_SYSTEMS]["mainControl"]["ctl"],
            ),
            connections=detach_cns_connections,
        )

        look_at_camera_connections = {
            "attribute": self.sticker_data[ATTRIBUTES][STICKER_ATTRIBUTES].get(
                "lookAtCamera"
            ),
            "weights": {
                "{0}W0".format(self.sticker_data[CONTROLS][STICKER_CONTROLS][1]): False,
                "{0}W1".format(
                    self.sticker_data[STICKER_SYSTEMS]["lookAtCamera"]["aimSticker"]
                ): True,
            },
            "reverseNode": True,
        }
        look_at_camera_space_switch = self.parser.apply_constraint(
            "parentConstraint",
            [
                self.sticker_data[STICKER_SYSTEMS]["mainControl"]["ctl"],
                self.sticker_data[STICKER_SYSTEMS]["lookAtCamera"]["aimSticker"],
            ],
            self.sticker_data[STICKER_SYSTEMS]["lookAtCamera"]["cns"],
            name="{0}_lookCns".format(
                self.sticker_data[STICKER_SYSTEMS]["lookAtCamera"]["cns"]
            ),
            connections=look_at_camera_connections,
        )
        return {
            "surfaceGeoCns": surface_ctl_geo_constraint,
            "surfaceNormalCns": surface_ctl_normal_constraint,
            "driveGeoSetup": drive_geo_setup,
            "detachCns": detach_cns,
            "spaceSwitch_LAC": look_at_camera_space_switch,
        }

    def create_sticker_controls(self):
        """Creates control shapes for both surface and main control transforms."""
        surface_ctl = self.sticker_data[CONTROLS][STICKER_CONTROLS][0]
        _surface_shp = self.parser.create_control_shape(surface_ctl, radius=1.5)
        main_ctl = self.sticker_data[CONTROLS][STICKER_CONTROLS][1]
        _main_shp = self.parser.create_control_shape(main_ctl, radius=1.2)

    def create_layer_controls(self):
        """Creates control shapes for all layers created."""
        radius = 1
        for layer in self.sticker_data[CONTROLS][LAYER_CONTROLS]:
            _layer_shp = self.parser.create_control_shape(layer, radius=radius)
            radius -= 0.15

    def create_offset_projection_subsystems(self):
        """Creates all the nodes for off:set projection subsystems
        Nodes: OneMinusX (Multiply Divide), addDirectionalOffset(plusMinusAverage), lookAtCameraOffset\
        disableIfDetach(condition), reverseOffset(multiplyDivide), layerCtlAddMargin(plusMinusAverage) \
        enableIfDetach(condition)

        translateOffset: oneMinusX_halfY (multiplyDivide), addDirectionalOffset(plusMinusAverage)
        """
        mainControl_attr_ref = self.sticker_data[ATTRIBUTES][STICKER_ATTRIBUTES]
        # Sticer identifier prefix avoiding duplicate names
        sticker_prefix = "{0}_{1}".format(self.name, "offsetProjection")

        # New utility node name
        name = "{0}_oneMinusX_halfY".format(sticker_prefix)

        # Create utility node
        oneminusx_doubley = self.parser.create_utility_node(
            "multiplyDivide",  # Type of utility node created
            node_name=name,  # Name of utility node
            asUtility=True,  # If it's a utility node
            connections=[  # Connection list that will be parsed and automatically create connections
                {
                    mainControl_attr_ref.get(
                        "offsetProjection"  # Driver
                    ): "{0}.input1X".format(
                        name
                    )  # Driven
                },
                {
                    mainControl_attr_ref.get("offsetProjection"): "{0}.input1Y".format(
                        name
                    )
                },
            ],
            # Attribute dictionary with custom values
            attributes={"input2X": -1, "input2Y": 0.5},
        )

        name = "{0}_addDirectionalOffset".format(sticker_prefix)
        add_directional_offset = self.parser.create_utility_node(
            "plusMinusAverage",
            node_name=name,
            asUtility=True,
            connections=[
                {
                    "{0}.outputX".format(
                        oneminusx_doubley
                    ): "{0}.input2D[0].input2Dx".format(name)
                },
                {
                    "{0}.outputY".format(
                        oneminusx_doubley
                    ): "{0}.input2D[0].input2Dy".format(name)
                },
            ],
            attributes={"input2D[1].input2Dx": -0.5, "input2D[1].input2Dy": 0.8},
        )

        self.create_translate_offset_subsystem(
            sticker_prefix, mainControl_attr_ref, add_directional_offset
        )
        self.create_scale_offset_subsystem(
            sticker_prefix, mainControl_attr_ref, add_directional_offset
        )

        # Create A oneMinusX_halfY
        # Create B addDirectionalOffset
        # Connect A-X -> B-2D[0]x
        # Call translateOffset_subsystem

    def create_translate_offset_subsystem(
        self, sticker_prefix, mainControl_attr_ref, add_directional_offset
    ):
        """Crea el subsistema translate_offset basado en el atributo offsetProjection"""
        name = "{0}_disableIfDetach".format(sticker_prefix)

        disable_if_detach_node = self.parser.create_utility_node(
            "condition",
            node_name=name,
            asUtility=True,
            connections=[
                {mainControl_attr_ref.get("detachPlane"): "{0}.firstTerm".format(name)},
                {
                    "{0}.output2D.output2Dx".format(
                        add_directional_offset
                    ): "{0}.colorIfFalseB".format(name)
                },
                {
                    "{0}.output2D.output2Dx".format(
                        add_directional_offset
                    ): "{0}.colorIfTrueR".format(name)
                },
            ],
            attributes={"secondTerm": 1, "colorIfFalseR": 0},
        )
        name = "{0}_reverseOffset".format(sticker_prefix)
        reverseOffset_node = self.parser.create_utility_node(
            "multiplyDivide",
            node_name=name,
            asUtility=True,
            connections=[
                {
                    "{0}.outColorB".format(
                        disable_if_detach_node
                    ): "{0}.input1Z".format(name)
                }
            ],
            attributes={"input2Z": -1},
        )

        name = "{0}_layerOffset".format(sticker_prefix)
        layerOffset_node = self.parser.create_utility_node(
            "plusMinusAverage",
            node_name=name,
            asUtility=True,
            connections=[
                {
                    "{0}.outputZ".format(
                        reverseOffset_node
                    ): "{0}.input2D[0].input2Dx".format(name)
                }
            ],
            attributes={"input2D[1].input2Dx": 1},
        )
        self.parser._create_utility_connections(
            [
                {
                    "{0}.outColorB".format(
                        disable_if_detach_node
                    ): "{0}.translateZ".format(
                        self.sticker_data[STICKER_SYSTEMS][SYSTEM_GEOSETUP]
                        .get("chain_transforms")[-1]
                        .name()
                    )
                }
            ]
        )
        for layer_definition in self.sticker_data[STICKER_SYSTEMS][
            SYSTEM_LAYERS
        ].values():
            self.parser._create_utility_connections(
                [
                    {
                        "{0}.output2Dx".format(
                            layerOffset_node
                        ): "{0}.translateZ".format(
                            layer_definition.get("layerCtlRoot").name()
                        )
                    },
                    {
                        "{0}.outColorR".format(
                            disable_if_detach_node
                        ): "{0}.translateZ".format(
                            layer_definition.get("transOffset").name()
                        )
                    },
                ]
            )
        # Create translateOffset_disabledIfDetach

    def create_scale_offset_subsystem(
        self, sticker_prefix, mainControl_attr_ref, add_directional_offset
    ):
        """ """
        name = "{0}_addLookAtCameraOffset".format(sticker_prefix)
        add_lookatcamera_offset_node = self.parser.create_utility_node(
            "plusMinusAverage",
            node_name=name,
            asUtility=True,
            connections=[
                {
                    "{0}.output2Dy".format(
                        add_directional_offset
                    ): "{0}.input2D[0].input2Dx".format(name)
                }
            ],
            attributes={"input2D[1].input2Dx": 1.2},
        )

        name = "{0}_scaleIfLookAtCamera".format(sticker_prefix)
        scale_if_lookatcamera_node = self.parser.create_utility_node(
            "condition",
            node_name=name,
            asUtility=True,
            connections=[
                {
                    "{0}.output2Dy".format(
                        add_directional_offset
                    ): "{0}.colorIfFalseB".format(name)
                },
                {
                    "{0}.output2Dx".format(
                        add_lookatcamera_offset_node
                    ): "{0}.colorIfTrueB".format(name)
                },
                {
                    mainControl_attr_ref.get("lookAtCamera"): "{0}.firstTerm".format(
                        name
                    )
                },
            ],
            attributes={"secondTerm": 1},
        )
        name = "{0}_scaleInit".format(sticker_prefix)
        scaleInit_node = self.parser.create_utility_node(
            "multiplyDivide",
            node_name=name,
            asUtility=True,
            connections=[
                {
                    "{0}.scale".format(
                        self.sticker_data[STICKER_SYSTEMS]["mainControl"]["ctl"].name()
                    ): "{0}.input1".format(name)
                },
                {
                    "{0}.scale".format(
                        self.sticker_data[STICKER_SYSTEMS]["mainControl"][
                            "scaleInit"
                        ].name()
                    ): "{0}.input2".format(name)
                },
            ],
        )
        name = "{0}_flipStickerX".format(sticker_prefix)
        flipx_sticker_condition = self.parser.create_utility_node(
            "condition",
            node_name=name,
            asUtility=True,
            connections=[
                {mainControl_attr_ref.get("flipX"): "{0}.firstTerm".format(name)},
            ],
            attributes={"secondTerm": 1, "colorIfTrueR": -1, "colorIfFalseR": 1},
        )

        name = "{0}_flipStickerY".format(sticker_prefix)
        flipy_sticker_condition = self.parser.create_utility_node(
            "condition",
            node_name=name,
            asUtility=True,
            connections=[
                {mainControl_attr_ref.get("flipY"): "{0}.firstTerm".format(name)},
            ],
            attributes={"secondTerm": 1, "colorIfTrueR": -1, "colorIfFalseR": 1},
        )
        name = "{0}_flipScaleSticker".format(sticker_prefix)
        flip_scale_sticker = self.parser.create_utility_node(
            "multiplyDivide",
            node_name=name,
            asUtility=True,
            connections=[
                {
                    "{0}.outColorR".format(
                        flipx_sticker_condition
                    ): "{0}.input1.input1X".format(name)
                },
                {
                    "{0}.outColorR".format(
                        flipy_sticker_condition
                    ): "{0}.input1.input1Y".format(name)
                },
                {
                    "{0}.outputX".format(scaleInit_node): "{0}.input2.input2X".format(
                        name
                    )
                },
                {
                    "{0}.outputY".format(scaleInit_node): "{0}.input2.input2Y".format(
                        name
                    )
                },
            ],
        )
        for layer_definition in self.sticker_data[STICKER_SYSTEMS][
            SYSTEM_LAYERS
        ].values():
            self.parser._create_utility_connections(
                [
                    {
                        "{0}.outColorB".format(
                            scale_if_lookatcamera_node
                        ): "{0}.scaleZ".format(layer_definition.get("scaleOffset"))
                    },
                    {
                        "{0}.outputY".format(
                            flip_scale_sticker
                        ): "{0}.scaleY".format(layer_definition.get("scaleOffset"))
                    },
                    {
                        "{0}.outputX".format(
                            flip_scale_sticker
                        ): "{0}.scaleX".format(layer_definition.get("scaleOffset"))
                    }
                ]
            )

    def create_layer_shading_nodes(self):
        """Creates shading nodes for each layer"""
        # Use layer name and definition to create shading nodes
        for layer_name, layer_definition in self.sticker_data[STICKER_SYSTEMS][
            SYSTEM_LAYERS
        ].items():
            # Fetch the place3dTexture node from the layer definition
            p3d = layer_definition.get("place3dTexture")
            # Create entry for each layer in the sticker_data.files dictionary
            self.sticker_data["files"][layer_name] = {}
            # Create entry for each layer in the sticker_data.projections dictionary
            self.sticker_data["projections"][layer_name] = {}
            # Call create_shading_nodes function to create shading nodes for each layer
            self.create_maps_shading_nodes(layer_name, p3d)

    def create_maps_shading_nodes(self, layer_name, p3d):
        """
        Creates file, projection & aiMatte nodes for each map declared in the sticker
        """
        for texture_map in self.texture_maps:
            is_sequence = self.is_sequence
            frame_extension = ""

            texture_map_file_path = self.file_path


            if self.is_sequence == 2:
                is_sequence = 1
                frame_extension = re.search(
                    r"\.([\d]*)\.", texture_map_file_path
                ).group(1)

            _p2d, file_node = self.parser.create_file_node(
                self.name,
                layer_name,
                texture_map,
                texture_map_file_path,
                frame_extension,
                is_sequence,
            )
            if self.is_sequence == 2:
                self.parser._create_utility_connections([
                    {
                        "{0}.{1}Texture".format(
                            self.sticker_data[STICKER_SYSTEMS]["mainControl"]["ctl"],
                            layer_name

                        ):"{0}.frameExtension".format(file_node)
                    }
                ])

            projection_node = self.parser.create_projection_node(
                self.name, layer_name, texture_map, p3d, file_node
            )
            matte_marerial = self.parser.create_aiMatte_material(
                self.name, layer_name, texture_map, projection_node
            )
            ## Update sticker_data with the created nodes

            self.sticker_data["projections"][layer_name].update(
                {texture_map: projection_node}
            )
            self.sticker_data["materials"]["aiMatte"].update(
                {texture_map: matte_marerial}
            )





        # for texture_map in self.texture_maps:
        #     # name_match_pattern = "{0}_{1}".format(self.name, texture_map)
        #     #
        #     # matched_textures_dict[texture_map] = self.build_texture_maps_dict(
        #     #     name_match_pattern, file_list
        #     # )
        #     #
        #     # texture_map_file_path = os.path.join(
        #     #     self.file_path, matched_textures_dict[texture_map][0]
        #     # )
        #     #
        #     texture_map_file_path = self.file_path
        #     frame_extension = False
        #     if img_sequence:
        #         frame_extension = re.search(
        #             r"\.([\d]*)\.", texture_map_file_path
        #         ).group(1)
        #
        #     _p2d, file_node = self.parser.create_file_node(
        #         self.name,
        #         layer_name,
        #         texture_map,
        #         texture_map_file_path,
        #         frame_extension,
        #     )
        #
        #     projection_node = self.parser.create_projection_node(
        #         self.name, layer_name, texture_map, p3d, file_node
        #     )
        #     matte_marerial = self.parser.create_aiMatte_material(
        #         self.name, layer_name, texture_map, projection_node
        #     )
        #     ## Update sticker_data with the created nodes
        #
        #     self.sticker_data["projections"][layer_name].update(
        #         {texture_map: projection_node}
        #     )
        #     self.sticker_data["materials"]["aiMatte"].update(
        #         {texture_map: matte_marerial}
        #     )

    def apply_to_material(self, layer="base", texture_map="color"):
        """Applies materials to the layers"""
        sticker_projection = self.sticker_data.get("projections").get(layer).get(texture_map)
        _new_material = self.parser.create_sticker_viewport_material(
            self.name, sticker_projection, self.geo_mesh
        )

        if self.parser.geo_has_stickers(self.geo_mesh):
            self.parser.insert_new_sticker_to_material(
                self.geo_mesh, sticker_projection
            )
