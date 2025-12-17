#!/usr/bin/env python
"""
A GUI for the minceraft launcher

Minceraft-launcher is a fast launcher for minecraft
Copyright (C) 2025  Cdr_Johannsen, Muslimitmilch

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# pylint: disable=wrong-import-position
import os
import threading
from importlib import metadata
from time import sleep

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
import minecraft_launcher_lib
from gi.repository import Adw, Gdk, Gio, GLib, Gtk
from minecraft_launcher_lib.types import CallbackDict

minceraft_gtk_path = os.path.abspath(os.path.dirname(__file__))
from minceraft import minceraft

# pylint: enable=wrong-import-position


class Minceraft(Adw.Application):  # pylint: disable=too-many-public-methods, too-many-instance-attributes
    """Handles the entire GUI for minceraft"""

    def __init__(self, **kwargs):  # pylint: disable=too-many-statements
        super().__init__(**kwargs)
        self.oh = minceraft.OptionHandler()
        self.skin: Gio.File
        self.width = "classic"
        minceraft.handleArgs(self.oh)
        self.connect("activate", self.on_activate)
        self.builder = Gtk.Builder()
        self.builder.add_from_file(minceraft_gtk_path + "/minceraft_gtk.ui")
        self.win = self.builder.get_object("win")
        self.add_account_dialog = self.builder.get_object("add-account-dialog")
        self.add_account_stack = self.builder.get_object("add-account-stack")
        self.add_account_select = self.builder.get_object("add-account-select")
        self.minceraft_confirm = self.builder.get_object("minceraft-confirm")
        self.minceraft_error_label = self.builder.get_object("minceraft-error-label")
        self.minceraft_password2 = self.builder.get_object("minceraft-password2")
        self.minceraft_password = self.builder.get_object("minceraft-password")
        self.minceraft_name = self.builder.get_object("minceraft-name")
        self.delete_alert = self.builder.get_object("delete-alert")
        self.about_dialog = self.builder.get_object("about-dialog")
        self.install_page = self.builder.get_object("install-page")
        self.fabric_check = self.builder.get_object("fabric-check")
        self.vanilla_check = self.builder.get_object("vanilla-check")
        self.forge_check = self.builder.get_object("forge-check")
        self.modloader = self.builder.get_object("modloader")
        self.show_snapshots_check = self.builder.get_object("show-snapshots-check")
        self.install_version_dropdown = self.builder.get_object("install-version-dropdown")
        self.install_version_list = self.builder.get_object("install-version-list")
        self.install_alias = self.builder.get_object("install-alias")
        self.install_button = self.builder.get_object("install-button")
        self.install_progress = self.builder.get_object("install-progress")
        self.preferences_dialog = self.builder.get_object("preferences-dialog")
        self.preferences_apply_button = self.builder.get_object("preferences-apply-button")
        self.min_ram = self.builder.get_object("min-ram")
        self.min_ram_adj = self.builder.get_object("min-ram-adj")
        self.max_ram = self.builder.get_object("max-ram")
        self.max_ram_adj = self.builder.get_object("max-ram-adj")
        self.startup_port = self.builder.get_object("startup-port")
        self.startup_server = self.builder.get_object("startup-server")
        self.reauth_button = self.builder.get_object("reauth-button")
        self.account_menu_button = self.builder.get_object("account-menu-button")
        self.account_popover = self.builder.get_object("account-popover")
        self.account_list = self.builder.get_object("account-list")
        self.add_account_button = self.builder.get_object("add-account-button")
        self.hamburger_popover = self.builder.get_object("hamburger-popover")
        self.main_stack = self.builder.get_object("main-stack")
        self.login_page = self.builder.get_object("login-page")
        self.login_dialog_label = self.builder.get_object("login-dialog-label")
        self.login_dialog_entry = self.builder.get_object("login-dialog-entry")
        self.login_wrong_password = self.builder.get_object("login-wrong-password")
        self.main_page = self.builder.get_object("main-page")
        self.skin_apply_button = self.builder.get_object("skin-apply-button")
        self.skin_slim_check = self.builder.get_object("skin-slim-check")
        self.skin_select_button = self.builder.get_object("skin-select-button")
        self.skin_select_label = self.builder.get_object("skin-select-label")
        self.version_dropdown = self.builder.get_object("version-dropdown")
        self.version_list = self.builder.get_object("version-list")
        self.preferences_button = self.builder.get_object("preferences-button")
        self.delete_button = self.builder.get_object("delete-button")
        self.install_new_button = self.builder.get_object("install-new-button")
        self.launch_button = self.builder.get_object("launch-button")

        self.hamburger_menu = Gio.Menu.new()  # pylint: disable=no-value-for-parameter
        self.about_action = Gio.SimpleAction.new("about", None)
        self.add_action(self.about_action)

        self.account_menu = Gio.Menu.new()  # pylint: disable=no-value-for-parameter

        self.connectAll()
        self.hamburger_menu.append("About", "app.about")
        self.hamburger_popover.set_menu_model(self.hamburger_menu)
        self.account_popover.set_menu_model(self.account_menu)
        self.reauth_button.set_sensitive(False)

        f_filter = Gtk.FileFilter()
        f_filter.add_mime_type("image/png")
        f_filters = Gio.ListStore.new(Gtk.FileFilter)
        f_filters.append(f_filter)
        self.file_dialog = Gtk.FileDialog.new()  # pylint: disable=no-value-for-parameter
        self.file_dialog.set_title("Select a skin")
        self.file_dialog.set_accept_label("Select")
        self.file_dialog.set_filters(f_filters)
        self.file_dialog.set_default_filter(f_filter)

        self.oh.setDebugCallback(self.debug)
        if not self.oh.load():
            self.showAddAccountDialog(None)

        self.updateUsers()
        self.updateVersions()
        self.account_menu_button.set_label(self.oh.username)
        self.skin_apply_button.set_sensitive(False)

        if self.oh.user_info["last_played"] != -1:
            self.version_dropdown.set_selected(self.oh.user_info["last_played"])

        if self.oh.password and self.oh.user_info["passwordHash"] == minceraft.encryption.hashValue(self.oh.password):
            self.oh.config[0]["last_user"] = self.oh.user
            self.oh.load()
            self.oh.saveConfig()
            self.handleVersionButtons()
            self.manageMainStack(None, 1)
            self.win.set_focus(self.launch_button)
            self.reauth_button.set_sensitive(True)
        else:
            self.manageMainStack(None, 0)

        self.current_max = 0
        self.modloader = "0"

    def debug(self, message):
        """Debug callback"""
        if self.oh.debug_mode:
            print(f"[DEBUG] {message}")

    def on_activate(self, application):  # pylint: disable=invalid-name
        """Gets called when the app activates"""
        del application
        self.delete_alert.set_modal(self.win)
        self.win.set_application(self)
        self.win.present()

    def connectAll(self):
        """
        Connects all Signals to their required functions
        """

        self.minceraft_confirm.connect("clicked", self.addMinceraft)
        self.about_action.connect("activate", self.showAbout)
        self.delete_button.connect("clicked", self.showDelete)
        self.preferences_button.connect("clicked", self.showPreferences)
        self.install_new_button.connect("clicked", self.showInstall)
        self.launch_button.connect("clicked", self.launch)
        self.reauth_button.connect("clicked", self.handleReauth)
        self.add_account_button.connect("clicked", self.showAddAccountDialog)
        self.delete_alert.connect("response", self.handleDelete)
        self.login_dialog_entry.connect("apply", self.login)
        self.min_ram.connect("value-changed", self.handleMinRam)
        self.max_ram.connect("value-changed", self.handleMaxRam)
        self.preferences_apply_button.connect("clicked", self.applyPreferences)
        self.install_button.connect("clicked", self.installVersion)
        self.vanilla_check.connect("toggled", self.updateModloader)
        self.fabric_check.connect("toggled", self.updateModloader)
        self.forge_check.connect("toggled", self.updateModloader)
        self.show_snapshots_check.connect("toggled", self.updateInstallVersions)
        self.skin_select_button.connect("clicked", self.selectSkin)
        self.skin_apply_button.connect("clicked", self.applySkin)

    def applySkin(self, *_):
        """Creates a thread to apply the new skin"""
        self.width = "slim" if self.skin_slim_check.get_active() else "classic"
        self.skin_apply_button.set_sensitive(False)
        self.skin_slim_check.set_sensitive(False)
        self.skin_select_button.set_sensitive(False)
        self.win.set_cursor(Gdk.Cursor.new_from_name("wait"))
        p_thread = threading.Thread(target=self.changeSkin)
        p_thread.daemon = True
        p_thread.start()

    def changeSkin(self):
        """Applys the new skin"""
        minceraft.changeSkin(self.oh, self.skin.get_parse_name(), self.width)
        GLib.idle_add(self.skin_apply_button.set_sensitive, True)
        GLib.idle_add(self.skin_slim_check.set_sensitive, True)
        GLib.idle_add(self.skin_select_button.set_sensitive, True)
        GLib.idle_add(self.win.set_cursor, None)

    def selectSkin(self, *_):
        """Opens the select skin filechooser"""
        self.file_dialog.open(self.win, None, self.fileChooserCallback)

    def fileChooserCallback(self, action, result):
        """Sets the skin to the one selected in the filechooser"""
        del action
        try:
            self.skin = self.file_dialog.open_finish(result)
            self.skin_select_label.set_text(self.skin.get_basename().strip(".png"))
            self.skin_apply_button.set_sensitive(True)
        except GLib.Error:
            pass

    def updateAccounts(self):
        """Updates the avaliable accounts"""
        self.account_menu.remove_all()
        for i in range(1, len(self.oh.users) + 1):
            action = Gio.SimpleAction.new(str(i), None)
            self.add_action(action)
            action.connect("activate", self.changeAccount, i)
            self.account_menu.append(self.oh.users[i - 1]["username"], f"app.{i}")

    def changeAccount(self, action, param, account):
        """Switches to another account"""
        del action, param
        self.oh.user = account
        self.oh.load()
        self.updateVersions()
        self.account_menu_button.set_label(self.oh.username)
        self.login_dialog_entry.delete_text(0, -1)
        self.manageMainStack(None, 0)
        self.reauth_button.set_sensitive(False)

    def updateModloader(self, action):
        """Update the selected modloader"""
        if action.get_active():
            self.updateInstallVersions(None)

    def updateInstallVersions(self, *_):
        """Update the avaliable versions list"""
        self.install_version_list.splice(0, len(self.install_version_list))
        if (
            self.vanilla_check.get_active() or self.forge_check.get_active()
        ):  # forge doesnt have a list of supportet versions
            versions = minecraft_launcher_lib.utils.get_version_list()
            for version in versions:
                if version["type"] != "snapshot" or self.show_snapshots_check.get_active():
                    self.install_version_list.append(version["id"])
        elif self.fabric_check.get_active():
            if self.show_snapshots_check.get_active():
                for version in minecraft_launcher_lib.fabric.get_all_minecraft_versions():
                    self.install_version_list.append(version["version"])
            else:
                self.install_version_list.splice(0, 0, minecraft_launcher_lib.fabric.get_stable_minecraft_versions())

    def installVersion(self, *_):
        """Creates a new version installation thread"""
        if self.vanilla_check.get_active():
            self.modloader = "0"
        elif self.fabric_check.get_active():
            self.modloader = "1"
        elif self.forge_check.get_active():
            self.modloader = "2"
        else:
            self.modloader = "3"
        self.install_progress.set_visible(True)
        self.install_button.set_sensitive(False)
        p_thread = threading.Thread(target=self.install)
        p_thread.daemon = True
        p_thread.start()
        # self.updateVersions()

    def install(self):
        """Triggers a new version installation"""
        callback: CallbackDict = {
            "setStatus": self.setStatus,
            "setProgress": self.setProgress,
            "setMax": self.setMax,
        }
        minceraft.install(
            self.oh,
            self.install_version_list.get_string(self.install_version_dropdown.get_selected()),
            self.modloader,
            self.install_alias.get_text(),
            callback,
        )
        sleep(2)
        self.oh.updateVersions()
        GLib.idle_add(self.updateVersions)
        self.oh.saveConfig()
        GLib.idle_add(self.win.set_focus, self.launch_button)
        GLib.idle_add(self.version_dropdown.set_selected, len(self.version_list) - 1)
        GLib.idle_add(self.manageMainStack, None, 1)

    def updateProgress(self):
        """Update the installation progress bar"""
        self.install_progress.set_fraction(self.install_progress.get_fraction())

    def setStatus(self, status: str):
        """Set installation status"""
        GLib.idle_add(self.install_progress.set_text, status)

    def setProgress(self, progress: int):
        """Set installation progress"""
        GLib.idle_add(
            self.install_progress.set_fraction,
            float(progress) / float(self.current_max),
        )

    def setMax(self, new_max: int):
        """Set installation max progress"""
        self.current_max = new_max

    def updateVersions(self):
        """Update installed versions"""
        self.version_list.splice(0, len(self.version_list))
        for i in self.oh.versions:
            self.version_list.append(i["alias"])

    def updateUsers(self):
        """Update users"""
        self.updateAccounts()
        # self.account_list.splice(0,len(self.account_list))
        # for i in self.oh.config[1:]:
        # self.account_list.append(i.get("username"))

    def newUser(self, *_):
        """Adds a new user"""
        self.add_account_dialog.set_sensitive(False)
        self.oh.password = self.minceraft_password.get_text()
        auth_successfull = False
        while not auth_successfull:
            auth_successfull = minceraft.newUser(
                self.oh, self.minceraft_name.get_text(), self.minceraft_password.get_text()
            )
            if not auth_successfull:
                self.minceraft_error_label.set_text("Authentification failed! Try again.")
        self.updateUsers()
        self.add_account_dialog.set_visible(False)
        self.add_account_dialog.set_sensitive(True)
        self.handleVersionButtons()

    def addMinceraft(self, *_):
        """Gets credentials for a new account"""
        if not self.minceraft_name.get_text():
            self.minceraft_error_label.set_text("Username missing")
        elif not self.minceraft_password.get_text() or not self.minceraft_password2.get_text():
            self.minceraft_error_label.set_text("Password missing")
        elif self.minceraft_password.get_text() != self.minceraft_password2.get_text():
            self.minceraft_error_label.set_text("Passwords are not the same")
        else:
            self.newUser()

    def applyPreferences(self, *_):
        """Apply and save selected preferences"""
        self.oh.versions[self.version_dropdown.get_selected()]["memory"][0] = str(int(self.max_ram.get_value()))
        self.oh.versions[self.version_dropdown.get_selected()]["memory"][1] = str(int(self.min_ram.get_value()))
        self.oh.versions[self.version_dropdown.get_selected()]["server"] = self.startup_server.get_text()
        self.oh.versions[self.version_dropdown.get_selected()]["port"] = str(int(self.startup_port.get_value()))
        self.oh.saveConfig()
        self.preferences_dialog.set_visible(False)

    def handleMinRam(self, *_):
        """Handles the lower limit for the maximum ram"""
        self.max_ram_adj.set_lower(self.min_ram.get_value())

    def handleMaxRam(self, *_):
        """Handles the upper limit for the minimum ram"""
        self.min_ram_adj.set_upper(self.max_ram.get_value())

    def login(self, *_):
        """Handles the login process"""
        self.oh.password = self.login_dialog_entry.get_text()
        if self.oh.user_info["passwordHash"] == minceraft.encryption.hashValue(self.oh.password):
            self.login_wrong_password.set_visible(False)
            self.oh.config[0]["last_user"] = self.oh.user
            self.oh.load()
            self.oh.saveConfig()
            self.handleVersionButtons()
            self.manageMainStack(None, 1)
            self.reauth_button.set_sensitive(True)
            self.win.set_focus(self.launch_button)
            self.login_dialog_entry.delete_text(0, -1)
        else:
            self.login_wrong_password.set_visible(True)

    def handleVersionButtons(self):
        """Sets version related buttons to incative if no version exists"""
        if self.oh.versions == []:
            self.delete_button.set_sensitive(False)
            self.preferences_button.set_sensitive(False)
            self.version_dropdown.set_sensitive(False)
            self.launch_button.set_sensitive(False)
        else:
            self.delete_button.set_sensitive(True)
            self.preferences_button.set_sensitive(True)
            self.version_dropdown.set_sensitive(True)
            self.launch_button.set_sensitive(True)

    def showAddAccountDialog(self, *_):
        """Clears and shows the add account dialog"""
        self.manageAddAccountStack(None, 0)
        self.minceraft_name.delete_text(0, -1)
        self.minceraft_password.delete_text(0, -1)
        self.minceraft_password2.delete_text(0, -1)
        self.add_account_dialog.set_visible(True)

    def manageAddAccountStack(self, action, page):
        """Manages the add account dialog"""
        del action
        pages = ["add-account-minceraft"]
        self.add_account_stack.set_visible_child_name(pages[page])

    def manageMainStack(self, action, page):
        """Sets the main windows stack to the wanted page"""
        del action
        pages = ["login-page", "main-page", "install-page"]
        self.main_stack.set_visible_child_name(pages[page])

    def showAbout(self, *_):
        """Shows the about dialog"""
        self.about_dialog.set_version(metadata.version("minceraft"))
        self.about_dialog.set_visible(True)

    def showDelete(self, *_):
        """Shows the version deletion dialog"""
        self.delete_alert.set_property(
            "secondary-text",
            f"Do you really want to delete {self.oh.versions[self.version_dropdown.get_selected()]['alias']}?",
        )
        cancel_button = self.delete_alert.get_child().get_last_child().get_first_child().get_first_child()
        self.delete_alert.get_child().get_last_child().get_first_child().set_focus_child(cancel_button)
        cancel_button.set_css_classes(["text-button", "error", "default"])
        self.delete_alert.set_visible(True)

    def showInstall(self, *_):
        """Shows the installation dialog"""
        self.updateInstallVersions(None)
        self.install_progress.set_visible(False)
        self.install_alias.delete_text(0, -1)
        self.vanilla_check.set_active(True)
        self.install_button.set_sensitive(True)
        self.manageMainStack(None, 2)

    def showPreferences(self, *_):
        """Updates and shows the preferences dialog"""
        self.preferences_dialog.set_title(self.oh.versions[self.version_dropdown.get_selected()]["alias"])
        self.max_ram_adj.set_value(int(self.oh.versions[self.version_dropdown.get_selected()]["memory"][0]))
        self.min_ram_adj.set_value(int(self.oh.versions[self.version_dropdown.get_selected()]["memory"][1]))
        self.startup_server.set_text(self.oh.versions[self.version_dropdown.get_selected()]["server"])
        port = self.oh.versions[self.version_dropdown.get_selected()]["port"]
        if port != "":
            self.startup_port.set_value(int(port))
        self.preferences_dialog.set_visible(True)

    def launch(self, *_):
        """Launches minecraft"""
        minceraft.launch(self.oh, self.version_dropdown.get_selected())
        sleep(3)
        self.quit()

    def handleReauth(self, *_):
        """Creates a reauth thread"""
        self.reauth_button.set_sensitive(False)
        self.win.set_cursor(Gdk.Cursor.new_from_name("wait"))
        n_thread = threading.Thread(target=self.reauth)
        n_thread.daemon = True
        n_thread.start()

    def reauth(self):
        """Triggers a reauth"""
        minceraft.auth(self.oh)
        GLib.idle_add(self.reauth_button.set_sensitive, True)
        GLib.idle_add(self.win.set_cursor, None)

    def handleDelete(self, action, param):
        """Handles the deletion of a minecraft version"""
        del action
        if param == -8:
            minceraft.deleteVersion(self.oh, self.version_dropdown.get_selected())
            self.updateVersions()
            self.handleVersionButtons()
        self.delete_alert.set_visible(False)


def main():
    """Run the minceraft gui launcher"""
    app = Minceraft(application_id="com.github.CdrJohannsen.minceraft")
    app.run()


if __name__ == "__main__":
    main()
