"""
novelWriter – Types and Flags
=============================

File History:
Created: 2024-04-01 [2.4rc1]

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

from PyQt5.QtCore import Qt

# Qt Alignment Flags

QtAlignAbsolute = Qt.AlignmentFlag.AlignAbsolute
QtAlignCenter = Qt.AlignmentFlag.AlignCenter
QtAlignCenterTop = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
QtAlignJustify = Qt.AlignmentFlag.AlignJustify
QtAlignLeft = Qt.AlignmentFlag.AlignLeft
QtAlignLeftBase = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBaseline
QtAlignLeftMiddle = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
QtAlignLeftTop = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
QtAlignMiddle = Qt.AlignmentFlag.AlignVCenter
QtAlignRight = Qt.AlignmentFlag.AlignRight
QtAlignRightBase = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBaseline
QtAlignRightMiddle = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
QtAlignRightTop = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
QtAlignTop = Qt.AlignmentFlag.AlignTop
