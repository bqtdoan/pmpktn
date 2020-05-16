from db_sql.sampling import commit_population
from db_sql.make_db import make_db, drop_db
from log_in_dialog import LogInDialog
from core.main_view import MainView
from nurse_view import NurseView
from print_func.print_func import MyPrinter
import wx

import argparse


def mainloop():
    app = wx.App()
    with LogInDialog(None) as dlg:
        job = dlg.ShowModal()
    if job == 0:  # doctor
        MainView(None).Show()
    elif job == 1:  # nurse
        NurseView(None).Show()
    else:
        quit()

    app.MainLoop()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--new", action="store_true",
                    help="make a new db")
    ap.add_argument("-s", "--sample", action="store_true",
                    help="sample 10 patients")
    ap.add_argument("-tpdf", "--testpdf", action="store_true",
                    help="make test pdf")
    args = vars(ap.parse_args())

    if args['new']:
        drop_db()
        make_db()
    if args["sample"]:
        commit_population()
    if args["testpdf"]:
        MyPrinter().preview_test()
    if not any(args.values()):
        mainloop()
