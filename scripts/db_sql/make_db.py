# -*- coding: utf-8 -*-
from initialize import engine
import datetime as dt
from sqlalchemy import Column, Integer, Float, String, DateTime,\
    Boolean, Date,\
    Text, CheckConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), index=True)
    gender = Column(Boolean, nullable=False)
    birthdate = Column(Date, nullable=False)
    address = Column(Text, default="")
    past_history = Column(Text, default="")
    visits = relationship(
        "Visit", back_populates="patient", order_by='Visit.id',
        lazy='dynamic', cascade="all, delete-orphan")


class Visit(Base):
    __tablename__ = 'visits'

    id = Column(Integer, primary_key=True)
    exam_date = Column(DateTime, default=dt.datetime.now,
                       onupdate=dt.datetime.now)
    note = Column(Text)
    diag = Column(String(50), nullable=False)
    weight = Column(Float, default=0)
    days = Column(Integer, default=2)
    followup = Column(Text, default='')
    bill = Column(Integer, default=0)
    patient_id = Column(ForeignKey('patients.id'))
    patient = relationship("Patient", back_populates='visits')
    linedrugs = relationship(
        "LineDrug", lazy='selectin', cascade="all, delete-orphan")


class DrugWarehouse(Base):
    __tablename__ = 'drugwarehouse'
    __table_args__ = (CheckConstraint("quantity >= 0"),
                      CheckConstraint("sale_price >= 0"))

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)
    quantity = Column(Integer, default=0)
    usage_unit = Column(String(10), default='viên')  # ml
    sale_unit = Column(String(10), default='viên')  # chai
    purchase_price = Column(Integer, default=0)  # gia mua vo
    sale_price = Column(Integer, default=0)  # gia chai
    usage = Column(String(50), default='uống')  # cach dung


class LineDrug(Base):
    __tablename__ = 'linedrugs'
    __table_args__ = (CheckConstraint("quantity >= 0"),
                      CheckConstraint("times >= 0"),
                      CheckConstraint("dosage_per >= 0"))

    id = Column(Integer, primary_key=True)
    drug_id = Column(ForeignKey("drugwarehouse.id"))
    dosage_per = Column(String(5), default=0)
    times = Column(Integer, default=0)
    quantity = Column(Integer, default=0)
    usage = Column(String(20), default='uống')
    visit_id = Column(ForeignKey("visits.id"))
    drug = relationship('DrugWarehouse', lazy='selectin')


class SamplePrescription(Base):
    __tablename__ = "sampleprescription"
    __table_args__ = (CheckConstraint("name != ''"),)

    id = Column(Integer, primary_key=True)
    name = Column(String(50), default='test', nullable=False)
    samplelinedrugs = relationship(
        "SampleLineDrug", lazy="selectin", cascade="all, delete-orphan")


class SampleLineDrug(Base):
    __tablename__ = "samplelinedrugs"
    __table_args__ = (CheckConstraint("times >= 0"),
                      CheckConstraint("dosage_per >= 0"))

    id = Column(Integer, primary_key=True)
    drug_id = Column(ForeignKey("drugwarehouse.id"))
    times = Column(Integer, default=0)
    dosage_per = Column(String(5), default=0)
    sampleprescription_id = Column(ForeignKey("sampleprescription.id"))
    drug = relationship('DrugWarehouse', lazy='selectin')


def make_db():
    Base.metadata.create_all(engine)
