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

import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pisi.api
import pisi.db
from dbus.mainloop.glib import DBusGMainLoop
import comar
import pm


class umMainClass(QMainWindow):
    def __init__(self,ebeveyn=None):
        super(umMainClass,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        self.name = "um"
        self.button_style = "border: none"
        self.tumunuSec = False
        self.gorunuyor = False
        self.sistemTablasiPencere = sistemTablasi(self)

        kutu_1 = QHBoxLayout()
        kutu_2 = QHBoxLayout()
        kutular = QVBoxLayout()
        kutular.addLayout(kutu_1)
        kutular.addLayout(kutu_2)
        merkezWidget = QWidget()
        merkezWidget.setLayout(kutular)
        self.setCentralWidget(merkezWidget)

        self.kaldirilacaklar = []
        self.kurulacaklar = []
        self.guncellenecekler = []

        self.appsList = QListWidget()
        kutu_1.addWidget(self.appsList)

        self.tumunu_sec_button = QPushButton(self.tr("Select All"))
        self.tumunu_sec_button.setIcon(QIcon(":/images/tumunuSec.svg"))
        self.tumunu_sec_button.setIconSize(QSize(24,24))
        self.tumunu_sec_button.setStyleSheet(self.button_style)
        self.tumunu_sec_button.pressed.connect(self.tumunuSecFonk)
        kutu_2.addWidget(self.tumunu_sec_button)

        self.yenile_button = QPushButton(self.tr("Refresh"))
        self.yenile_button.setIcon(QIcon(":/images/yenile.svg"))
        self.yenile_button.setIconSize(QSize(24,24))
        self.yenile_button.setStyleSheet(self.button_style)
        self.yenile_button.pressed.connect(self.updateDepo)
        kutu_2.addWidget(self.yenile_button)

        self.guncelle_button = QPushButton(self.tr("Update"))
        self.guncelle_button.setIcon(QIcon(":/images/apply.svg"))
        self.guncelle_button.setIconSize(QSize(24,24))
        self.guncelle_button.setStyleSheet(self.button_style)
        self.guncelle_button.pressed.connect(self.operationWidgetRun)
        kutu_2.addWidget(self.guncelle_button)
        self.setMinimumSize(500,300)
        self.setWindowTitle(self.tr("Updates"))
        self.updateDepo()
        self.appsListAddItem()

    def appsListAddItem(self):
        self.guncellenecekler = []
        guncellenecek_paketler = pisi.api.list_upgradable()
        self.appsList.clear()
        for i in guncellenecek_paketler:
            customWidget = CustomWidgetPackageClass(self)
            customWidget.paketAdiIconEkle(i)
            if self.tumunuSec:
                customWidget.checkBoxTrue()
            customListWidgetItem = QListWidgetItem(self.appsList)
            customListWidgetItem.setSizeHint(customWidget.sizeHint())
            self.appsList.setItemWidget(customListWidgetItem,customWidget)
            qApp.processEvents()

    def tumunuSecFonk(self):
        if self.tumunuSec:
            self.tumunuSec = False
        else:
            self.tumunuSec = True
        self.appsListAddItem()

    def operationWidgetRun(self):
        self.operationWindow = pm.OperationWidgetClass(self)
        self.operationWindow.exec_()

    def updateDepo(self):
        DBusGMainLoop(set_as_default=True)
        self.link = comar.Link()
        self.pmanager = self.link.System.Manager['pisi']
        self.link.listenSignals("System.Manager",self.donut)
        self.pmanager.updateAllRepositories()
        self.appsListAddItem()
        self.sistemTablasiPencere.mesajGoster()

    def donut(self,package,signal,args):
        pass

    def pencereBuyutKucult(self):
        if self.gorunuyor:
            self.hide()
        else:
            self.show()

    def hideEvent(self,olay):
        self.gorunuyor = False

    def showEvent(self,olay):
        self.gorunuyor = True

    def pencereBuyutKucultSignal(self,reason):
        if reason == QSystemTrayIcon.Trigger:
            self.pencereBuyutKucult()

    def kapat(self):
        qApp.quit()

class CustomWidgetPackageClass(QWidget):
    def __init__(self,ebeveyn=None):
        super(CustomWidgetPackageClass,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
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
            self.ebeveyn.guncellenecekler.append(self.paketAdi)
        else:
            self.guncelle_check_box.setText(self.tr("Update"))
            self.ebeveyn.guncellenecekler.remove(self.paketAdi)

    def paketAdiIconEkle(self,paketAdi):
        self.paketAdi = paketAdi
        self.paket_adi.setText(self.paketAdi)
        if os.path.exists("/usr/share/Lime-Store/apps/"+paketAdi+".svg"):
            self.paket_icon.setPixmap(QPixmap("/usr/share/Lime-Store/apps/"+paketAdi+".svg").scaled(32,32))
        else:
            self.paket_icon.setPixmap(QPixmap("/usr/share/Lime-Store/apps/package.svg").scaled(32,32))

    def checkBoxTrue(self):
        self.guncelle_check_box.setChecked(True)

class sistemTablasi(QWidget):
    def __init__(self,ebeveyn=None):
        super(sistemTablasi,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        self.tablaSimgesi = QSystemTrayIcon(self)
        self.tablaSimgesi.setIcon(QIcon(":/images/sisTab.png"))
        self.tablaSimgesi.show()
        self.tablaSimgesi.activated.connect(self.ebeveyn.pencereBuyutKucultSignal)
        menu = QMenu("Context Menu", self)
        menu.addAction(QAction(QIcon(":/images/ac-kapa.svg"),self.tr("Max-Min"),self,statusTip=self.tr("Max-Min"),triggered=self.ebeveyn.pencereBuyutKucult,checkable=False))
        menu.addAction(QAction(QIcon(":/images/yenile.svg"),self.tr("Refresh"),self,statusTip=self.tr("Refresh"),triggered=self.ebeveyn.updateDepo,checkable=False))
        menu.addAction(QAction(QIcon(":/images/kapat.svg"),self.tr("Close"),self,statusTip=self.tr("Close"),triggered=self.ebeveyn.kapat,checkable=False))
        self.tablaSimgesi.setContextMenu(menu)

    def mesajGoster(self):
        if len(pisi.api.list_upgradable()) == 0:
            self.tablaSimgesi.showMessage(self.tr("Up To Date"), self.tr("Your system is up to date"),icon=QSystemTrayIcon.Information, msecs=10000)
        else:
            msj = str(len(pisi.api.list_upgradable())) + self.tr(" Package update available")
            self.tablaSimgesi.showMessage(self.tr("Update Available"), msj, icon=QSystemTrayIcon.Information, msecs=10000)
            self.tablaSimgesi.messageClicked.connect(self.ebeveyn.pencereBuyutKucult)
