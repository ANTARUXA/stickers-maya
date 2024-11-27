# Stickers

## Introduction

`Stickers` is a plugin that allows the artist to add custom decals to any
geometry without worrying about UVs.

Using a custom projection system, the artist is able to move, scale and rotate
any image, making `Stickers` a very flexible system that can be used to create
numerous variants of a character without having to redo its textures every
time. All the `Stickers` properties can be animated, providing the artist with
almost no limitations of what they can do with it. Multiple `stickers` can be
placed in one geometry.

`Stickers` makes combining these 2D and 3D animation techniques a lot easier.

## Image types

`Stickers` can both load **still images** and **image sequences**. Artist can
then choose between rendering the `sticker` frame by frame, or select
individual frames. This is useful for cases where each image in the sequence is
a different pose or variant of the same element.

>[!WARNING]
>`Stickers` can load any type of image, but some functionality (specially
>Alpha channels and tranparencies) have been only tested with `.png` files. If
>you try and use other filetypes, do it at your own risk, and report any bug
>that you may encounter.

## Requirements

* Blender: 4.2

## Install

## Basic usage

When launching the plugin, `Stickers` creates a tab in the 3dview to create or
remove stickers.

### Creating a sticker

To create a `sticker`, open the `Stickers` menu tab in the 3d view (or press `n`).
Introduce an unique name in the first field, it should not be the same to any other sticker.

Then, we can choose which type of sticker we want to create

#### Base sticker

1. Select the image path in the interface.

1. Select the desired geometry, change to `EDIT MODE` and select one vertex.
   That vertex will be the starting point for the sticker. It can be adjusted once created.

1. After setting everything, click on `Create sticker`

#### Image Sequecne Sticker

Check the `Image Sequence` checkbox and follow the same instructions as a **base sticker**

#### Multi-pose Sticker

Check the `Controled anim` checkbox and follow the same instructions as a **base sticker**

>[!IMPORTANT]
>The image sequence and multi-pose image files need to be numbered. Make sure they follow a pattern
>that Blender can recogniced

Once created, you can animate (translate, rotate, scale), flip and change the
opacity of the sticker through the main object's properties.

The `sticker` object is located under the selected geometry. There is a root
node called `{sticker_name}_anchor_node` that 'anchors' the sticker to the
geometry, and `{sticker_name}_base_node` which is the main controller node,
holds the principal attributes and can be animated.

<!-- Show properties in ui through images -->

Inside the `shader editor`, the artist can use a panel to rearrange the
rendering order of all created stickers (similar to 'move to front/back'
controls)

<!-- Outliner images -->

## Advanced use cases
