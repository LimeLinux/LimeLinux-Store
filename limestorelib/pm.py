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

from dbus.mainloop.glib import DBusGMainLoop
import comar
import pisi.api
import pisi.db

class pmMainClass(QMainWindow):
    def __init__(self,ebeveyn=None):
        super(pmMainClass,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        self.name = "main"

        DBusGMainLoop(set_as_default=True)
        kutu_1 = QHBoxLayout()
        kutu_2 = QHBoxLayout()
        kutu_3 = QHBoxLayout()
        kutular = QVBoxLayout()
        kutular.addLayout(kutu_1)
        kutular.addLayout(kutu_2)
        kutular.addLayout(kutu_3)
        merkezWidget = QWidget()
        merkezWidget.setLayout(kutular)
        self.setCentralWidget(merkezWidget)
        self.setMinimumSize(1000,600)
        self.setWindowTitle(self.tr("Package Shop"))
        self.installApps = pisi.api.list_installed()
        self.listedeki_paketler = pisi.api.list_available()

        self.kur_kaldir = "Kur"

        self.kaldirilacaklar = []
        self.kurulacaklar = []
        self.guncellenecekler = []

        self.button_style = "border: none"
        self.groups = {}
        self.db_group = pisi.db.groupdb.GroupDB()
        self.mapper = QSignalMapper(self)

        self.all_button = QPushButton()
        self.all_button.setIcon(QIcon(":/apps/all.svg"))
        self.all_button.setIconSize(QSize(24,24))
        self.all_button.setStyleSheet(self.button_style)
        self.all_button.pressed.connect(self.paketBilgileriGuncelle)
        kutu_1.addWidget(self.all_button)

        for i in self.db_group.list_groups():
            if i != "all":
                _name = self.db_group.get_group(i)
                name = _name.icon
                varmi = self.groups.get(name,"bunelan")
                if varmi == "bunelan":
                    self.groups[name] = [i]
                    button = QPushButton()
                    button.setToolTip(name)
                    button.setWhatsThis(i)
                    button.setIcon(QIcon("/usr/share/Lime-Store/apps/"+name+".svg"))
                    button.setIconSize(QSize(20,20))
                    button.setFixedWidth(20)
                    button.setFixedHeight(20)
                    button.setStyleSheet(self.button_style)
                    button.pressed.connect(self.mapper.map)
                    kutu_1.addWidget(button)
                    self.mapper.setMapping(button,name)
                else:
                    varmi.append(i)
        self.mapper.mapped["QString"].connect(self.groupComponents)

        self.search_Line = QLineEdit()
        self.search_Line.returnPressed.connect(self.searchPackage)
        kutu_1.addWidget(self.search_Line)

        self.search_button = QPushButton()
        self.search_button.setIcon(QIcon(":/apps/search.svg"))
        self.search_button.setIconSize(QSize(24,24))
        self.search_button.setStyleSheet(self.button_style)
        self.search_button.pressed.connect(self.searchPackage)
        kutu_1.addWidget(self.search_button)

        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon(":/apps/settings.svg"))
        self.settings_button.setIconSize(QSize(24,24))
        self.settings_button.setStyleSheet(self.button_style)
        self.settings_button.pressed.connect(self.ayarlarBaslat)
        kutu_1.addWidget(self.settings_button)

        self.appsList = QListWidget()
        self.appsList.setViewMode(QListView.IconMode)
        kutu_2.addWidget(self.appsList)

        self.basket_icon_label = QLabel()
        self.basket_icon_label.setPixmap(QPixmap(":/apps/baskett.svg").scaled(24,24))
        self.basket_icon_label.setFixedWidth(30)
        kutu_3.addWidget(self.basket_icon_label)

        self.basket_information_label = QLabel(self.tr("No package selected"))
        kutu_3.addWidget(self.basket_information_label)


        self.group_name_label = QLabel("All")
        kutu_3.addWidget(self.group_name_label)

        self.apply_button = QPushButton(self.tr("Apply"))
        self.apply_button.setIcon(QIcon(":/apps/apply.svg"))
        self.apply_button.setFixedWidth(75)
        self.apply_button.setIconSize(QSize(24,24))
        self.apply_button.setStyleSheet(self.button_style)
        self.apply_button.pressed.connect(self.operationWidgetRun)
        kutu_3.addWidget(self.apply_button)

    def ayarlarBaslat(self):
        ayarlarPencere = SettingsWidgetClass(self)
        ayarlarPencere.show()

    def resizeEvent(self,olay):
        self.paketListesiYenile()

    def groupComponents(self,groups_name):
        self.groupPackages = []
        self.group_name_label.setText(groups_name)
        for i in self.groups.get(groups_name):
            for x in self.db_group.get_group_components(i):
                for y in pisi.db.componentdb.ComponentDB().get_packages(x):
                    self.groupPackages.append(y)

        self.listAdd = True
        self.packagesAddList(self.groupPackages)

    def paketBilgileriGuncelle(self):
        self.listAdd = True
        all_packages = pisi.api.list_available()
        all_packages.sort()
        self.group_name_label.setText("All")
        self.installApps = pisi.api.list_installed()
        self.packagesAddList(all_packages)

    def paketListesiYenile(self):
        self.listAdd = True
        self.packagesAddList(self.listedeki_paketler)

    def operationWidgetRun(self):
        self.operationWindow = OperationWidgetClass(self)
        self.operationWindow.exec_()

    def searchPackage(self):
        self.listAdd = False
        search_text = self.search_Line.text()
        if len(search_text) != 0:
            self.listAdd = True
            found_list = pisi.api.search_package([search_text])
            found_list.sort()
            self.packagesAddList(found_list)

    def packagesAddList(self,packages):
        self.listedeki_paketler = packages
        self.appsList.clear()
        for i in packages:
            if self.listAdd:
                self.appsname = i
                if self.kur_kaldir == "Kur":
                    if i not in self.installApps:
                        customWidget = CustomWidgetPackageClass(self)
                        customWidget.setText(i)
                        customWidget.setIcon(i)
                        customWidget.setButtonTextInstall()
                        customWidget.setCheckBoxTextAddBasket()
                        customListWidgetItem = QListWidgetItem(self.appsList)
                        customListWidgetItem.setSizeHint(customWidget.sizeHint())
                        self.appsList.setItemWidget(customListWidgetItem,customWidget)
                elif self.kur_kaldir == "Kaldır":
                    if i in self.installApps:
                        customWidget = CustomWidgetPackageClass(self)
                        customWidget.setText(i)
                        customWidget.setIcon(i)
                        customWidget.setButtonTextDelete()
                        customWidget.setCheckBoxTextNone()
                        customListWidgetItem = QListWidgetItem(self.appsList)
                        customListWidgetItem.setSizeHint(customWidget.sizeHint())
                        self.appsList.setItemWidget(customListWidgetItem,customWidget)
                qApp.processEvents()
            else:
                break
        self.listAdd = False

    def upgradeBasketLabel(self):
        bos = True
        text = ""
        if len(self.kurulacaklar) != 0:
            text += self.tr(" %d package will be installed")%(len(self.kurulacaklar))
            bos = False
        if len(self.kaldirilacaklar) !=0:
            text += self.tr(" %d package to be removed")%(len(self.kaldirilacaklar))
            bos = False
        if bos:
            text = self.tr("No package selected")
        self.basket_information_label.setText(text)

