"""
The MIT License (MIT)

Copyright (c) 2013 Niko Skrypnik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

"""
Object3D class
=============

"""

from kivy.properties import NumericProperty, ListProperty, ObjectProperty, AliasProperty
from kivy.graphics import Scale, Rotate, PushMatrix, PopMatrix, Translate, Mesh
from kivy.graphics.instructions import InstructionGroup
from kivy.event import EventDispatcher

from kivy3.math.vectors import Vector3


class Object3D(EventDispatcher):
    """Base class for all 3D objects in rendered
    3D world.
    """

    scale = ObjectProperty(Vector3(0, 0, 0))

    def __init__(self, **kw):

        super(Object3D, self).__init__(**kw)
        self.name = kw.pop('name', '')
        self.children = list()
        self.parent = None

        self._position = Vector3(0, 0, 0)
        self._rotation = Vector3(0, 0, 0)
        self._position.set_change_cb(self.on_pos_changed)
        self._rotation.set_change_cb(self.on_angle_change)

        # general instructions
        self._pop_matrix = PopMatrix()
        self._push_matrix = PushMatrix()
        self._translate = Translate(*self.pos)
        self._scale = Scale(self.scale)
        self._rotors = {
                        "x": Rotate(self._rotate[0], 1, 0, 0),
                        "y": Rotate(self._rotate[1], 0, 1, 0),
                        "y": Rotate(self._rotate[2], 0, 0, 1)
                        }

        self._instructions = InstructionGroup()

    def add(self, obj):
        self.children.append(obj)
        obj.parent = self

    def _set_position(self, val):
        if isinstance(val, Vector3):
            self._position = val
        else:
            self._position = Vector3(val)
        self._position.set_change_cb(self.on_pos_changed)

    def _get_position(self):
        return self._position

    position = AliasProperty(_get_position, _set_position)
    pos = position  # just shortcut

    def _set_rotation(self, val):
        if isinstance(val, Vector3):
            self._rotation = val
        else:
            self._rotation = Vector3(val)
        self._rotation.set_change_cb(self.on_angle_change)
        self._rotor["x"].angle = self._rotation.x
        self._rotor["y"].angle = self._rotation.y
        self._rotor["z"].angle = self._rotation.z

    def _get_rotation(self):
        return self._rotation

    rotation = AliasProperty(_get_rotation, _set_rotation)

    def on_pos_changed(self, coord, v):
        " Some coordinate was changed "

    def on_angle_change(self, axis, angle):
        self._rotor[axis].angle = angle

    def on_scale(self, val):
        self._scale.xyz = (val, val, val)

    def as_instructions(self):
        """ Get instructions set for renderer """
        if not self._instructions.children:
            self._instructions.add(self._push_matrix)
            self._instructions.add(self._translate)
            self._instructions.add(self.scale)
            for rot in self._rotors.itervalues():
                self._instructions.add(rot)
            for instr in self.custom_instructions():
                self._instructions.add(instr)
            for child in self.get_children_instructions():
                self._instructions.add(child)
            self._instructions.add(self._push_matrix)
        return self._instructions

    def custom_instructions(self):
        """ Should be overriden in subclasses to provide some extra
            instructions
        """
        return []

    def get_children_instructions(self):
        for child in self.children:
            yield child.as_instructions()
