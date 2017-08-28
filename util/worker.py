#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#
# code from https://stackoverflow.com/a/41605909
#
"""Worker module"""

import csv
import time

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from util import httpfn


B_COLOR = "\033[1;30m"
E_COLOR = "\033[0;m"
DBG = False

__module__ = "worker"


def printit(string):
    """Print a variable string for debug purposes"""
    print("{}\n{}{}{}".format(__module__, B_COLOR, string, E_COLOR))


class Worker(QObject):
    """
    Must derive from QObject in order to emit signals, connect slots to other signals, and operate in a QThread.
    """
    # demo signals
    sig_step_demo = pyqtSignal(int, str)  # worker id, step description: emitted every step through work() loop
    sig_done_demo = pyqtSignal(int)  # worker id: emitted at end of work()
    sig_msg_demo = pyqtSignal(str)  # message to be shown to user
    # real world signals
    sig_status = pyqtSignal(int, str)  # worker id, progress: emitted every step through the file
    sig_done = pyqtSignal(int)  # worker id: emitted at end of the file

    def __init__(self, thread_id: int, app):
        super().__init__()
        self.__app = app
        self.__thread_id = thread_id
        self.__abort = False

    @pyqtSlot()
    def import_contacts_csv(self, contacts, filename, header):
        """
        Import contacts using csv file
        :param contacts:
        :param filename:
        :param header:
        :return:
        """
        filename.encode("utf8")
        self.sig_status.emit(self.__thread_id, "{}".format("Forbereder indlæsning ..."))
        contacts.recreate_table()
        ftext = ">>> Import er færdig!"
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            line = 0
            for row in reader:
                self.__app.processEvents()
                if not len(row) == contacts.csv_field_count:
                    ftext = "FEJL: Formatet i den valgte fil er ikke korrekt!"
                    break
                if header and line == 0:
                    line += 1
                    continue
                self.sig_status.emit(self.__thread_id, "{} - {}".format(row[2].strip(), row[3].strip()))
                contacts.import_csv(row)  # send row to database

        self.sig_status.emit(self.__thread_id, "{}".format(ftext))
        self.sig_done.emit(self.__thread_id)

    @pyqtSlot()
    def import_customers_csv(self, customers, filename, header):
        """
        Import customers using csv file
        :param customers:
        :param filename:
        :param header:
        :return:
        """
        filename.encode("utf8")
        self.sig_status.emit(self.__thread_id, "{}".format("Forbereder indlæsning ..."))
        customers.recreate_table()
        ftext = ">>> Import er færdig!"
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            rows = list(reader)
            # self.progress_c.rowcount.emit(len(rows))
            for line, row in enumerate(rows):
                self.__app.processEvents()
                if not len(row) == customers.csv_field_count:
                    ftext = "FEJL: Formatet i den valgte fil er ikke korrekt!"
                    break
                # self.progress_c.rowcount.emit(line)
                if header and line == 0:
                    continue
                self.sig_status.emit(self.__thread_id, "{} - {}".format(row[1].strip(), row[2].strip()))
                customers.import_csv(row)  # send row to database

        self.sig_status.emit(self.__thread_id, "{}".format(ftext))
        self.sig_done.emit(self.__thread_id)

    @pyqtSlot()
    def import_customers_http(self, customers, employees, settings):
        """
        Import customers using http
        :param customers:
        :param employees:
        :param settings:
        :return:
        """
        self.sig_status.emit(self.__thread_id, "{}".format("Forbereder hentning ..."))
        # fetch datafile from http server
        data = httpfn.get_customers(settings, employees)
        self.sig_status.emit(self.__thread_id, "{}".format("Henter fra server ..."))
        for row in data:  # data processing
            self.__app.processEvents()
            self.sig_status.emit(self.__thread_id, "{} - {}".format(row[0], row[1]))
            customers.import_http(row)  # init_detail row to database
        self.sig_done.emit(self.__thread_id)

    @pyqtSlot()
    def import_products_http(self, products, settings):
        """
        Import products using http
        :param products:
        :param settings:
        """
        self.sig_status.emit(self.__thread_id, "{}".format("Forbereder hentning ..."))
        products.drop_table()  # drop product table
        self.sig_status.emit(self.__thread_id, "{}".format("Henter fra server ..."))
        # fetching datafile using http with settings
        data = httpfn.get_products(settings)
        for row in data:  # data processing
            self.__app.processEvents()
            self.sig_status.emit(self.__thread_id, "{} - {}".format(row[0], row[1]))
            products.insert(row)  # init_detail row to database
        self.sig_done.emit(self.__thread_id)

    @pyqtSlot()
    def import_reports_csv(self, employeeid, reports, filename, header):
        """
        Import reports using csv file
        :param employeeid
        :param reports:
        :param filename:
        :param header:
        :return:
        """
        filename.encode("utf8")
        self.sig_status.emit(self.__thread_id, "{}".format("Forbereder indlæsning ..."))
        reports.recreate_table()
        ftext = ">>> Import er færdig!"
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            rows = list(reader)
            # self.progress_c.rowcount.emit(len(rows))
            for line, row in enumerate(rows):
                self.__app.processEvents()
                if not len(row) == reports.csv_field_count:
                    ftext = "FEJL: Formatet i den valgte fil er ikke korrekt!"
                    break
                # self.progress_c.rowcount.emit(line)
                if header and line == 0:
                    continue
                self.sig_status.emit(self.__thread_id, "{} - {}".format(row[2].strip(), row[3].strip()))
                reports.import_csv(row, employeeid)  # send row to database

        self.sig_status.emit(self.__thread_id, "{}".format(ftext))
        self.sig_done.emit(self.__thread_id)

    @pyqtSlot()
    def import_visits_csv(self, visits, filename, header):
        """
        Import visits using csv file
        :param visits:
        :param filename:
        :param header:
        :return:
        """
        filename.encode("utf8")
        self.sig_status.emit(self.__thread_id, "{}".format("Forbereder indlæsning ..."))
        visits.recreate_table()
        ftext = ">>> Import er færdig!"
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            rows = list(reader)
            # self.progress_c.rowcount.emit(len(rows))
            for line, row in enumerate(rows):
                self.__app.processEvents()
                if not len(row) == visits.csv_field_count:
                    ftext = "FEJL: Formatet i den valgte fil er ikke korrekt!"
                    break
                # self.progress_c.rowcount.emit(line)
                if header and line == 0:
                    continue
                self.sig_status.emit(self.__thread_id, "{} - {}".format(row[2].strip(), row[3].strip()))
                visits.import_csv(row)  # send row to database

        self.sig_status.emit(self.__thread_id, "{}".format(ftext))
        self.sig_done.emit(self.__thread_id)

    @pyqtSlot()
    def import_visit_details_csv(self, details, filename, header):
        """
        Import visit details using csv file
        :param details:
        :param filename:
        :param header:
        :return:
        """
        filename.encode("utf8")
        self.sig_status.emit(self.__thread_id, "{}".format("Forbereder indlæsning ..."))
        details.recreate_table()
        ftext = ">>> Import er færdig!"
        with open(filename) as csvdata:
            reader = csv.reader(csvdata, delimiter="|")
            rows = list(reader)
            # self.progress_c.rowcount.emit(len(rows))
            for line, row in enumerate(rows):
                self.__app.processEvents()
                if not len(row) == details.csv_field_count:
                    ftext = "FEJL: Formatet i den valgte fil er ikke korrekt!"
                    break
                # self.progress_c.rowcount.emit(line)
                if header and line == 0:
                    continue
                self.sig_status.emit(self.__thread_id, "{} - {}".format(row[2].strip(), row[3].strip()))
                details.import_csv(row)  # send row to database

        self.sig_status.emit(self.__thread_id, "{}".format(ftext))
        self.sig_done.emit(self.__thread_id)

    @pyqtSlot()
    def work_demo(self):
        """
        Pretend this worker method does work that takes a long time. During this time, the thread's
        event loop is blocked, except if the application's processEvents() is called: this gives every
        thread (incl. main) a chance to process events, which in this sample means processing signals
        received from GUI (such as abort).
        """
        thread_name = QThread.currentThread().objectName()
        thread_id = int(QThread.currentThreadId())  # cast to int() is necessary
        self.sig_msg_demo.emit('Running worker #{} from thread "{}" (#{})'.format(self.__thread_id, thread_name, thread_id))

        for step in range(100):
            time.sleep(0.1)
            self.sig_step_demo.emit(self.__thread_id, 'step ' + str(step))

            # check if we need to abort the loop; need to process events to receive signals;
            self.__app.processEvents()  # this could cause change to self.__abort
            if self.__abort:
                # note that "step" value will not necessarily be same for every thread
                self.sig_msg_demo.emit('Worker #{} aborting work at step {}'.format(self.__thread_id, step))
                break

        self.sig_done_demo.emit(self.__thread_id)

    def abort_work_demo(self):
        """
        Signal to abort work
        """
        self.sig_msg_demo.emit('Worker #{} notified to abort'.format(self.__thread_id))
        self.__abort = True
