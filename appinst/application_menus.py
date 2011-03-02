# Copyright (c) 2008-2011 by Enthought, Inc.
# All rights reserved.

import sys
import platform

# The custom_tools package is importable when the Python was created by an
# "enicab" installer, in which case the directory custom_tools contains
# platform-independent install information in __init__.py and platform-specific
# information about user setting chosen during the install process.
try:
    import custom_tools
except ImportError:
    custom_tools = None


def get_default_menu():
    if custom_tools:
        return [
            { # Sub-menu correspond to product name and version.
                'id': custom_tools.FULL_NAME,
                'name': custom_tools.FULL_NAME,
                }]
    else:
        name = 'Python-%i.%i' % sys.version_info[:2]
        return [{
                'id': name,
                'name': name,
                }]


def install(menus, shortcuts, install_mode='user', uninstall=False):
    """
    Install an application menu according to the specified mode.

    This call is meant to work on all platforms.  If done on Linux, the menu
    will be installed to both Gnome and KDE desktops if they are available.

    Note that the information required is sufficient to install application
    menus on systems that follow the format of the Desktop Entry Specification
    by freedesktop.org.  See:
            http://freedesktop.org/Standards/desktop-entry-spec

    menus: A list of menu descriptions that will be added/merged into the OS's
        application menu.   A menu description is a dictionary containing the
        following keys and meanings:
            category: An optional identifier used to locate shortcuts within a
                menu.  Note that the string you specify here is not necessarily
                the full category you'll need to use in your shortcut as this
                package ensures uniqueness of category values by concatenating
                them as it goes down the menu hierarchy, using a '.' as the
                separator char.  For example, if a menu with category 'Abc'
                contains a sub-menu who's category is 'Def', then the full
                category for the sub-menu will be 'Abc.Def'.
            id: A string that can be used to represent the resources needed to
                represent the menu.  i.e. on Linux, the id is used for the name
                of the '.directory' file.  If no category is explicitly
                specified, the id is used as the category specification.
            name: The display name of the menu.
            sub-menus: A list of menu descriptions that make up sub-menus of
                this menu.

    shortcuts: A list of shortcut specifications to be created within the
        previously specified menus.   A shortcut specification is a dictionary
        consisting of the following keys and values:
            categories: A list of the menu categories this shortcut should
                appear in.  We only support your own menus at this time due to
                cross-platform difficulties with identifying "standard"
                locations.
            cmd: A list of strings where the first item in the list is the
                executable command and the other items are arguments to be
                passed to that command.   Each argument should be a separate
                item in the list.   Note that you can use the special text
                markers listed here as the first command string to represent
                standard commands that are platform dependent:

                '{{FILEBROWSER}}' specifies that the following arguments are
                    paths to be opened in the OS's file system explorer.
                '{{WEBBROWSER}}' specifies that the following arguments are
                    paths to be opened in the OS's standard, or user's default,
                    web browser.

            comment: A description for the shortcut, typically becomes fly-over
                help.
            icon: An optional path to an .ico file to use as the icon for this
                shortcut.
            id: A string that can be used to represent the resources needed to
                represent the shortcut.  i.e. on Linux, the id is used for the
                name of the '.desktop' file.  If no id is provided, the name
                is used as the id.
            name: The display name for this shortcut.
            terminal: A boolean value representing whether the shortcut should
                run within a shell / terminal.

    install_mode: should be either 'user' or 'system' and controls where the
        menus and shortcuts are installed on the system, depending on platform.

    TODO: Create separate APIs for product-specific shortcuts vs. generic
    shortcuts
    """
    # If we can, determine the install mode the user chose during the install
    # process.
    if custom_tools and sys.platform == 'win32':
        from custom_tools.msi_property import get
        if get('ALLUSERS') == '1':
            install_mode = 'system'

    # Validate we have a valid install mode.
    assert install_mode in ('user', 'system')

    # FIXME: Uninstall only support for Windows at this point.
    if uninstall and sys.platform != 'win32':
        sys.exit("Uninstall is currently only supported for Windows, "
                 "not for platform: %s" % sys.platform)

    if not menus:
        menus = get_default_menu()
        for sc in shortcuts:
            sc['categories'] = [custom_tools.FULL_NAME]
    """
    import pprint
    pp = pprint.PrettyPrinter(indent=4, width=20)
    print 'MENUS: %s' % pp.pformat(menus)
    print 'SHORTCUTS: %s' % pp.pformat(shortcuts)
    print 'INSTALL_MODE: %s' % install_mode
    """
    if sys.platform == 'linux2':
        dist = platform.dist()
        if dist[0] == 'redhat':
            rh_ver = dist[1]
            if rh_ver.startswith('3'):  # Dispatch for RedHat 3.
                from appinst.rh3 import RH3
                RH3().install_application_menus(menus, shortcuts, install_mode)
                return
            elif rh_ver.startswith('4'):  # Dispatch for RedHat 4.
                from appinst.rh4 import RH4
                RH4().install_application_menus(menus, shortcuts, install_mode)
                return
        from appinst.linux2 import Linux
        Linux().install_application_menus(menus, shortcuts, install_mode)
        return
    elif sys.platform == 'darwin':
        from appinst.osx import OSX
        OSX().install_application_menus(menus, shortcuts, install_mode)
        return
    elif sys.platform == 'win32':
        from appinst.win32 import Win32
        Win32().install_application_menus(menus, shortcuts, install_mode,
                                          uninstall=uninstall)
        return
    sys.exit('Unhandled platform. Unable to create application menu(s).')


def uninstall(menus, shortcuts, install_mode='user'):
    """
    Uninstall application menus.

    FIXME: This currently only works for Windows which can determine the install
    mode from the registry entry. There should be a method for linux as well
    which determines the installation type possibly from the install directory,
    a stored value, or user input.
    """
    install(menus, shortcuts, install_mode, uninstall=True)
