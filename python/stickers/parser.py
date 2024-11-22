#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Antaruxa S.L - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by:
# Andrés Méndez del Río <andres.mendez@antaruxa.com>, 2023
# Cristina Fernandez Gomez <cristina.fernandez@antaruxa.com>, 2023

import importlib
import os


class Parser:
    """Custom wrappers of common functions and utilities using globals in order to avoid hardcoding maya commands"""

    def __init__(self):
        try:
            self.cmds = importlib.import_module("maya.cmds")
            self.pm = importlib.import_module("pymel.core")
        except:
            pass

    def hierarchy_parent(self, hierarchy_list, master_node):
        """Parents a list of nodes in reverse order.
        Each element gets parented to the previous node in the array,
        and the last one is parented to the master_node

        Args:
            hierarchy_list (List): List of built nodes we want to parent as hierarchy
            master_node (PyNode): Transform node that will be the parent of the entire hierarchy
        """
        # Creates a reverse ordered list
        reverse_hierarchy_list = hierarchy_list[::-1]
        # Creates a loop to get the object and its index
        for idx, grp in enumerate(reverse_hierarchy_list):
            # If the current grp is the first element of the hierarchy,
            # we parent to the chainParent and stop de loop
            if grp == hierarchy_list[0]:
                self.parent_nodes(grp, master_node)
                return
            self.parent_nodes(grp, reverse_hierarchy_list[idx + 1])

    # def __repr__(self):
    #     return dict(self.__class__)

    def update_name(self, chain, new_chain_part):
        """Updates the descriptor part of the node name with the parameter given

        Args:
            chain (str): original string name
            new_chain_part (str): new word that replaces "sticker" word

        Returns:
            str: Returns the new formatted string
        """
        # Split
        chain_split = chain.split("_")
        for idx, chain_part in enumerate(chain_split):
            if chain_part == "sticker":
                chain_split[idx] = new_chain_part
        return "_".join(chain_split)

    def exec_func(self, func, *args, **kwargs):
        """Abstract function to execute specific maya modules (self.cmds, pymel.core, etc.)
        With any function and specific arguments or keyword arguments

        Args:
            func (function): function to execute

        Returns:
            misc: Returns the output result of executing said function.
        """
        result = func(*args, **kwargs)
        return result

    def point_on_poly_constraint(self, chain_name, driver, driven):
        """Creates a poitOnPolyConstraint between the driver geometry and a transform node

        Args:
            chain_name (str): name of the point_on_poly_constraint
            driver (list): Driver Geometry (or vertex)
            driven (pymel.core.nodetypes.Transform): trasnform
        Returns:
            pymel.core.nodetypes.PointOnPolyConstraint: point_on_poly_constraint Node
        """
        self.pm.select([driver, driven])
        func = getattr(self.pm, "pointOnPolyConstraint")
        output = func(name=chain_name)
        output.offsetRotateX.set(-90)
        return output

    def apply_constraint(self, cns, drivers, driven, connections=None, **kwargs):
        """Abstract Function to create multiple constraints

        Args:
            cns (str): Type of constraint to create
            drivers (PyNode): Driver objects of the constraint
            driven (PyNode): Driven Objects of constraint
        Returns:
            pymel.core.nodetypes.{cns}: Returns constraint Object
        """

        if self.cmds.objExists(kwargs.get("name")):
            return self.pm.PyNode(kwargs.get("name"))
        func = getattr(self.pm, cns)
        cns = self.exec_func(func, drivers, driven, **kwargs)
        if connections:
            self.apply_constraint_connections(
                connections.get("attribute"),
                connections.get("reverseNode"),
                cns,
                connections.get("weights"),
            )
        return cns

    def create_control_shape(
        self, ctl_transform, shape_type="circle", normal=[0, 0, 1], **kwargs
    ):
        """
        Create simple circle shape (by default) oriented to x. And makes it the shape of the ctl_transform
        """
        shape = {"circle": "circle", "square": "nurbSquare"}
        func = getattr(self.pm, shape[shape_type])
        # Check if ctl_transform has any children (shapes)
        _ctl_shape = self.exec_func(
            func, name="_temp_{0}".format(ctl_transform.name()), normal=normal, **kwargs
        )[0]
        self.parent_shape(ctl_transform, _ctl_shape.getShape())
        print("parented shape to {0}".format(ctl_transform))
        self.pm.delete(_ctl_shape)

    def parent_shape(self, transform, shape):
        """Parents a given shape to the specified transform"""
        func = getattr(self.pm, "parent")

        self.exec_func(func, shape, transform, relative=True, shape=True)

    def apply_constraint_connections(self, attribute, reverse_node, cns_name, weights):
        """Create connections to the contraint's weights.
        Currently valid to one direct connection
        or one attribute driving 2 weights, with a reverse node inbetweeen

        Args:
            attribute (string): Main attribute that will drive the constraint's weights
            reverse_node (bool): Indicator that the connection will need a Reverse Node
            cns_name (str): Name of the contraint to be driven
            weights (dict): Dictionary describing the nature of the connection,
                            if its direct, it wont pass through the reverse node
        """
        if reverse_node:
            rev_node = self.cmds.shadingNode("reverse", asUtility=True)
            self.cmds.connectAttr(attribute, rev_node + ".inputX")
        for weight, direct_connection in weights.items():
            if direct_connection:
                self.cmds.connectAttr(attribute, cns_name + "." + weight)
                continue
            self.cmds.connectAttr(rev_node + ".outputX", cns_name + "." + weight)

    def create_plane(self, name, parent="", _position=None, **kwargs):
        """Creates a GeoPlane

        Args:
            name (string): GeoPlane transform's node name
            parent (str, optional): Parent node. Defaults to "".
            position (list, optional): Node's position. Defaults to [].

        Returns:
            tuple: Plane's transform and shape
        """
        if self.cmds.objExists(name):
            return self.pm.PyNode(name), self.pm.PyNode(name + "Shape")

        func = getattr(self.pm, "polyPlane")
        plane, plane_shape = self.exec_func(func, name=name, **kwargs)
        if parent:
            self.parent_nodes(plane, parent)
        return plane, plane_shape

    def create_group(self, nodes, *args, **kwargs):
        """Abstract function to custom create transform nodes.

        Args:
            nodes (str or list): List of names to create

        Returns:
            PyNode or list of PyNodes: returns every transform created
        """
        # Fetch the group function in pymel.core
        func = getattr(self.pm, "group")

        # If passed a list into nodes, executes recursively until completed
        if isinstance(nodes, list):
            # Creates a list with the created nodes
            node_list = [self.create_group(node, *args, **kwargs) for node in nodes]
            return node_list
        if self.cmds.objExists(nodes):
            return self.pm.PyNode(nodes)
        # Creates single transform.
        transform = self.exec_func(func, *args, name=nodes, empty=True, **kwargs)
        return transform

    def create_system(self, base_string, name_string, group_name_array):
        """Base function that creates the transform nodes for an specific chain, name and groups

        Args:
            parser (Parser): Parser to execute operations, will be replaced by an instance of class
            base_string (str): Name of parent sticker
            name_string (str): new descriptor name
            group_name_array (List[str]): list of group names that will compose the new system

        Returns:
            tuple: Returns a tuple of the new chain name and the newly created groups
        """
        # Updates 'base_string' descriptor field with 'name_string' value
        chain_base_name = base_string
        if name_string != "":
            chain_base_name = self.update_name(base_string, name_string)
        # Generates new list of goup names
        main_control_groups = [
            chain_base_name + "_" + new_group for new_group in group_name_array
        ]
        created_groups = self.create_group(main_control_groups)
        return chain_base_name, created_groups

    def create_ik_handles(
        self, name="", start_joint="", end_effector="", solver="ikSCsolver"
    ):
        """Wrapper of pm.ikHandle. Creates ikHandles with custom properties

        Args:
            name (str, optional): Node name. Defaults to "".
            start_joint (str, optional): Chain's starting joint. Defaults to "".
            end_effector (str, optional): Chain's ending joint. Defaults to "".
            solver (str, optional): ik Solver. Defaults to "ikSCsolver".

        Returns:
            tuple: ikHandle object reference and effector object reference
        """
        if self.cmds.objExists(name + "_ikh"):
            return self.pm.PyNode(name + "_ikh"), self.pm.PyNode(name + "_eff")
        func = getattr(self.pm, "ikHandle")

        handle, effector = self.exec_func(
            func,
            name=name + "_ikh",
            startJoint=start_joint,
            endEffector=end_effector,
            solver=solver,
        )
        handle.visibility.set(False)
        handle.translateZ.set(0)
        return handle, self.pm.rename(effector, name + "_eff")

    def parent_nodes(self, childs, parent):
        """Parent all child nodes to specific node

        Args:
            childs (list / pyNode): Node or list of nodes to parent
            parent (pyNode): Parent node
        """
        func = getattr(self.pm, "parent")

        if isinstance(childs, list):
            for child in childs:
                self.exec_func(func, child, parent)
            return
        self.exec_func(func, childs, parent)

    def create_attribute(self, node, keyable=True, channelBox=False, **kwargs):
        """Creates a custom attribute and sets it visible in the channelBox if requested

        Extends pm.addAttr and pm.setAttr functionality

        Args:
            node (string): Node's name that will get the attribute
            keyable (bool, optional): If the attribute will be keyable. Defaults to True.
            channelBox (bool, optional): If the attribute will be visible in the channelBox. Defaults to False.

        Returns:
            dict: Dictionary {Attribute's longName : Attribute path}
        """
        attribute_path = "{node}.{attr}".format(node=node, attr=kwargs.get("longName"))

        if self.cmds.objExists(attribute_path):
            return {kwargs.get("longName"): attribute_path}

        func = getattr(self.pm, "addAttr")
        set_func = getattr(self.pm, "setAttr")

        _attribute = self.exec_func(func, node, keyable=keyable, **kwargs)

        if channelBox:
            self.exec_func(set_func, attribute_path, channelBox=channelBox)
        output = {kwargs.get("longName"): attribute_path}
        return output

    def set_attribute(self, node, attribute, value):
        """Sets the node's specified attribute to a value

        Args:
            node (pyNode): Node to change its attribute
            attribute (str): Attribute name
            value (misc): Value for the specified attribute
        """
        getattr(node, attribute).set(value)

    def create_3d_texture(self, node, translate=None, scale=None, *args, **kwargs):
        """Creates a place 3d Texture node, and changes its transform

        Args:
            node (_type_): _description_
            transform (_type_, optional): _description_. Defaults to list().
            scale (_type_, optional): _description_. Defaults to list().
        """
        func = getattr(self.pm, "createNode")
        if self.cmds.objExists(kwargs.get("name")):
            return self.pm.PyNode(kwargs.get("name"))
        #     return self.pm.PyNode(kwargs.get("name"))
        node = self.exec_func(func, node, *args, **kwargs)
        if translate:
            node.translate.set(translate)
        if scale:
            node.scale.set(scale)
        return node

    def create_utility_node(
        self,
        node_type,
        node_name,
        connections=None,
        attributes=None,
        *args,
        **kwargs
    ):
        """Creates any type of utility node in the node editor"""
        if self.cmds.objExists(node_name):
            return self.pm.PyNode(node_name)
        func = getattr(self.pm, "shadingNode")
        _node = self.exec_func(
            func, node_type, name=node_name, *args, **kwargs
        )

        if connections:
            self._create_utility_connections(connections)

        if attributes:
            self._set_utility_values(node_name, attributes)
        return _node
    def _set_utility_values(self, node, attr_dict):
        for attr, value in attr_dict.items():
            try:
                self.cmds.setAttr("{0}.{1}".format(node, attr), value)
            except:
                self.pm.PyNode("{0}.{1}".format(node, attr)).set(value)
    def _create_utility_connections(self, connection_list, **kwargs):
        """Creates connections between node_editor's utility nodes"""
        for pair in connection_list:
            for orig_plug, dest_plug in pair.items():
                self.cmds.connectAttr(orig_plug, dest_plug)

    def create_joint(self, nodes, parent="", *args, **kwargs):
        """Creates a joint, hides the drawStyle, and parents to any node if requested

        Args:
            nodes (string): Joint name
            parent (str, optional): Joint parent's name. Defaults to "".

        Returns:
            pyNode: Joint Object reference
        """
        func = getattr(self.pm, "joint")
        if self.cmds.objExists(nodes):
            return self.pm.PyNode(nodes)
        joint = self.exec_func(func, name=nodes, *args, **kwargs)

        if parent:
            self.parent_nodes(joint, parent)
        self.set_attribute(joint, "drawStyle", 2)
        return joint

    def create_file_node(self, sticker_name, layer_name, texture_map, file_path,frame_extension):
        # Connect a place2dtexture node to the file node
        place2dTexture = self.create_utility_node(
            "place2dTexture", node_name = sticker_name + "_" + layer_name + "_" + texture_map +
            "_place2dTexture", asUtility=True,
            attributes={"wrapU": 0, "wrapV": 0}
        )
        file_node_name = "_".join([sticker_name, layer_name, texture_map])

        file_node = self.create_utility_node("file",
                                             node_name = file_node_name,
                                            asUtility=True,
                                             connections = [
                                                 {"{0}.outUV".format(place2dTexture):"{0}.uvCoord".format(file_node_name)},
                                                 {"{0}.outUvFilterSize".format(place2dTexture):"{0}.uvFilterSize".format(file_node_name)},
                                                 {"{0}.vertexCameraOne".format(place2dTexture):"{0}.vertexCameraOne".format(file_node_name)},
                                                 {"{0}.vertexUvOne".format(place2dTexture):"{0}.vertexUvOne".format(file_node_name)},
                                                 {"{0}.vertexUvThree".format(place2dTexture):"{0}.vertexUvThree".format(file_node_name)},
                                                 {"{0}.vertexUvTwo".format(place2dTexture):"{0}.vertexUvTwo".format(file_node_name)},
                                                 {"{0}.coverage".format(place2dTexture):"{0}.coverage".format(file_node_name)},
                                                 {"{0}.mirrorU".format(place2dTexture):"{0}.mirrorU".format(file_node_name)},
                                                 {"{0}.mirrorV".format(place2dTexture):"{0}.mirrorV".format(file_node_name)},
                                                 {"{0}.noiseUV".format(place2dTexture):"{0}.noiseUV".format(file_node_name)},
                                                 {"{0}.offset".format(place2dTexture):"{0}.offset".format(file_node_name)},
                                                 {"{0}.repeatUV".format(place2dTexture):"{0}.repeatUV".format(file_node_name)},
                                                 {"{0}.rotateFrame".format(place2dTexture):"{0}.rotateFrame".format(file_node_name)},
                                                 {"{0}.rotateUV".format(place2dTexture):"{0}.rotateUV".format(file_node_name)},
                                                 {"{0}.stagger".format(place2dTexture):"{0}.stagger".format(file_node_name)},
                                                 {"{0}.translateFrame".format(place2dTexture):"{0}.translateFrame".format(file_node_name)},
                                                 {"{0}.wrapU".format(place2dTexture):"{0}.wrapU".format(file_node_name)},
                                                 {"{0}.wrapV".format(place2dTexture):"{0}.wrapV".format(file_node_name)}
                                                 ],
                                             attributes={
                                                         'useFrameExtension':1,
                                                         })
        if os.path.isfile(file_path):
            file_node.setAttr('ftn', file_path)
        file_node.setAttr('frameExtension', int(frame_extension))

        return place2dTexture, file_node

    def create_projection_node(self, sticker_name, layer_name, texture_map, p3d, file_node):
        # Create a projection node
        projection_node_name = "_".join([sticker_name, layer_name, texture_map, "projection"])

        projection_node = self.create_utility_node("projection",
                                                   node_name = projection_node_name,
                                                   asUtility=True,
                                                   connections = [
                                                       {"{0}.outColor".format(file_node):"{0}.image".format(projection_node_name)}, {"{0}.worldInverseMatrix".format(p3d):"{0}.placementMatrix".format(projection_node_name)},
                                                       ],
                                                   attributes=
                                                   {
                                                       "wrap": 0,
                                                       'defaultColorR':0,
                                                       'defaultColorG':0,
                                                       'defaultColorB':0,
                                                       }

                                                   )
        return projection_node

    def create_aiMatte_material(self, sticker_name, layer_name, texture_map, projection):
        # Create an aiMatte material
        aiMatte_material_name = "_".join([sticker_name, layer_name, texture_map, "bake_shd"])
        aiMatte_material = self.create_utility_node("aiMatte",
                                                    asShader=True,
                                                    node_name = aiMatte_material_name,
                                                    connections = [
                                                        {"{0}.outColor".format(projection):"{0}.color".format(aiMatte_material_name)},
                                                        ]
                                                    )
        self.cmds.sets(name='{0}_SG'.format(aiMatte_material_name), empty=True, renderable=True,
                    noSurfaceShader=True)
        self.cmds.connectAttr('{0}.outColor'.format(aiMatte_material_name),
                            '{0}.surfaceShader'.format(aiMatte_material_name + "_SG"))
        return aiMatte_material

    def create_sticker_viewport_material(self, sticker_name, last_projection, mesh):
        '''
        Create a viewport material for the sticker
        '''
        sticker_vp_material_name = "_".join([sticker_name, "viewport_shd"])
        if self.cmds.objExists(sticker_vp_material_name):
            return self.pm.PyNode(sticker_vp_material_name)
        vp_material = self.create_utility_node("lambert",
                                               node_name = sticker_vp_material_name,
                                               asShader=True,
                                               connections = [
                                                   {"{0}.outColor".format(last_projection):"{0}.color".format(sticker_vp_material_name)},
                                                   ],
                                               )
        self.cmds.sets(name='{0}_SG'.format(sticker_vp_material_name), empty=True, renderable=True,
                    noSurfaceShader=True)

        self.cmds.connectAttr('{0}.outColor'.format(sticker_vp_material_name),
                            '{0}.surfaceShader'.format(sticker_vp_material_name + "_SG"))

        self.cmds.sets(mesh, e=True, forceElement=sticker_vp_material_name + "_SG")
        return vp_material
