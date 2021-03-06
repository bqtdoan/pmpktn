from initialize import *
import other_func as otf
import db_sql.db_func as dbf
from patient_dialog import EditPatientDialog
import wx


class MyMenuBar(wx.MenuBar):

    def __init__(self, mv):
        super().__init__()
        self.mv = mv
        self._createMenu()

    def _createMenu(self):
        homeMenu = wx.Menu()
        menuAbout = homeMenu.Append(wx.ID_ABOUT, "Thông tin")
        menuExit = homeMenu.Append(wx.ID_EXIT, "&Exit\tALT+F4")

        patientMenu = wx.Menu()
        menuNewPatient = patientMenu.Append(
            id_new_patient, "Bệnh nhân mới\tF1")
        menuEditPatient = patientMenu.Append(
            id_edit_patient, "Chỉnh sửa thông tin bệnh nhân")
        menuDelPatient = patientMenu.Append(
            id_del_patient, "Xoá bệnh nhân")
        patientMenu.AppendSeparator()

        menuNewVisit = patientMenu.Append(id_new_visit, "Lượt khám mới\tF2")
        menuSaveVisit = patientMenu.Append(id_save_visit, "Lưu lượt khám\tF3")

        editMenu = wx.Menu()
        menuRefresh = editMenu.Append(wx.ID_REFRESH, "Refresh\tF5")

        reportmenu = wx.Menu()
        menureporttoday = reportmenu.Append(wx.ID_ANY, "Báo cáo hôm nay")

        self.Append(homeMenu, "Home")
        self.Append(patientMenu, "Khám bệnh")
        self.Append(editMenu, "Edit")
        self.Append(reportmenu, "Báo cáo")

        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onNewPatient, menuNewPatient)
        self.Bind(wx.EVT_MENU, self.onEditPatient, menuEditPatient)
        self.Bind(wx.EVT_MENU, self.onDelPatient, menuDelPatient)
        self.Bind(wx.EVT_MENU, self.onNewVisit, menuNewVisit)
        self.Bind(wx.EVT_MENU, self.onSaveVisit, menuSaveVisit)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)

        self.Bind(wx.EVT_MENU, self.onRefresh, menuRefresh)

        self.Bind(wx.EVT_MENU, self.onReportToday, menureporttoday)

    def onAbout(self, e):
        with wx.MessageDialog(self.mv, "Tạo bởi Vương Kiến Thanh\nthanhstardust@outlook.com",
                              "Phần mềm phòng khám tại nhà", wx.OK) as dlg:
            dlg.ShowModal()

    def onNewPatient(self, e):
        self.mv.right.NewPatient()

    def onEditPatient(self, e):
        pid = int(wx.GetTextFromUser(
            "Mã bệnh nhân cần chỉnh sửa", "Chỉnh sửa thông tin bệnh nhân", parent=self.mv))
        if pid != "":
            patient = next(filter(lambda x: x.id == pid,
                                  self.mv.left.book.GetPage(0).init_p_list))
            with EditPatientDialog(self.mv, patient) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    dlg.edit_patient()
                    wx.MessageBox("Đã lưu thay đổi", "Chỉnh sửa thông tin bệnh nhân")

    def onDelPatient(self, e):
        pid = int(wx.GetTextFromUser(
            "Mã bệnh nhân cần xoá", "Xoá bệnh nhân", parent=self.mv))
        if pid != "":
            patient = next(filter(lambda x: x.id == pid,
                                  self.mv.left.book.GetPage(0).init_p_list))
            dbf.delete_patient(patient, sess=self.mv.sess)
            wx.MessageBox("Đã xoá bệnh nhân", "Xoá bệnh nhân")


    def onNewVisit(self, e):
        self.mv.right.NewVisit()

    def onSaveVisit(self, e):
        self.mv.right.SaveVisit()

    def onExit(self, e):
        self.mv.Close()

    def onRefresh(self, e):
        self.mv.Refresh()

    def onReportToday(self, e):
        count, income, cost, sale, profit = [
            otf.bill_int_to_str(i) for i in dbf.GetTodayReport()]

        with wx.MessageDialog(self.mv,
                              f"Tổng số lượt khám: {count}\n"
                              f"Tổng thu: {income}\n\n"
                              f"Tiền thuốc vốn: {cost}\n"
                              f"Tiền thuốc bán ra: {sale}\n"
                              f"Lời từ thuốc: {profit}",
                              "Báo cáo hôm nay") as dlg:
            dlg.ShowModal()
