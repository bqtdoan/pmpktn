from initialize import *
from core.__init__ import *
from db_sql.db_func import query_linedrug_list_by_name
import os
import wx
import wx.adv
import logging


class DrugPopup(wx.ComboPopup):

    def __init__(self, parent):
        super().__init__()
        self.lc = None
        self.init_d_l = query_linedrug_list_by_name('').all()
        self.d_l = []

    def Create(self, parent):
        self.lc = wx.ListCtrl(
            parent,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.SIMPLE_BORDER)
        self.lc.AppendColumn('Thuốc', width=200)
        self.lc.AppendColumn('Số lượng')
        self.lc.AppendColumn('Đơn giá')
        self.lc.AppendColumn('Cách dùng', width=100)
        self.lc.Bind(wx.EVT_MOTION, self.OnMotion)
        self.lc.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.lc.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Update()
        return True

    def Init(self):
        self.value = -1
        self.curitem = -1

    def GetControl(self):
        return self.lc

    def SetStringValue(self, val):
        idx = self.lc.FindItem(-1, val)
        if idx != wx.NOT_FOUND:
            self.lc.Select(idx)

    def GetStringValue(self):
        if self.value >= 0:
            return self.lc.GetItemText(self.value, col=0)
        return ""

    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        return super().GetAdjustedSize(*popup_size)

    def Update(self, s=''):
        self.lc.DeleteAllItems()
        self.d_l = list(filter(lambda x: s.upper() in x.name, self.init_d_l))
        for item in self.d_l:
            self.lc.Append(
                [item.name, item.quantity, item.sale_price, item.usage])

    def OnMotion(self, e):
        item, flags = self.lc.HitTest(e.GetPosition())
        if item >= 0:
            self.lc.Select(item)
            self.curitem = item

    def OnLeftDown(self, e):
        try:
            self.value = self.curitem
            self.ComboCtrl.drugWH = self.d_l[self.value]
            self.Dismiss()
            self.ComboCtrl.SelectAll()
            self.ComboCtrl.SetInsertionPointEnd()
        except IndexError:
            self.Dismiss()

    def OnPopup(self):
        self.Init()
        self.Update(self.ComboCtrl.Value)
        if self.lc.ItemCount > 0:
            if self.curitem < (self.lc.ItemCount - 1):
                self.curitem += 1
            self.lc.Select(self.curitem)
            self.lc.EnsureVisible(self.curitem)

    def KeyDown(self):
        if self.lc.ItemCount > 0:
            if self.curitem < (self.lc.ItemCount - 1):
                self.curitem += 1
            self.lc.Select(self.curitem)
            self.lc.EnsureVisible(self.curitem)

    def KeyUp(self):
        if self.lc.ItemCount > 0:
            if self.curitem > 0:
                self.curitem -= 1
            self.lc.Select(self.curitem)
            self.lc.EnsureVisible(self.curitem)
        else:
            self.KeyESC()

    def KeyESC(self):
        a = self.ComboCtrl.Value
        self.Dismiss()
        self.ComboCtrl.ChangeValue(a)
        self.ComboCtrl.SetInsertionPointEnd()

    def KeyReturn(self):
        self.OnLeftDown(None)

    def onKeyPress(self, e):
        c = e.GetKeyCode()
        if c == wx.WXK_DOWN:
            self.KeyDown()
        elif c == wx.WXK_UP:
            self.KeyUp()
        elif c == wx.WXK_ESCAPE:
            self.KeyESC()
        elif c == wx.WXK_RETURN:
            self.KeyReturn()


class DrugPicker(wx.ComboCtrl):

    def __init__(self, parent):
        super().__init__(parent, size=drugctrl_size, style=wx.TE_PROCESS_ENTER)
        self.drug_popup = DrugPopup(self)
        self.SetPopupControl(self.drug_popup)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Bind(wx.EVT_TEXT, self.onTextChange)
        self.SetHint("Nhấn Enter để search thuốc")
        self._drugWH = None
        self.EnablePopupAnimation(enable=False)

    @property
    def drugWH(self):
        return self._drugWH

    @drugWH.setter
    def drugWH(self, dwh):
        self._drugWH = dwh
        v_inf = self.Parent
        if dwh:
            v_inf.usage_unit.Label = dwh.usage_unit
            v_inf.sale_unit.Label = dwh.sale_unit
        else:
            self.ChangeValue('')
            v_inf.dosage_per.ChangeValue('')
            v_inf.usage_unit.Label = '{Đơn vị}'
            v_inf.times.ChangeValue("")
            v_inf.quantity.ChangeValue("")
            v_inf.sale_unit.Label = '{Đơn vị}'
            v_inf.usage.ChangeValue("")

    def onKeyPress(self, e):
        if os.name == "posix":
            if e.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_DOWN]:
                if not self.IsPopupShown():
                    self.Popup()
            else:
                e.Skip()
        else:
            if e.GetKeyCode() not in [wx.WXK_RETURN,
                                      wx.WXK_UP,
                                      wx.WXK_DOWN,
                                      wx.WXK_ESCAPE]:
                if self.IsPopupShown():
                    a = self.Value
                    self.Dismiss()
                    self.ChangeValue(a)
                    self.SetInsertionPointEnd()
            e.Skip()

    def onTextChange(self, e):
        if os.name == "nt":
            if e.String == "":
                self.Clear()
            elif len(e.String) >= 1:
                if not self.IsPopupShown():
                    self.Popup()
                self.SetInsertionPointEnd()
        if os.name == "posix":
            if e.String == "":
                self.Clear()

    def Clear(self):
        self.drugWH = None


