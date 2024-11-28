#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Written by:
# Andrés Méndez del Río <andres.mendez@antaruxa.com>, 2023
# Cristina Fernandez Gomez <cristina.fernandez@antaruxa.com>, 2023

from . import parser
from . import sticker


class Builder:
    """Abstract Class. Creates, manipulates and organices complex sticker systems"""

    def __init__(self, root_path="", character_name="", sticker_definitions=None):
        """Initialices Builder's class atributes

        Init method for the abstract class Builder. This class is meant to be wrapped
        by another Builder Type class, to add functionality, structures and methods that
        increase the versatility of stickers.
        An example of a class that could inherit from this Builder's class could be
        a Facial System sticker manager, with functionality to create an entire facial system
        and all its dependencies.

        Example:
            definitions = [{
                      "name": "eye",
                      "flag": "L",
                      "index": 0,
                      "geometry": ["geo_camisa.vtx[226]"],
                      "layers": [{"layerName": "base"}],
                  }]
            builder = builder.Builder(sticker_definitions=definitions)

            # This creates the builder object, in order to create each sticker, we need to run this
            builder.create_stickers()

        Args:
            root_path (str, optional): Folder path containing the sticker's images. Defaults to "".
            character_name (str, optional):
            Character name which has the geometry associated to the sticker. Defaults to "".
            sticker_definitions (list[Dict], optional):
            List of dictionaries containing the necessary parameters to
            creathe each sticker . Defaults to None.

        """
        self.parser = parser.Parser()
        self.root_path = root_path
        self.character_name = character_name

        self.sticker_definitions = sticker_definitions if sticker_definitions else []
        self.stickers = {}

    def create_stickers(self):
        """Travels all stickers declared inside the class' sticker_definition
        and calls _create_sticker each time"""
        for definition in self.sticker_definitions:
            self._create_sticker(definition)

    def _create_sticker(self, definition):
        """Abstract function, creates a single sticker given its definition,
        Args:
            definition (dict): Sticker creation parameters.
        """
        sticker_obj = sticker.Sticker(**definition)
        sticker_obj.create()
        self.stickers.update(
            {
                definition.get('name'): sticker_obj.sticker_data
            }
        )

    def add_stickers(self, definition):
        """Auxiliary function. Lets the User create more stickers at any
        point after the builder is constructed

        Args:
            definition (dict/list): Sticker creation parameters, can be a list fo definitions
        """
        if isinstance(definition, list):
            for sticker_def in definition:
                self._create_sticker(sticker_def)
        self._create_sticker(definition)
