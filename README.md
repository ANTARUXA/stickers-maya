# Stickers

<!-- TOC -->

* [Introduction](#introduction)
* [Image types](#image-types)
* [Requirements](#requirements)
* [Install](#install)
* [Launch UI](#Launch-UI)
* [Basic usage](#basic-usage)
   + [Creating a sticker](#creating-a-sticker)
      - [Base sticker](#base-sticker)
      - [Image Sequence Sticker](#image-sequence-sticker)
      - [Multi-pose Sticker](#multi-pose-sticker)
   + [Animation](#animation)
* [Extra functionality](#extra-functionality)
   + [Specific image selection (Multi-pose sticker)](#specific-image-selection-multi-pose-sticker)
* [TODO](#todo)

<!-- END TOC-->

## Introduction

`Stickers` is a plugin that allows the artist to add custom decals to any
geometry without worrying about texturing through UVs.

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

> [!WARNING]
>`Stickers` can load any type of image, but some functionality
>(specially Alpha channels and tranparencies) have been only tested with `.png`
>files. If you try and use other filetypes, do it at your own risk, and report
>any bug that you may encounter.

## Requirements

* Autodesk Maya: 2022+

## Install

`Stickers` is released as a module for Maya

To install `Stickers`, go to the
[releases](https://github.com/ANTARUXA/stickers-maya/releases) page and
download the latest zip.

Extract its contents in one of the default directories that maya uses to load `modules` and everything is good to go

Some of the default paths are:

  * Windows:

        C:/Program Files/Autodesk/Maya<version>/modules
        C:/Users/<username>/Documents/maya/<version>/modules
        C:/Users/<username>/Documents/maya/modules
        C:/Program Files/Common Files/Autodesk Shared/Modules/maya/<version>


  * Linux:

        /usr/autodesk/maya<version>/modules
        $HOME/maya/<version>/modules
        $HOME/maya/modules
        /usr/autodesk/modules/maya/<version>
        /usr/autodesk/modules/maya

  * macOS:

        /Applications/Autodesk/maya<version>/Maya.app/Contents/module
        $HOME/Library/Preferences/Autodesk/maya/<version>/modules
        $HOME/Library/Preferences/Autodesk/maya/modules
        /Users/Shared/Autodesk/modules/maya/<version>
        /Users/Shared/Autodesk/modules/maya

> [!TIP]
> If you want to avoid any potential conflict pasting the `scripts` folder
> directly in one of the previous file, You can create a new folder and move
> `scripts` into it, then modify the `stickers.mod` file to reflect any change
> on the directory structure. Please double check that the paths are
> correct in the `.mod` file as a wrong relative path is the most frequent
> cause of error

## Launch UI

Use this code inside Maya to launch the plugin

```python

from stickers import ui

try:
    sticker_ui.close()
    sticker_ui.deleteLater()
except:
    pass

sticker_ui = ui.StickerUI()
sticker_ui.show()
```
You can add it to any shelf and use the icon provided with the plugin

## Basic usage

When launching the plugin, `Stickers` creates a window with all the fields required

### Creating a sticker

To create a `sticker`, open the `Stickers` ui. Introduce an unique name in the
first field, it should not be the same to any other sticker.

Then, we can choose which type of sticker we want to create.

#### Base sticker

1. Select the image path in the interface.

1. Select a vertex from the desired geometry and press the `<<`
   button on the ui. That sets the attachment point of the sticker That vertex
   will be the starting point for the sticker. The default poistion
   can be adjusted after created.

1. After setting everything, click on `Create sticker`.

#### Image Sequence Sticker

Check the `Image Sequence` checkbox and follow the same instructions as a
**base sticker**.

#### Multi-pose Sticker

Check the `Multi pose` checkbox and follow the same instructions as a
**base sticker**.

> [!IMPORTANT]
>The image sequence and multi-pose image files need to be
>numbered. Make sure they follow a pattern that Maya can detect
>as an image sequence

### Animation

The `mainControl` is in charge of all the channles that can be animated.

* Translation

  All 3 axis `X`, `Y`, `Z` are free to move and keyable

* Rotation

  Because the projection is perpendicular to the normal of the geometry, only
  the `Z` axis can be used to rotate the sticker. It's also keyable.

* Scaling

  Both `X` and `Y` axis can be scaled and keyed, scaling on the Z axis doesn't
  affect the sticker.

* Flip

  Two custom attributes, `Flip X` and `Flip Y`, are meant to mirror the
  `sticker` horizontally or vertically.

## Extra functionality

### Specific image selection (Multi-pose sticker)

When creating a **Multi pose** sticker, a custom attribute will be created to control which
image from the *image sequence* will be rendered and use it as a `pose`, without the image
sequence being linked by the current frame of the scene.

## TODO:

- [ ] Add support for more texture maps (Normal, Bump, Roughness...)
- [ ] Add `bake sticker to geometry` routine
    - [ ] Add render layers compatibility
- [ ] Add multi-layered stickers