class DrugList(wx.ListCtrl):

    def __init__(self, parent):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.total_drug_price = 0
        self.dwh_list = []
        self.AppendColumn('STT', width=d_stt_w)
        self.AppendColumn('Thuốc', width=d_name_w)
        self.AppendColumn('Số cữ', width=d_socu_w)
        self.AppendColumn('Liều 1 cữ', width=d_l1cu_w)
        self.AppendColumn('Tổng cộng', width=d_tc_w)
        self.AppendColumn('Cách dùng', width=d_tc_w * 4)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onDrugSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDrugDeselect)

    def Update(self, linedruglist=None):
        if not linedruglist:
            linedruglist = self.Parent.Parent.visit.linedrugs
        self.dwh_list = [i.drug for i in linedruglist]
        self.DeleteAllItems()
        for i, ld in enumerate(linedruglist, start=1):
            self.Append(
                [i,
                 ld.drug.name,
                 f"{ld.times}",
                 f"{ld.dosage_per} {ld.drug.usage_unit}",
                 f"{ld.quantity} {ld.drug.sale_unit}",
                 ld.usage])
        self.calc_total_drug_price()

    def Clear(self):
        self.DeleteAllItems()
        self.dwh_list = []
        self.total_drug_price = 0

    def onDrugSelect(self, e):
        i = e.Index
        inf = self.Parent
        inf.drugpicker.drugWH = self.dwh_list[i]
        inf.drugpicker.ChangeValue(self.dwh_list[i].name)
        inf.times.ChangeValue(self.GetItemText(i, 2))
        inf.dosage_per.ChangeValue(self.GetItemText(i, 3).partition(' ')[0])
        inf.quantity.ChangeValue(self.GetItemText(i, 4).partition(' ')[0])
        inf.usage.ChangeValue(self.GetItemText(i, 5))

    def onDrugDeselect(self, e):
        self.Parent.drugpicker.Clear()

    def Add_or_Update(self, **kwargs):
        assert self.ItemCount == len(self.dwh_list)
        inf = self.Parent
        try:
            # find if already added drug
            row = [i.id for i in self.dwh_list].index(d.id)
            loggin.debug('drug found -> UPDATE ')
            self.SetItem(row, 2, times.Value)
            self.SetItem(row, 3, f"{dosage_per.Value} {d.usage_unit}")
            self.SetItem(row, 4, f"{quantity.Value} {d.sale_unit}")
            self.SetItem(row, 5, usage.Value)
        except ValueError:
            logging.debug('drug not found -> ADD')
            self.Append([
                self.ItemCount + 1,
                d.name,
                times.Value,
                f"{dosage_per.Value} {d.usage_unit}",
                f"{quantity.Value} {d.sale_unit}",
                usage.Value
            ])
            self.dwh_list.append(d)
        inf.drugpicker.Clear()
        inf.drugpicker.SetFocus()
        self.calc_total_drug_price()

    def Remove(self):
        assert self.ItemCount == len(self.dwh_list)
        idx = self.GetFirstSelected()
        logging.debug(f"Delete drug {self.dwh_list[idx].name} ")
        if idx >= 0:
            self.dwh_list.pop(idx)
            self.DeleteItem(idx)
            for row in range(1, self.ItemCount):
                self.SetItem(row - 1, 0, str(row))
        else:
            logging.debug('drug not selected when delete')
        self.calc_total_drug_price()

    def calc_total_drug_price(self):
        assert self.ItemCount == len(self.dwh_list)
        self.total_drug_price = 0
        if self.ItemCount > 0:
            for i in range(self.ItemCount):
                qty = int(self.GetItemText(i, 4).partition(' ')[0])
                p = self.dwh_list[i].sale_price
                self.total_drug_price += (qty * p)

    def build_linedrugs(self):
        linedrugs = []
        for i in range(self.ItemCount):
            ld = {}
            ld['drug_id'] = self.dwh_list[i].id
            ld['dosage_per'] = self.GetItemText(i, 3).partition(' ')[0]
            ld['times'] = int(self.GetItemText(i, 2))
            ld['quantity'] = int(self.GetItemText(i, 4).partition(' ')[0])
            ld['usage'] = self.GetItemText(i, 5)
            linedrugs.append(ld)
        return linedrugs
