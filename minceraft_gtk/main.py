#!/usr/bin/env python
import gi

gi.require_version("Gtk", "4.0")
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import sys
sys.path.append('../src')
import minceraft

class Minceraft(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.builder = Gtk.Builder()
        self.builder.add_from_file("minceraft_gtk.ui")
        self.version_dropdown = self.builder.get_object("version-dropdown")
        self.delete_dialog = self.builder.get_object("delete-alert")
        self.delete_dialog.connect("response",self.handle_delete)

        self.versions=["1.8.9","fabric 1.20.1"]

    def on_activate(self, app):
        about_button = self.builder.get_object("about-button")
        about_button.connect("clicked", self.show_about)
        delete_button = self.builder.get_object("delete-button")
        delete_button.connect("clicked", self.show_delete)
        preferences_button = self.builder.get_object("preferences-button")
        preferences_button.connect("clicked", self.show_preferences)
        install_dialog_button = self.builder.get_object("install-dialog-button")
        install_dialog_button.connect("clicked", self.show_install)
        launch_button = self.builder.get_object("launch-button")
        launch_button.connect("clicked", self.launch)
        reauth_button = self.builder.get_object("reauth-button")
        reauth_button.connect("clicked", self.reauth)
        version_list = self.builder.get_object("version-list")
        for i in self.versions: version_list.append(i)

        self.win = self.builder.get_object("win")
        self.delete_dialog.set_modal(self.win)
        self.win.set_application(self)
        self.win.present()

    def show_about(self,action):
        about_dialog = self.builder.get_object("about")
        about_dialog.set_visible(True)

    def show_delete(self,action):
        self.delete_dialog.set_property("secondary-text",f"Do you really want to delete {self.versions[self.version_dropdown.get_selected()]}?")
        cancel_button = self.delete_dialog.get_child().get_last_child().get_first_child().get_first_child()
        # print(cancel_button.get_css_classes())
        cancel_button.set_css_classes(["text-button","destructive","flat","default"])
        # print(cancel_button.get_css_classes())
        self.delete_dialog.set_visible(True)

    def show_install(self,action):
        install_dialog = self.builder.get_object("install")
        install_dialog.set_visible(True)

    def show_preferences(self,action):
        preferences_dialog = self.builder.get_object("preferences")
        preferences_dialog.set_title(self.versions[self.version_dropdown.get_selected()])
        preferences_dialog.set_visible(True)

    def launch(self,action):
        print(dir(action))
        print(self.version_dropdown.get_selected())

    def reauth(self,action):
        pass

    def handle_delete(self,action,param):
        print(param)
        self.delete_dialog.set_visible(False)

app = Minceraft(application_id="com.github.muslimitmilch.minceraft")
app.run(sys.argv)
