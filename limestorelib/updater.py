#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#  Copyright 2016 Fatih KAYA <sonakinci41@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA

import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pisi.api
import pisi.db
from dbus.mainloop.glib import DBusGMainLoop
import comar
import store


class UpdaterWindow(QWidget):

    def __init__(self, parent=None):
        super(UpdaterWindow, self).__init__(parent)
        self.parent = parent
        self.setWindowIcon(QIcon(":/images/limelinux-updater.svg"))
        self.setWindowTitle(self.tr("System Updater"))
        self.setMinimumSize(500, 300)
        self.setLayout(QVBoxLayout())

        self.systemTray = SystemTray(self)

        self.updateListWidget = QListWidget()
        self.layout().addWidget(self.updateListWidget)

        buttonLayout = QHBoxLayout()
        self.layout().addLayout(buttonLayout)

        self.allButton = QCheckBox(self.tr("Select All"))
        self.allButton.setIcon(QIcon(":/images/tumunuSec.svg"))
        self.allButton.setIconSize(QSize(24, 24))
        self.allButton.toggled.connect(self.allSelectSlot)
        buttonLayout.addWidget(self.allButton)

        self.updateButton = QPushButton(self.tr("Update"))
        self.updateButton.setIcon(QIcon(":/images/yenile.svg"))
        self.updateButton.setIconSize(QSize(24, 24))
        self.updateButton.pressed.connect(self.updateRepo)
        buttonLayout.addWidget(self.updateButton)

        self.installButton = QPushButton(self.tr("Install"))
        self.installButton.setIcon(QIcon(":/images/apply.svg"))
        self.installButton.setIconSize(QSize(24, 24))
        self.installButton.pressed.connect(self.operationWidgetRun)
        buttonLayout.addWidget(self.installButton)


        self.updateRepo()
        self.appsListAddItem()

    def appsListAddItem(self):
        self.guncellenecekler = []
        guncellenecek_paketler = pisi.api.list_upgradable()
        self.updateListWidget.clear()

        for i in guncellenecek_paketler:
            customWidget = CustomWidgetPackageClass(self)
            customWidget.paketAdiIconEkle(i)

            customListWidgetItem = QListWidgetItem(self.updateListWidget)
            customListWidgetItem.setSizeHint(customWidget.sizeHint())

            self.updateListWidget.setItemWidget(customListWidgetItem, customWidget)
            qApp.processEvents()

    def allSelectSlot(self, all):
        if self.updateListWidget.count() > 0:
            if all:
                for row in range(self.updateListWidget.count()):
                    self.updateListWidget.item(row).setChecked(True)
                    qApp.processEvents()

            else:
                for row in range(self.updateListWidget.count()):
                    self.updateListWidget.item(row).setChecked(False)
                    qApp.processEvents()

    def operationWidgetRun(self): # Buna gerek kalmıcak
        self.operationWindow = store.OperationWidgetClass(self)
        self.operationWindow.exec_()

    def updateRepo(self):
        DBusGMainLoop(set_as_default=True)

        self.link = comar.Link()
        self.pmanager = self.link.System.Manager['pisi']
        self.link.listenSignals("System.Manager",self.donut)
        self.pmanager.updateAllRepositories()
        self.appsListAddItem()
        self.systemTray.messageShow()

    def donut(self, package, signal, args):
        pass

    def windowHideOrShow(self, reason):
        if self.isVisible():
            self.setVisible(False)

        else:
            self.setVisible(True)

class CustomWidgetPackageClass(QWidget):

    path = "/usr/share/limelinux-store/apps"

    def __init__(self, parent=None):
        super(CustomWidgetPackageClass, self).__init__(parent)
        self.parent = parent

        kutular = QGridLayout()
        self.setLayout(kutular)
        self.guncelle_check_box = QCheckBox(self.tr("Update"))
        self.guncelle_check_box.setFixedWidth(120)
        self.guncelle_check_box.stateChanged.connect(self.checkBoxPressed)
        kutular.addWidget(self.guncelle_check_box,0,0,1,1)
        self.paket_icon = QLabel()
        self.paket_icon.setFixedWidth(32)
        kutular.addWidget(self.paket_icon,0,1,1,1)
        self.paket_adi = QLabel()
        kutular.addWidget(self.paket_adi,0,2,1,1)

    def checkBoxPressed(self):
        if self.guncelle_check_box.isChecked():
            self.guncelle_check_box.setText(self.tr("Updated"))
            self.parent.guncellenecekler.append(self.paketAdi)
        else:
            self.guncelle_check_box.setText(self.tr("Update"))
            self.parent.guncellenecekler.remove(self.paketAdi)

    def paketAdiIconEkle(self,paketAdi):
        info = pisi.api.info(self.paketAdi)
        text = str(info[0]).split("\n")

        yeni_Icon_Name = None
        for i in text:
            split_text = i.split(":")
            if len(split_text) > 0 and split_text[0] == "Icon":
                yeni_Icon_Name = split_text[1][1:]
                break

        if yeni_Icon_Name != "None":

            if os.path.exists(os.path.join(self.path, yeni_Icon_Name + ".svg")):
                self.paket_icon.setPixmap(QPixmap(os.path.join(self.path, yeni_Icon_Name + ".svg")))

            elif os.path.exists(os.path.join(self.path, self.paketAdi + ".svg")):
                self.paket_icon.setPixmap(QPixmap(os.path.join(self.path, self.paketAdi + ".svg")))

            else:
                self.paket_icon.setPixmap(QPixmap(os.path.join(self.path, "package.svg")))

        else:
            if os.path.exists(os.path.join(self.path, self.paketAdi + ".svg")):
                self.paket_icon.setPixmap(QPixmap(os.path.join(self.path, self.paketAdi + ".svg")))

            else:
                self.paket_icon.setPixmap(QPixmap(os.path.join(self.path, "package.svg")))

    def setChecked(self, check):
        self.guncelle_check_box.setChecked(check)


class SystemTray(QSystemTrayIcon):

    def __init__(self, parent=None):
        super(SystemTray, self).__init__(parent)
        self.parent = parent
        self.setIcon(QIcon(":/images/limelinux-updater.svg"))
        self.setToolTip(self.tr("System Updater"))
        self.activated.connect(self.parent.windowHideOrShow)


        menu = QMenu()
        menu.addAction(QAction(QIcon(":/images/yenile.svg"), self.tr("Update"), self, triggered=self.parent.updateRepo))
        menu.addAction(QAction(QIcon(":/images/kapat.svg"),self.tr("Close"), self, triggered=qApp.quit))
        self.setContextMenu(menu)

        self.show()

    def messageShow(self):
        if len(pisi.api.list_upgradable()) == 0:
            self.showMessage(self.tr("Up To Date"), self.tr("Your system is up to date"),icon=QSystemTrayIcon.Information, msecs=5000)

        else:
            msg = str(len(pisi.api.list_upgradable())) + self.tr(" Package update available")
            self.showMessage(self.tr("Update Available"), msg, icon=QSystemTrayIcon.Information, msecs=5000)
            self.messageClicked.connect(self.parent.pencereBuyutKucult)
