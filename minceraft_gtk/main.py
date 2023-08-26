#!/usr/bin/env python
import threading
from time import sleep

import gi
import minecraft_launcher_lib

gi.require_version("Gtk", "4.0")
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib, Gdk
import sys
sys.path.append('../src')
import minceraft

class Minceraft(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.oh = minceraft.optionHandler.OptionHandler()
        minceraft.handleArgs(self.oh)
        self.builder = Gtk.Builder()
        self.builder.add_from_file("minceraft_gtk.ui")
        self.win                        = self.builder.get_object("win")
        self.add_account_dialog         = self.builder.get_object("add-account-dialog")
        self.add_account_leaflet        = self.builder.get_object("add-account-leaflet")
        self.add_account_2fa            = self.builder.get_object("add-account-2fa")
        self.twoFA_url                  = self.builder.get_object("2fa-url")
        self.twoFA_confirm              = self.builder.get_object("2fa-confirm")
        self.twoFA_error_label          = self.builder.get_object("2fa-error-label")
        self.add_account_normal         = self.builder.get_object("add-account-normal")
        self.microsoft_mail             = self.builder.get_object("microsoft-mail")
        self.microsoft_password         = self.builder.get_object("microsoft-password")
        self.normal_error_label         = self.builder.get_object("normal-error-label")
        self.normal_spinner             = self.builder.get_object("normal-spinner")
        self.normal_confirm             = self.builder.get_object("normal-confirm")
        self.add_account_select         = self.builder.get_object("add-account-select")
        self.auth_type_select           = self.builder.get_object("auth-type-select")
        self.normal_auth_action         = self.builder.get_object("normal-auth-action")
        self.twoFA_action               = self.builder.get_object("2fa-action")
        self.add_account_minceraft      = self.builder.get_object("add-account-minceraft")
        self.minceraft_confirm          = self.builder.get_object("minceraft-confirm")
        self.minceraft_error_label      = self.builder.get_object("minceraft-error-label")
        self.minceraft_password2        = self.builder.get_object("minceraft-password2")
        self.minceraft_password         = self.builder.get_object("minceraft-password")
        self.minceraft_name             = self.builder.get_object("minceraft-name")
        self.delete_alert               = self.builder.get_object("delete-alert")
        self.about_dialog               = self.builder.get_object("about-dialog")
        self.install_page               = self.builder.get_object("install-page")
        self.fabric_check               = self.builder.get_object("fabric-check")
        self.vanilla_check              = self.builder.get_object("vanilla-check")
        self.forge_check                = self.builder.get_object("forge-check")
        self.modloader                  = self.builder.get_object("modloader")
        self.show_snapshots_check       = self.builder.get_object("show-snapshots-check")
        self.install_version_dropdown   = self.builder.get_object("install-version-dropdown")
        self.install_version_list       = self.builder.get_object("install-version-list")
        self.install_alias              = self.builder.get_object("install-alias")
        self.install_button             = self.builder.get_object("install-button")
        self.install_progress           = self.builder.get_object("install-progress")
        self.preferences_dialog         = self.builder.get_object("preferences-dialog")
        self.preferences_apply_button   = self.builder.get_object("preferences-apply-button")
        self.min_ram                    = self.builder.get_object("min-ram")
        self.min_ram_adj                = self.builder.get_object("min-ram-adj")
        self.max_ram                    = self.builder.get_object("max-ram")
        self.max_ram_adj                = self.builder.get_object("max-ram-adj")
        self.startup_port               = self.builder.get_object("startup-port")
        self.startup_server             = self.builder.get_object("startup-server")
        self.reauth_button              = self.builder.get_object("reauth-button")
        self.account_menu_button        = self.builder.get_object("account-menu-button")
        self.account_popover            = self.builder.get_object("account-popover")
        self.account_list               = self.builder.get_object("account-list")
        self.add_account_button         = self.builder.get_object("add-account-button")
        self.hamburger_popover          = self.builder.get_object("hamburger-popover")
        self.main_leaflet               = self.builder.get_object("main-leaflet")
        self.login_page                 = self.builder.get_object("login-page")
        self.login_dialog_label         = self.builder.get_object("login-dialog-label")
        self.login_dialog_entry         = self.builder.get_object("login-dialog-entry")
        self.login_wrong_password       = self.builder.get_object("login-wrong-password")
        self.main_page                  = self.builder.get_object("main-page")
        self.skin_apply_button          = self.builder.get_object("skin-apply-button")
        self.skin_slim_check            = self.builder.get_object("skin-slim-check")
        self.skin_select_button         = self.builder.get_object("skin-select-button")
        self.skin_select_label          = self.builder.get_object("skin-select-label")
        self.version_dropdown           = self.builder.get_object("version-dropdown")
        self.version_list               = self.builder.get_object("version-list")
        self.preferences_button         = self.builder.get_object("preferences-button")
        self.delete_button              = self.builder.get_object("delete-button")
        self.install_new_button         = self.builder.get_object("install-new-button")
        self.launch_button              = self.builder.get_object("launch-button")
        
        self.hamburger_menu = Gio.Menu.new()
        self.about_action = Gio.SimpleAction.new("about",None)
        self.add_action(self.about_action)

        self.account_menu = Gio.Menu.new()
        
        self.connectAll()
        self.hamburger_menu.append("About", "app.about")
        self.hamburger_popover.set_menu_model(self.hamburger_menu)
        self.account_popover.set_menu_model(self.account_menu)
        self.reauth_button.set_sensitive(False)

        self.file_dialog = Gtk.FileDialog.new()

        self.oh.set_debug_callback(print)
        if not self.oh.load():
            self.show_add_account_dialog(None)

        self.updateUsers()
        self.updateVersions()
        self.account_menu_button.set_label(self.oh.username)

        if self.oh.user_info["last_played"] != -1: self.version_dropdown.set_selected(self.oh.user_info["last_played"])
        self.main_leaflet.set_visible_child(self.login_page)

        self.current_max=0
        self.modloader="0"

    def on_activate(self, app):
        self.delete_alert.set_modal(self.win)
        self.win.set_application(self)
        self.win.present()

    def connectAll(self):
        """
        Connects all Signals to their required functions
        """

        self.minceraft_confirm.connect(         "clicked",      self.add_minceraft)
        self.normal_auth_action.connect(        "clicked",      self.manage_add_account_leaflet,2)
        self.twoFA_action.connect(              "clicked",      self.prepare2fa)
        self.about_action.connect(              "activate",     self.show_about)
        self.delete_button.connect(             "clicked",      self.show_delete)
        self.preferences_button.connect(        "clicked",      self.show_preferences)
        self.install_new_button.connect(        "clicked",      self.show_install)
        self.launch_button.connect(             "clicked",      self.launch)
        self.reauth_button.connect(             "clicked",      self.handle_reauth)
        self.add_account_button.connect(        "clicked",      self.show_add_account_dialog)
        self.delete_alert.connect(              "response",     self.handle_delete)
        self.login_dialog_entry.connect(        "apply",        self.login)
        self.min_ram.connect(                   "value-changed",self.handle_min_ram)
        self.max_ram.connect(                   "value-changed",self.handle_max_ram)
        self.preferences_apply_button.connect(  "clicked",      self.apply_preferences)
        self.normal_confirm.connect(            "clicked",      self.newNormalAuth)
        self.twoFA_confirm.connect(             "clicked",      self.new2FactorAuth)
        self.install_button.connect(            "clicked",      self.installVersion)
        self.vanilla_check.connect(             "toggled",      self.updateModloader)
        self.fabric_check.connect(              "toggled",      self.updateModloader)
        self.forge_check.connect(               "toggled",      self.updateModloader)
        self.show_snapshots_check.connect(      "toggled",      self.updateInstallVersions)
        self.skin_select_button.connect(        "clicked",      self.selectSkin)
        self.skin_apply_button.connect(         "clicked",      self.applySkin)

    def applySkin(self,action):
        self.width = "slim" if self.skin_slim_check.get_active() else "classic"
        self.skin_apply_button.set_sensitive(False)
        self.skin_slim_check.set_sensitive(False)
        self.skin_select_button.set_sensitive(False)
        self.win.set_cursor(Gdk.Cursor.new_from_name("wait"))
        pThread = threading.Thread(target=self.changeSkin)
        pThread.daemon=True
        pThread.start()

    def changeSkin(self):
        minceraft.changeSkin(self.oh,self.skin.get_parse_name(),self.width)
        GLib.idle_add(self.skin_apply_button.set_sensitive,True)
        GLib.idle_add(self.skin_slim_check.set_sensitive,True)
        GLib.idle_add(self.skin_select_button.set_sensitive,True)
        GLib.idle_add(self.win.set_cursor,None)

    def selectSkin(self,action):
        self.file_dialog.open(self.win,None,self.fileChooserCallback)

    def fileChooserCallback(self,action,result):
        self.skin = self.file_dialog.open_finish(result)
        self.skin_select_label.set_text(self.skin.get_basename().strip(".png"))

    def updateAccounts(self):
        self.account_menu.remove_all()
        for i in range(1,len(self.oh.users)+1):
            action = Gio.SimpleAction.new(str(i),None)
            self.add_action(action)
            action.connect("activate",self.changeAccount,i)
            self.account_menu.append(self.oh.users[i-1]["username"],f"app.{i}")

    def changeAccount(self,action,param,account):
        self.oh.user=account
        self.oh.load()
        self.updateVersions()
        self.account_menu_button.set_label(self.oh.username)
        self.login_dialog_entry.delete_text(0,-1)
        self.main_leaflet.set_visible_child(self.login_page)
        self.reauth_button.set_sensitive(False)


    def updateModloader(self,action):
        if action.get_active():
            self.updateInstallVersions(None)

    def updateInstallVersions(self,action):
        self.install_version_list.splice(0,len(self.install_version_list))
        if self.vanilla_check.get_active() or self.forge_check.get_active(): # forge doesnt have a list of supportet versions
            versions = minecraft_launcher_lib.utils.get_version_list()
            for version in versions:
                if version["type"]!="snapshot" or self.show_snapshots_check.get_active():
                    self.install_version_list.append(version["id"])
        elif self.fabric_check.get_active():
            if self.show_snapshots_check.get_active():
                for version in minecraft_launcher_lib.fabric.get_all_minecraft_versions():
                    self.install_version_list.append(version["version"])
            else:
                self.install_version_list.splice(0,0,minecraft_launcher_lib.fabric.get_stable_minecraft_versions())

    def installVersion(self,action):
        if self.vanilla_check.get_active():self.modloader="0"
        elif self.fabric_check.get_active():self.modloader="1"
        elif self.forge_check.get_active():self.modloader="2"
        else: self.modloader="3"
        self.install_progress.set_visible(True)
        self.install_button.set_sensitive(False)
        pThread = threading.Thread(target=self.install)
        pThread.daemon=True
        pThread.start()
        self.updateVersions()

    def install(self):
        callback = {
          "setStatus": self.set_status,
          "setProgress": self.set_progress,
          "setMax": self.set_max
        }
        minceraft.install(self.oh,
                          self.install_version_list.get_string(self.install_version_dropdown.get_selected()),
                          self.modloader,
                          self.install_alias.get_text(),
                          callback)

    def updateProgress(self):
        self.install_progress.set_fraction(self.install_progress.get_fraction())

    def set_status(self,status: str):
        print(status)
        if not status == "Installation complete":
            GLib.idle_add(self.install_progress.set_text,status)
        else:
            sleep(1)
            self.updateVersions()
            self.oh.saveConfig()
            self.main_leaflet.set_visible_child(self.main_page)


    def set_progress(self,progress: int):
        prog = f"{progress}/{self.current_max}"
        GLib.idle_add(self.install_progress.set_fraction,float(progress)/float(self.current_max))

    def set_max(self,new_max: int):
        self.current_max = new_max

    def updateVersions(self):
        self.version_list.splice(0,len(self.version_list))
        for i in self.oh.versions: self.version_list.append(i["alias"])

    def updateUsers(self):
        self.updateAccounts()
        # self.account_list.splice(0,len(self.account_list))
        # for i in self.oh.config[1:]:
            # self.account_list.append(i.get("username"))

    def prepare2fa(self,action):
        minceraft.twoFactorOpenBrowser()
        self.manage_add_account_leaflet(None,3)

    def new2FactorAuth(self,action):
        self.twoFA_error_label.set_text("")
        if not self.twoFA_url.get_text():
            self.twoFA_error_label.set_text("URL missing")
        else:
            auth_successfull=minceraft.newTwoFactorAuth(self.oh,
                                                        self.minceraft_name.get_text(),
                                                        self.minceraft_password.get_text(),
                                                        self.twoFA_url.get_text())
            if not auth_successfull:
                self.twoFA_error_label.set_text("The url is not valid, try again")
                minceraft.twoFactorOpenBrowser()
            else:
                self.oh.password=self.minceraft_password.get_text()
                self.updateUsers()
                self.add_account_dialog.set_visible(False)
                self.handle_version_buttons()



    def newNormalAuth(self,action):
        if not self.microsoft_mail.get_text() or not self.microsoft_password.get_text():
            self.normal_error_label.set_text("Mail address and password need to be provided")
        else:
            self.normal_error_label.set_text("")
            self.normal_confirm.set_sensitive(False)
            self.normal_spinner.set_spinning(True)
            nThread = threading.Thread(target=self.addNormalAuth)
            nThread.daemon=True
            nThread.start()

    def addNormalAuth(self):
        auth_successfull = minceraft.newNormalAuth(self.oh,
                                                   self.minceraft_name.get_text(),
                                                   self.minceraft_password.get_text(),
                                                   self.microsoft_mail.get_text(),
                                                   self.microsoft_password.get_text())
        if not auth_successfull:
            GLib.idle_add(self.normal_error_label.set_text,"Invalid credentials")
        else:
            self.oh.password=self.minceraft_password.get_text()
            GLib.idle_add(self.updateUsers)
            GLib.idle_add(self.add_account_dialog.set_visible,False)
        GLib.idle_add(self.normal_confirm.set_sensitive,True)
        GLib.idle_add(self.normal_spinner.set_spinning,False)
        GLib.idle_add(self.handle_version_buttons)


    def add_minceraft(self,action):
        if not self.minceraft_name.get_text():
            self.minceraft_error_label.set_text("Username missing")
        elif not self.minceraft_password.get_text() or not self.minceraft_password2.get_text():
            self.minceraft_error_label.set_text("Password missing")
        elif self.minceraft_password.get_text() != self.minceraft_password2.get_text():
            self.minceraft_error_label.set_text("Passwords are not the same")
        else:
            self.manage_add_account_leaflet(None,1)

    def apply_preferences(self,action):
        self.oh.versions[self.version_dropdown.get_selected()]["memory"][0] = str(int(self.max_ram.get_value()))
        self.oh.versions[self.version_dropdown.get_selected()]["memory"][1] = str(int(self.min_ram.get_value()))
        self.oh.versions[self.version_dropdown.get_selected()]["server"]    = self.startup_server.get_text()
        self.oh.versions[self.version_dropdown.get_selected()]["port"]      = str(int(self.startup_port.get_value()))
        self.oh.saveConfig()
        self.preferences_dialog.set_visible(False)

    def handle_min_ram(self,action):
        self.max_ram_adj.set_upper(self.min_ram.get_value())

    def handle_max_ram(self,action):
        self.min_ram_adj.set_upper(self.max_ram.get_value())

    def login(self,action):
        self.oh.password = self.login_dialog_entry.get_text()
        if self.oh.user_info["passwordHash"] == minceraft.encryption.hashValue(self.oh.password):
            self.login_wrong_password.set_visible(False)
            self.oh.config[0]["last_user"]=self.oh.user
            self.oh.load()
            self.oh.saveConfig()
            self.handle_version_buttons()
            self.main_leaflet.set_visible_child(self.main_page)
            self.reauth_button.set_sensitive(True)
            self.login_dialog_entry.delete_text(0,-1)
        else:
            self.login_wrong_password.set_visible(True)

    def handle_version_buttons(self):
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

    def show_add_account_dialog(self,action):
        self.add_account_leaflet.set_visible_child(self.add_account_minceraft)
        self.add_account_dialog.set_visible(True)

    def manage_add_account_leaflet(self,action,page):
        pages = [self.add_account_minceraft, self.add_account_select, self.add_account_normal, self.add_account_2fa]
        self.add_account_leaflet.set_visible_child(pages[page])
    
    def manage_main_leaflet(self,action,page):
        pages=[self.login_page,self.main_page]
        self.main_leaflet.set_visible_child(pages[page])

    def show_about(self,action,param):
        self.about_dialog.set_version(self.oh.config[0]["launcher_version"])
        self.about_dialog.set_visible(True)

    def show_delete(self,action):
        self.delete_alert.set_property("secondary-text",f"Do you really want to delete {self.oh.versions[self.version_dropdown.get_selected()]['alias']}?")
        cancel_button = self.delete_alert.get_child().get_last_child().get_first_child().get_first_child()
        self.delete_alert.get_child().get_last_child().get_first_child().set_focus_child(cancel_button)
        cancel_button.set_css_classes(["text-button","error","default"])
        self.delete_alert.set_visible(True)

    def show_install(self,action):
        self.updateInstallVersions(None)
        self.install_progress.set_visible(False)
        self.install_alias.set_text("")
        self.vanilla_check.set_active(True)
        self.install_button.set_sensitive(True)
        self.main_leaflet.set_visible_child(self.install_page)

    def show_preferences(self,action):
        self.preferences_dialog.set_title(self.oh.versions[self.version_dropdown.get_selected()]["alias"])
        self.max_ram_adj.set_value(int(self.oh.versions[self.version_dropdown.get_selected()]["memory"][0]))
        self.min_ram_adj.set_value(int(self.oh.versions[self.version_dropdown.get_selected()]["memory"][1]))
        self.startup_server.set_text(self.oh.versions[self.version_dropdown.get_selected()]["server"])
        port = self.oh.versions[self.version_dropdown.get_selected()]["port"]
        if port != "":
            self.startup_port.set_value(int(port))
        self.preferences_dialog.set_visible(True)

    def launch(self,action):
        minceraft.launch(self.oh,self.version_dropdown.get_selected())

    def handle_reauth(self,action):
        self.reauth_button.set_sensitive(False)
        self.win.set_cursor(Gdk.Cursor.new_from_name("wait"))
        nThread = threading.Thread(target=self.reauth)
        nThread.daemon=True
        nThread.start()

    def reauth(self):
        minceraft.auth(self.oh)
        GLib.idle_add(self.reauth_button.set_sensitive,True)
        GLib.idle_add(self.win.set_cursor,None)

    def handle_delete(self,action,param):
        if param == -8:
            minceraft.deleteVersion(self.oh,self.version_dropdown.get_selected())
            self.updateVersions()
            self.handle_version_buttons()
        self.delete_alert.set_visible(False)

app = Minceraft(application_id="com.github.muslimitmilch.minceraft")
app.run(sys.argv)
