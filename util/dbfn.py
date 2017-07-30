#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Frede Hundewadt <f@hundewadt.dk>
# Copyright: Frede Hundewadt <fh@uex.dk>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Sqlite database functions"""

import sqlite3
from configuration import config


def create_tables():
    """Wrapper for creating all tables"""
    for table in config.TABLES:
        create_table(table)


def create_table(tablename):
    """Create table wrapper
    :param tablename:
    """
    if tablename == "contact":
        create_table_contacts()
        return True
    if tablename == "customer":
        create_table_customers()
        return True
    if tablename == "employee":
        create_table_employees()
        return True
    if tablename == "visit":
        create_table_visits()
        return True
    if tablename == "orderline":
        create_table_orderlines()
        return True
    if tablename == "product":
        create_table_product()
        return True
    if tablename == "report":
        create_table_reports()
        return True
    if tablename == "settings":
        create_table_settings()
        return True
    return False


def create_table_contacts():
    """Create contact table"""
    sql = "CREATE TABLE IF NOT EXISTS contact (" \
          "contactid INTEGER PRIMARY KEY NOT NULL, " \
          "customerid INTEGER, name TEXT, department TEXT, email TEXT, phone TEXT, infotext TEXT);"

    db = sqlite3.connect(config.DBPATH)
    with db:
        db.execute(sql)

    db.commit()


def create_table_customers():
    """Create customer table"""
    # row: |0  |1   |2   |3   |4       |5      |6    |7      |8    |9    |10 |11   |12 |13 |14 |15  |16 |17   |19
    # old:  acc comp add1 add2 zipcity  country s_rep phone1  vat
    # new:  acc comp add1 add2 zipcity  country s_rep phone1  vat   email att phon2
    # csv:  id  acc  comp add1 add2     zipcode city  country s_rep phon1 vat email del mod cre info
    # db :  id  acc  comp add1 add2     zipcode city  country s_rep phon1 vat email del mod cre info att phon2 factor
    sql = "CREATE TABLE IF NOT EXISTS customer (" \
          "customerid INTEGER PRIMARY KEY NOT NULL, " \
          "account TEXT, company TEXT, address1 TEXT, address2 TEXT, zipcode TEXT, city TEXT, country TEXT, " \
          "salesrep TEXT, phone1 TEXT, vat TEXT, email TEXT, deleted INTEGER, modified INTEGER, created TEXT, " \
          "infotext TEXT, att TEXT, phone2 TEXT, factor REAL);"

    db = sqlite3.connect(config.DBPATH)
    with db:
        db.execute(sql)


def create_table_employees():
    """Create employee table"""
    sql = "CREATE TABLE IF NOT EXISTS employee (" \
          "employeeid INTEGER PRIMARY KEY NOT NULL, " \
          "salesrep TEXT, fullname TEXT, email TEXT, country TEXT, sas INT);"
    db = sqlite3.connect(config.DBPATH)
    with db:
        db.execute(sql)

    db.commit()


def create_table_orderlines():
    """Create orderline table"""
    sql = "CREATE TABLE IF NOT EXISTS orderline (" \
          "lineid INTEGER PRIMARY KEY NOT NULL, orderid INTEGER, pcs INTEGER, " \
          "sku TEXT, infotext TEXT, price REAL, " \
          "sas INTEGER, discount REAL);"
    conn = sqlite3.connect(config.DBPATH)
    with conn:
        conn.execute(sql)

    conn.commit()


def create_table_visits():
    """Create visit table"""
    statement = "CREATE TABLE IF NOT EXISTS visit (" \
                "visitid INTEGER PRIMARY KEY NOT NULL, " \
                "reportid INTEGER, employeeid INTEGER, customerid INTEGER, podate TEXT, " \
                "posent INTEGER, pocontact TEXT, ponum TEXT, pocompany TEXT, poaddress1 TEXT, " \
                "poaddress2 TEXT, pozipcode TEXT, pocity TEXT, pocountry TEXT, infotext TEXT, " \
                "proddemo TEXT, prodsale TEXT, ordertype TEXT, turnsas REAL, turnsale REAL, " \
                "turntotal REAL, approved INT);"
    db = sqlite3.connect(config.DBPATH)
    with db:
        db.execute(statement)
    db.commit()


def create_table_product():
    """Create product table"""
    sql = "CREATE TABLE IF NOT EXISTS product (" \
          "sku TEXT, name1 TEXT, name2 TEXT, name3 TEXT, item TEXT, " \
          "price REAL, d2 REAL, d4 REAL, d6 REAL, d8 REAL, d12 REAL, " \
          "d24 REAL, d48 REAL, d96 REAL, min REAL, net REAL, groupid TEXT);"
    db = sqlite3.connect(config.DBPATH)
    with db:
        db.execute(sql)

    db.commit()


def create_table_reports():
    """Create report table"""
    sql = "CREATE TABLE IF NOT EXISTS report (" \
          "reportid INTEGER PRIMARY KEY NOT NULL, employeeid INTEGER, repno INTEGER, repdate TEXT, " \
          "newvisitday INTEGER, newdemoday INTEGER, newsaleday INTEGER, newturnoverday REAL, " \
          "recallvisitday INTEGER, recalldemoday INTEGER, recallsaleday INTEGER, recallturnoverday REAL, " \
          "sasday INTEGER, sasturnoverday REAL, demoday INTEGER, saleday INTEGER, " \
          "kmmorning INTEGER, kmevening INTEGER, supervisor TEXT, territory TEXT, workday INTEGER, " \
          "infotext TEXT, sent INTEGER, offday INTEGER, offtext TEXT, kmprivate INT);"
    db = sqlite3.connect(config.DBPATH)
    with db:
        db.execute(sql)

    db.commit()


def create_table_settings():
    """Create app settings table"""
    sql = "CREATE TABLE IF NOT EXISTS settings (" \
          "usermail TEXT, userpass TEXT, usercountry TEXT, pd TEXT, pf TEXT, sf TEXT, " \
          "http TEXT, smtp TEXT, port INTEGER, mailto TEXT, " \
          "mailserver TEXT, mailport TEXT, mailuser TEXT, mailpass TEXT, " \
          "fc TEXT, fp TEXT, fe TEXT, lsc TEXT, lsp TEXT, sac TEXT, sap TEXT);"

    db = sqlite3.connect(config.DBPATH)
    with db:
        db.execute(sql)

    db.commit()


def drop_table(tablename):
    """Drop table wrapper
    :param tablename:
    """
    conn = sqlite3.connect(config.DBPATH)
    with conn:
        statement = "drop table if exists {}".format(tablename)
        conn.execute(statement)

    conn.commit()


def exist_table(tablename):
    """Check database if tablename exist
    :param tablename:
    """
    statement = "select name from sqlite_master " \
                "where type='{}' and name='{}';".format("table", tablename)
    conn = sqlite3.connect(config.DBPATH)
    with conn:
        cur = conn.cursor()
        cur.execute(statement)
        t = cur.fetchone()
        if t:
            return True
    return False


def recreate_table(table):
    """Recreate table
    :param table: tablename
    """
    drop_table(table)
    create_table(table)
