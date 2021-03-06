#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Copyright (C) Samsung Electronics, 2016
#
# 2016         Ilya Palachev                 <i.palachev@samsung.com>

import os
import sys
import logging
import check
import argparse

binfmt_directory = "/proc/sys/fs/binfmt_misc"


def __get_name(architecture):
    """
    Gets the name of binfmt file by the architecture.

    @param architecture The architecture.
    @return             The binafmt name.
    """
    binfmt_name = None
    if "arm64" in architecture or "aarch64" in architecture:
        binfmt_name = "arm64"
    elif "arm" in architecture:
        binfmt_name = "arm"
    else:
        raise Exception("Behavior for architecture {0} is not "
                        "implemented!".format(architecture))
    return binfmt_name


def __disable_all():
    """
    Disables or registered binary formats
    """
    binfmt_status_path = os.path.join(binfmt_directory, "status")
    check.file_exists(binfmt_status_path)
    with open(binfmt_status_path, 'w') as binfmt_status:
        binfmt_status.write("-1\n")

binfmt_magic = {}
binfmt_mask = {}
binfmt_flag = {}
binfmt_magic["arm"] = "".join(["\\x7fELF",
                               "\\x01", "\\x01", "\\x01", "\\x00",
                               "\\x00", "\\x00", "\\x00", "\\x00",
                               "\\x00", "\\x00", "\\x00", "\\x00",
                               "\\x02", "\\x00", "\\x28", "\\x00"])
binfmt_mask["arm"] = "".join(["\\xff", "\\xff", "\\xff", "\\xff",
                              "\\xff", "\\xff", "\\xff", "\\x00",
                              "\\xff", "\\xff", "\\xff", "\\xff",
                              "\\xff", "\\xff", "\\xff", "\\xff",
                              "\\xfe", "\\xff", "\\xff", "\\xff"])
binfmt_magic["arm64"] = "".join(["\\x7fELF",
                                 "\\x02", "\\x01", "\\x01", "\\x00",
                                 "\\x00", "\\x00", "\\x00", "\\x00",
                                 "\\x00", "\\x00", "\\x00", "\\x00",
                                 "\\x02", "\\x00", "\\xb7"])
binfmt_mask["arm64"] = "".join(["\\xff", "\\xff", "\\xff", "\\xff",
                                "\\xff", "\\xff", "\\xff", "\\x00",
                                "\\xff", "\\xff", "\\xff", "\\xff",
                                "\\xff", "\\xff", "\\xff", "\\xff",
                                "\\xfe", "\\xff", "\\xff"])
binfmt_flag["qemu"] = "OC"
binfmt_flag["qemu-wrapper"] = "P"


def __register(architecture, qemu_executable_path):
    """
    Register the binary format for the given architecture.

    @param architecture         The architecture.
    @param qemu_executable_path The absolute path to qemu binary INSIDE the
                                chroot directory (after chrooting to it). It
                                must always begin with '/'.
    """
    qemu_type = "qemu"
    if os.path.basename(qemu_executable_path).endswith("-binfmt"):
        qemu_type = "qemu-wrapper"
    binfmt_register_path = os.path.join(binfmt_directory, "register")
    check.file_exists(binfmt_register_path)

    binfmt_name = __get_name(architecture)
    binary_format = ":{0}:M::{1}:{2}:{3}:{4}".format(binfmt_name,
                                                     binfmt_magic[binfmt_name],
                                                     binfmt_mask[binfmt_name],
                                                     qemu_executable_path,
                                                     binfmt_flag[qemu_type])
    with open(binfmt_register_path, 'w') as binfmt_register:
        binfmt_register.write(binary_format)


def __parse_args():
    """ customize arguments """
    parser = argparse.ArgumentParser(description='Register qemu in binfmt_misc.')
    parser.add_argument('--arch', '-a', default='armv7l', help='target architecture')
    parser.add_argument('--qemu', '-q', default='/usr/bin/qemu-arm', help='path to qemu executable')

    return parser.parse_args()


def main(argv):
    args = __parse_args()
    __disable_all()
    __register(args.arch, args.qemu)


if __name__ == "__main__":
    exit(main(sys.argv))