class CustomWidgetPackageClass(QWidget):
    def __init__(self,ebeveyn=None):
        super(CustomWidgetPackageClass,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        self.name = "c_widget"
        kutular = QGridLayout()
        self.appsname = self.ebeveyn.appsname
        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setFixedWidth(128)
        self.icon_label = QPushButton()
        self.icon_label.setStyleSheet("border: none")
        self.icon_label.setFixedWidth(128)
        self.icon_label.setFixedHeight(128)
        self.install_delete_button = QPushButton()
        self.install_delete_button.setFixedWidth(128)
        self.basket_check_box = QCheckBox()
        self.basket_check_box.setFixedWidth(128)
        kutular.addWidget(self.text_label,0,0,1,1)
        kutular.addWidget(self.icon_label,1,0,1,1)
        kutular.addWidget(self.install_delete_button,2,0,1,1)
        kutular.addWidget(self.basket_check_box,3,0,1,1)
        self.setLayout(kutular)
        self.icon_label.pressed.connect(self.infoView)
        self.install_delete_button.pressed.connect(self.buttonDeletePressed)

    def setText(self,icon_Url):
        self.text_label.setText(icon_Url)

    def setIcon(self,icon_Url):
        if os.path.exists("/usr/share/Lime-Store/apps/"+icon_Url+".svg"):
            self.icon_label.setIcon(QIcon("/usr/share/Lime-Store/apps/"+icon_Url+".svg"))
        else:
            self.icon_label.setIcon(QIcon("/usr/share/Lime-Store/apps/package.svg"))
        self.icon_label.setIconSize(QSize(128,128))

    def buttonDeletePressed(self):
        if self.kurulu:
            self.kurulacaklar = []
            self.kaldirilacaklar = [self.appsname]
        else:
            self.kaldirilacaklar = []
            self.kurulacaklar = [self.appsname]
        self.guncellenecekler = []
        self.operationWindow = OperationWidgetClass(self)
        self.operationWindow.exec_()

    def setButtonTextInstall(self):
        self.install_delete_button.setText(self.tr("Install"))
        self.install_delete_button.setStyleSheet("QPushButton { background-color: #8dd35f; color:#ffffff}")

    def setButtonTextDelete(self):
        self.install_delete_button.setText(self.tr("Remove"))
        self.install_delete_button.setStyleSheet("QPushButton { background-color: #f0544c; color:#ffffff}")

    def setCheckBoxTextAddBasket(self):
        self.basket_check_box.setText(self.tr("Add to Basket"))
        self.kurulu = False
        if self.appsname in self.ebeveyn.kurulacaklar:
            self.basket_check_box.setChecked(True)
        self.basket_check_box.stateChanged.connect(self.checkButtonPressed)

    def setCheckBoxTextNone(self):
        self.basket_check_box.setText(self.tr("Add To Removals"))
        self.kurulu = True
        if self.appsname in self.ebeveyn.kaldirilacaklar:
            self.basket_check_box.setChecked(True)
        self.basket_check_box.stateChanged.connect(self.checkButtonPressed)

    def infoView(self):
        self.infoText = str(pisi.api.info(self.appsname)[0])
        self.infoWindow = InfoWidgetClass(self)
        self.infoWindow.show()

    def checkButtonPressed(self):
        if self.kurulu:
            if self.basket_check_box.isChecked():
                self.ebeveyn.kaldirilacaklar.append(self.appsname)
            else:
                self.ebeveyn.kaldirilacaklar.remove(self.appsname)
        else:
            if self.basket_check_box.isChecked():
                self.ebeveyn.kurulacaklar.append(self.appsname)
            else:
                self.ebeveyn.kurulacaklar.remove(self.appsname)
        self.ebeveyn.upgradeBasketLabel()

class InfoWidgetClass(QDialog):
    def __init__(self,ebeveyn=None):
        super(InfoWidgetClass,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        kutular = QGridLayout()
        self.package_name_label = QLabel()
        kutular.addWidget(self.package_name_label,0,1,1,1)
        self.summary_label = QLabel()
        kutular.addWidget(self.summary_label,1,1,1,1)
        self.description_label = QLabel()
        kutular.addWidget(self.description_label,2,1,1,1)
        self.icon_label = QLabel()
        self.icon_label.setFixedWidth(128)
        self.icon_label.setFixedHeight(128)
        self.icon_label.setScaledContents(True)
        kutular.addWidget(self.icon_label,0,0,3,1)
        self.setLayout(kutular)
        self.setWindowFlags(Qt.Popup)
        self.infoCustomization()
        self.setIcon(self.ebeveyn.appsname)

        screenSize = QDesktopWidget().screenGeometry()
        cursorPos = QCursor.pos()
        pos_x = cursorPos.x()
        pos_y = cursorPos.y()
        if pos_x + self.sizeHint().width() > screenSize.width():
            pos_x = screenSize.width() - self.sizeHint().width()
        if pos_y + self.sizeHint().height() > screenSize.height():
            pos_y = screenSize.height() - self.sizeHint().height()
        self.move(QPoint(pos_x,pos_y))

    def infoCustomization(self):
        text = self.ebeveyn.infoText.split("\n")
        text_name = ""
        text_summary = ""
        text_description = ""
        for i in text:
            split_text = i.split(":")
            if len(split_text) > 0 and split_text[0] == "Package":
                text_name += (split_text[1][1:] + "=" + split_text[2])
            elif len(split_text) > 0 and split_text[0] == "Summary":
                text_summary += (split_text[0] + "=" + split_text[1])
            elif len(split_text) > 0 and split_text[0] == "Description":
                text_description += (split_text[0] + "=" + split_text[1])
            elif len(split_text) > 0 and split_text[0] == "IsA":
                self.package_name_label.setText(text_name)
                self.summary_label.setText(text_summary)
                self.description_label.setText(text_description)
                break
            else:
                if split_text[0] == "Source":
                    pass
                elif text_summary == "":
                    text_name += (i + "\n")
                elif text_description == "":
                    text_summary += (i + "\n")
                else:
                    text_description += (i + "\n")

    def setIcon(self,icon_Url):
        if os.path.exists("/usr/share/Lime-Store/apps/"+icon_Url+".svg"):
            self.icon_label.setPixmap(QPixmap("/usr/share/Lime-Store/apps/"+icon_Url+".svg").scaled(128,128))
        else:
            self.icon_label.setPixmap(QPixmap("/usr/share/Lime-Store/apps/package.svg").scaled(128,128))

class OperationWidgetClass(QDialog):
    def __init__(self,ebeveyn=None):
        super(OperationWidgetClass,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        kutular = QGridLayout()
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0,100)
        kutular.addWidget(self.progressBar,0,0,1,2)
        self.actions = QTextEdit()
        kutular.addWidget(self.actions,1,0,1,2)
        self.exitButton = QPushButton("Çık")
        self.exitButton.pressed.connect(self.kapatFonk)
        kutular.addWidget(self.exitButton,2,0,1,1)
        self.startButton = QPushButton("Başla")
        self.startButton.pressed.connect(self.startFonk)
        kutular.addWidget(self.startButton,2,1,1,1)
        self.setLayout(kutular)
        self.setWindowTitle(self.tr("Operation"))
        self.operationsInformation()

    def kapatFonk(self):
        QDialog.accept(self)
        self.listeGuncelle()

    def closeEvent(self,olay):
        QDialog.accept(self)
        self.listeGuncelle()

    def operationsInformation(self):
        total = ""
        operasyon = ""
        if len(self.ebeveyn.kurulacaklar):
            operasyon += self.tr("===================\nPackages to Install\n===================\n")
            sayac = 0
            for x in pisi.api.get_install_order(self.ebeveyn.kurulacaklar):
                operasyon = operasyon + "+" + x + "   %d KB\n"%(pisi.api.calculate_download_size([x])[0])
                sayac += 1
            total += self.tr("%d package will be installed\n")%(sayac)
        if len(self.ebeveyn.kaldirilacaklar):
            operasyon += self.tr("===================\nPackages to Remove\n===================\n")
            sayac = 0
            for x in pisi.api.get_remove_order(self.ebeveyn.kaldirilacaklar):
                operasyon = operasyon + "-" + x + "\n"
                sayac += 1
            total += self.tr("%d Package to be removed\n")%(sayac)
        if len(self.ebeveyn.guncellenecekler):
            operasyon += self.tr("===================\nPackages to be updated\n===================\n")
            sayac = 0
            for x in pisi.api.get_upgrade_order(self.ebeveyn.guncellenecekler):
                operasyon = operasyon + "^" + x + "\n"
                sayac += 1
            for x in pisi.api.get_base_upgrade_order(self.ebeveyn.guncellenecekler):
                operasyon = operasyon + "^" + x + "\n"
                sayac += 1
            total += self.tr("%d package to be updated\n")%(sayac)
        self.actions.setText(total + operasyon)

    def startFonk(self):
        self.startButton.setDisabled(True)
        self.link = comar.Link()
        self.pmanager = self.link.System.Manager['pisi']
        self.link.listenSignals("System.Manager",self.donut)
        if len(self.ebeveyn.kaldirilacaklar) != 0:
            self.pmanager.removePackage(",".join(self.ebeveyn.kaldirilacaklar), async=self.donut)
        if len(self.ebeveyn.kurulacaklar) != 0:
            self.pmanager.installPackage(",".join(self.ebeveyn.kurulacaklar), async=self.donut)
        if len(self.ebeveyn.guncellenecekler) != 0:
            self.pmanager.updatePackage(",".join(self.ebeveyn.guncellenecekler), async=self.donut)

    def listeGuncelle(self):
        pisi.db.invalidate_caches()
        if self.ebeveyn.name == "main":
            self.ebeveyn.kaldirilacaklar = []
            self.ebeveyn.kurulacaklar = []
            self.ebeveyn.guncellenecekler = []
            self.ebeveyn.upgradeBasketLabel()
            self.ebeveyn.installApps = pisi.api.list_installed()
            self.ebeveyn.paketListesiYenile()
        elif self.ebeveyn.name == "c_widget":
            self.ebeveyn.ebeveyn.kaldirilacaklar = []
            self.ebeveyn.ebeveyn.kurulacaklar = []
            self.ebeveyn.ebeveyn.guncellenecekler = []
            self.ebeveyn.ebeveyn.upgradeBasketLabel()
            self.ebeveyn.ebeveyn.installApps = pisi.api.list_installed()
            self.ebeveyn.ebeveyn.paketListesiYenile()
        elif self.ebeveyn.name == "um":
            self.ebeveyn.updateDepo()

    def donut(self,package,signal,args):
        if signal == "status":
            islem = args[0]
            package_name = args[1]
            if islem == "updatingrepo":
                self.actionsAddText(self.tr("%s the repository is being updated...")%(package_name))
            elif islem == "extracting":
                self.actionsAddText(self.tr("%s package archive is open...")%(package_name))
            elif islem == "configuring":
                self.actionsAddText(self.tr("%s package is configured...")%(package_name))
            elif islem == "removing":
                self.actionsAddText(self.tr("%s package is being removed...")%(package_name))
            elif islem == "installing":
                self.actionsAddText(self.tr("%s package is being installed...")%(package_name))
            elif islem == "upgraded":
                self.actionsAddText(self.tr("%s package updated.")%(package_name))
            elif islem == "installed":
                self.actionsAddText(self.tr("%s package installed.")%(package_name))
            elif islem == "removed":
                self.actionsAddText(self.tr("%s package removed.")%(package_name))

        if signal == "progress":
            islem = args[0]
            if islem == "fetching":
                package_name = args[1]
                download_speed = args[3]
                speed_label = args[4]
                downloaded = args[5]
                download_size = args[6]
                speed = "%d %s" %(download_speed,speed_label)
                self.progressBarYuzdeHesaplama(downloaded,download_size)
                self.actionsAddText(self.tr("Downloading...\nPackage Name : %s \nDownload Speed : %s \nDownloaded Size : %d \nTotal Size :%d") %(package_name,speed,downloaded,download_size))
        elif signal == "finished" or signal == None:
            self.actionsAddText(self.tr("Completed."))
        elif signal == "eror":
            self.actionsAddText(self.tr("EROR!!!\n%s")%(args[0]))

    def actionsAddText(self,text):
        self.actions.clear()
        self.actions.setText(text)

    def progressBarYuzdeHesaplama(self,kucuk,buyuk):
        progres_precent = str(round(float(kucuk) / float(buyuk),2)).split(".")[1]
        if len(progres_precent) == 1:
            progres_precent = progres_precent + "0"
        elif len(progres_precent) == 0:
            progres_precent = "100"
        self.progressBar.setValue(int(progres_precent))

class SettingsWidgetClass(QDialog):
    def __init__(self,ebeveyn=None):
        super(SettingsWidgetClass,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        kutular = QGridLayout()
        self.sekmeler = QTabWidget()
        self.sekmeler.addTab(self.kur_kaldirSekmesi(),self.tr("Install-Remove"))
        self.sekmeler.addTab(self.depoSekmesi(),self.tr("Repos"))
        kutular.addWidget(self.sekmeler)
        self.setWindowTitle(self.tr("Settings"))
        self.setFixedWidth(550)
        self.setLayout(kutular)

    def kur_kaldirSekmesi(self):
        kur_kaldirParca = QWidget()
        kur_kaldirKutular = QGridLayout()
        kur_kaldirParca.setLayout(kur_kaldirKutular)
        label_kur = QLabel(self.tr("<b><center>Install Package</center></b>"))
        label_kaldir = QLabel (self.tr("<b><center>Remove Package</center></b>"))
        kur_kaldirKutular.addWidget(label_kur,0,0,1,1)
        kur_kaldirKutular.addWidget(label_kaldir,0,1,1,1)
        button_kur = QPushButton()
        button_kur.setIcon(QIcon(":/apps/package-add.svg"))
        button_kur.setIconSize(QSize(200,200))
        button_kur.setStyleSheet(self.ebeveyn.button_style)
        button_kur.pressed.connect(self.kurAyarla)
        kur_kaldirKutular.addWidget(button_kur,1,0,1,1)
        button_kaldir = QPushButton()
        button_kaldir.setIcon(QIcon(":/apps/package-remove.svg"))
        button_kaldir.setIconSize(QSize(200,200))
        button_kaldir.setStyleSheet(self.ebeveyn.button_style)
        button_kaldir.pressed.connect(self.kaldirAyarla)
        kur_kaldirKutular.addWidget(button_kaldir,1,1,1,1)
        return kur_kaldirParca

    def depoSekmesi(self):
        depoParca = QWidget()
        depoKutular = QGridLayout()
        depoParca.setLayout(depoKutular)
        self.repoListe = QListWidget()
        depoKutular.addWidget(self.repoListe,0,0,1,1)
        self.repoListesiDoldur(pisi.api.list_repos(only_active=False))
        self.repoEkle_dugme = QPushButton(self.tr("Add New Repo"))
        self.repoEkle_dugme.pressed.connect(self.repoEkleBaslat)
        depoKutular.addWidget(self.repoEkle_dugme,1,0,1,1)
        return depoParca

    def repoListesiDoldur(self,repolar):
        self.repoListe.clear()
        for i in repolar:
            customWidget = CustomWidgetRepoClass(self)
            customWidget.repoAdiEkle(i)
            customWidget.repoAdresiEkle(pisi.db.repodb.RepoDB().get_repo_url(i))
            if pisi.db.repodb.RepoDB().repo_active(i):
                customWidget.checkBoxAktif()
            else:
                customWidget.checkBoxAktifDegil()
            customListWidgetItem = QListWidgetItem(self.repoListe)
            customListWidgetItem.setSizeHint(customWidget.sizeHint())
            self.repoListe.setItemWidget(customListWidgetItem,customWidget)

    def kurAyarla(self):
        self.ebeveyn.kur_kaldir = "Kur"
        self.ebeveyn.kaldirilacaklar = []
        self.ebeveyn.upgradeBasketLabel()
        QDialog.accept(self)
        self.ebeveyn.paketListesiYenile()

    def kaldirAyarla(self):
        self.ebeveyn.kur_kaldir = "Kaldır"
        self.ebeveyn.kurulacaklar = []
        self.ebeveyn.upgradeBasketLabel()
        QDialog.accept(self)
        self.ebeveyn.paketListesiYenile()

    def repoEkleBaslat(self):
        repoEkleDiyalogPencere = RepoEkleDiyalogSinif(self)
        repoEkleDiyalogPencere.show()

class CustomWidgetRepoClass(QWidget):
    def __init__(self,ebeveyn=None):
        super(CustomWidgetRepoClass,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        self.name = "c_widget_repo"
        kutular = QGridLayout()
        self.aktif_check_box = QCheckBox()
        kutular.addWidget(self.aktif_check_box,0,0,1,2)
        kutular.addWidget(QLabel(self.tr("Repo Name:")),1,0,1,1)
        kutular.addWidget(QLabel(self.tr("Repo URL:")),2,0,1,1)
        self.repoAdi_label = QLabel()
        self.repoAdresi_label = QLabel()
        kutular.addWidget(self.repoAdi_label,1,1,1,1)
        kutular.addWidget(self.repoAdresi_label,2,1,1,1)
        self.silDugme = QPushButton(self.tr("Remove"))
        self.silDugme.pressed.connect(self.repoSil)
        kutular.addWidget(self.silDugme,0,3,3,1)
        self.setLayout(kutular)

    def repoSil(self):
        try:
            pisi.api.remove_repo(self.depoAdi)
            self.ebeveyn.repoListesiDoldur(pisi.api.list_repos(only_active=False))
        except:
            QMessageBox.warning(self,self.tr("Eror"),self.tr("Please run lime-store root user"))

    def repoAdiEkle(self,isim):
        self.depoAdi = isim
        self.repoAdi_label.setText(isim)

    def repoAdresiEkle(self,adres):
        self.repoAdresi_label.setText(adres)

    def checkBoxAktif(self):
        self.aktif_check_box.setChecked(True)
        self.aktif_check_box.setText(self.tr("Active"))
        self.aktif_check_box.stateChanged.connect(self.repoAktifDeaktif)

    def checkBoxAktifDegil(self):
        self.aktif_check_box.setChecked(False)
        self.aktif_check_box.setText(self.tr("Not Active"))
        self.aktif_check_box.stateChanged.connect(self.repoAktifDeaktif)

    def repoAktifDeaktif(self):
        if self.aktif_check_box.isChecked():
            self.aktif_check_box.setText(self.tr("Active"))
            pisi.db.repodb.RepoDB().activate_repo(self.depoAdi)
        else:
            self.aktif_check_box.setText(self.tr("Not Active"))
            pisi.db.repodb.RepoDB().deactivate_repo(self.depoAdi)

class RepoEkleDiyalogSinif(QDialog):
    def __init__(self,ebeveyn=None):
        super(RepoEkleDiyalogSinif,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        kutular = QGridLayout()
        kutular.addWidget(QLabel(self.tr("Repo Name")),0,0,1,1)
        kutular.addWidget(QLabel(self.tr("Repo Url")),1,0,1,1)
        self.repoAdi_line_edit = QLineEdit()
        kutular.addWidget(self.repoAdi_line_edit,0,1,1,1)
        self.repoUrl_line_edit = QLineEdit()
        kutular.addWidget(self.repoUrl_line_edit,1,1,1,1)
        self.ekle_dugme = QPushButton(self.tr("Add"))
        self.ekle_dugme.pressed.connect(self.repoKontrol)
        kutular.addWidget(self.ekle_dugme,2,0,1,2)
        self.setWindowTitle(self.tr("Add Repo"))
        self.setLayout(kutular)

    def repoKontrol(self):
        if self.repoAdi_line_edit.text() != "":
            if self.repoUrl_line_edit.text() != "":
                try:
                    pisi.api.add_repo(str(self.repoAdi_line_edit.text()),str(self.repoUrl_line_edit.text()))
                    print self.repoAdi_line_edit.text(),self.repoUrl_line_edit.text()
                    pisi.api.update_repo(str(self.repoAdi_line_edit.text()))
                except Exception as hata:
                    QMessageBox.warning(self,self.tr("Eror"),str(hata))
                    pisi.api.remove_repo(self.repoAdi_line_edit.text())
                self.ebeveyn.repoListesiDoldur(pisi.api.list_repos(only_active=False))
                QDialog.accept(self)
            else:
                QMessageBox.warning(self,self.tr("Eror"),self.tr("Please enter a repo URL"))
        else:
            QMessageBox.warning(self,self.tr("Eror"),self.tr("Please enter a repo Name"))
