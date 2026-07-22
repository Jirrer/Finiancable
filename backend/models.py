from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
 
db:SQLAlchemy = SQLAlchemy(session_options={"expire_on_commit": False})

class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
	
    def get_id(self):
        return str(self.id)
    
class Purchase(db.Model):
    __tablename__ = "purchase"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float, nullable=False)
    info = db.Column(db.Text, nullable=True)


class Income(db.Model):
    __tablename__ = "income"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float, nullable=False)
    info = db.Column(db.Text, nullable=True)


class Transfer(db.Model):
    __tablename__ = "transfer"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float, nullable=False)
    info = db.Column(db.Text, nullable=True)

class TESTING_MODEL():
    def __init__(self):
        self.income = (
            ('Description', 'Label'),
            ('INTEREST', 'passive'),
            ('INTEREST PAYMENT RECEIVED', 'passive'),
            ('SALARY CREDITED TO ACCOUNT', 'passive'),
            ('RECURRING INTEREST PAYMENT', 'passive'),
            ('BONUS PAYMENT RECEIVED', 'passive'),
            ('DIVIDEND PAYMENT INTEREST', 'passive'),
            ('SAVINGS INTEREST CREDIT', 'passive'),
            ('LOAN REFUND CREDITED', 'passive'),
            ('REFUND FROM TAX AUTHORITIES', 'passive'),
            ('RETIREMENT ACCOUNT CONTRIBUTION', 'passive'),
            ('CREATIVE STAFFIN PAYROLL  102325', 'payroll'),
            ('EARLY PAY: HASTINGSMUTUAL PAYROLL 003034 072525', 'payroll'),
            ('PAYROLL DEPOSIT FROM HASTINGS MUTUAL', 'payroll'),
            ('DIRECT DEPOSIT FROM EMPLOYER', 'payroll'),
            ('PAYROLL CREDIT FROM HASTINGS MUTUAL 080125', 'payroll'),
            ('DIRECT DEPOSIT SALARY AUGUST 2025', 'payroll'),
            ('ACH DEPOSIT FROM EMPLOYER PAYROLL', 'payroll'),
            ('BONUS PAYMENT CREDITED TO CHECKING', 'payroll'),
            ('SALARY ADJUSTMENT POSTED 081225', 'payroll'),
            ('DIVIDEND PAYMENT RECEIVED 08/10/25', 'payroll'),
            ('PAYROLL DEPOSIT 080825 COMPANY XYZ', 'payroll'),
            ('INTEREST PAYMENT FROM SAVINGS ACCOUNT', 'payroll'),
            ('MONTHLY SALARY PAYMENT AUGUST', 'payroll'),
            ('ACH DEPOSIT FROM COMPANY PAYROLL', 'payroll'),
            ('RECURRING PAYROLL CREDIT', 'payroll'),
            ('EARLY PAYROLL DEPOSIT', 'payroll'),
            ('MONTHLY SALARY DEPOSIT', 'payroll'),
            ('PAYROLL ADJUSTMENT POSTED', 'payroll')
        )

        self.purchase = (
            ('Description', 'Label'),
            ('ctlp*great lakes muslansing             mi', 'food_drink'),
            ('buffalo wild wngs 35lansing             mi', 'food_drink'),
            ('harpers restaurant &east lansing        mi', 'food_drink'),
            ('raising canes   east lansing        mi', 'food_drink'),
            ('tst* dublin square -east lansing        mi', 'food_drink'),
            ('speedway  00004eagle               mi', 'gas'),
            ('wal-mart supercentersaint johns         mi', 'shopping'),
            ('marathon petro231803portland            mi', 'gas'),
            ('exxonmobil          westphalia          mi', 'gas'),
            ('e 2nd st 12831fowler              mi', 'misc'),
            ('south riley grocery dewitt              mi', 'food_drink'),
            ('ms. schafer\'s bar   westphalia          mi', 'food_drink'),
            ('tst* tavern  001westphalia          mi', 'food_drink'),
            ('best buy            lansing             mi', 'shopping'),
            ('sierra # 0000041lansing             mi', 'shopping'),
            ('t j maxx            lansing             mi', 'shopping'),
            ('recurring purchase at spotify', 'subscription'),
            ('pymt to netflix com - 002 netflix com los gatos ca', 'subscription'),
            ('at amazon mktpl*n42c0', 'shopping'),
            ('at dd *doordash wendy', 'food_drink'),
            ('recurring purchase at amazon prime*n49is', 'subscription'),
            ('at ctlp*great lakes m', 'food_drink'),
            ('at jimmy johns', 'food_drink'),
            ('at amazon mktpl*n461m', 'shopping'),
            ('at amazon mktpl*n41xn', 'shopping')

        )

        self.transaction = (
            ('Description', 'Label'),
            ('INTEREST', 'income'),
            ('CREATIVE STAFFIN PAYROLL  102325', 'income'),
            ('EARLY PAY: HASTINGSMUTUAL PAYROLL 003034 072525', 'income'),
            ('PAYROLL DEPOSIT FROM HASTINGS MUTUAL', 'income'),
            ('INTEREST PAYMENT RECEIVED', 'income'),
            ('SALARY CREDITED TO ACCOUNT', 'income'),
            ('DIRECT DEPOSIT FROM EMPLOYER', 'income'),
            ('PAYROLL CREDIT FROM HASTINGS MUTUAL 080125', 'income'),
            ('MOBILE PAYMENT - THANK YOU', 'transfer'),
            ('5/3 ONLINE TRANSFER TO CK:  REF ', 'transfer'),
            ('NON-5/3 CASH WITHDRAWAL FEE', 'transfer'),
            ('5/3 ONLINE TRANSFER FROM SV:  REF ', 'transfer'),
            ('WEB INITIATED PAYMENT AT AMEX EPAYMENT ACH PMT M8702 121525', 'transfer'),
            ('WEB INITIATED TRANSFER TO SAVINGS', 'transfer'),
            ('ONLINE ACH TRANSFER FROM CHECKING ACCOUNT', 'transfer'),
            ('TRANSFER TO INVESTMENT ACCOUNT VIA WEB', 'transfer'),
            ('ACH TRANSFER FROM EXTERNAL BANK', 'transfer'),
            ('ONLINE TRANSFER TO SAVINGS 080525 REF # 987654', 'transfer'),
            ('WEB TRANSFER TO INVESTMENT ACCOUNT', 'transfer'),
            ('TRANSFER FROM SAVINGS TO CHECKING VIA WEB', 'transfer'),
            ('WEB INITIATED PAYMENT AT JOHN IRRER TRUE ACH JOHN IRRER', 'transfer'),
            ('ONLINE TRANSFER FROM EXTERNAL BANK 080725', 'transfer'),
            ('ACH PAYMENT TRANSFER TO SAVINGS 080825', 'transfer'),
            ('DEBIT CARD PURCHASE AT THE MULLIKEN ROADH, MULLIKEN, MI ON 080125 FROM CARD#: ', 'purchase'),
            ('DEBIT CARD PURCHASE AT SHIELS TAVERN, HUBBARDSTON, MI ON 080125 FROM CARD#: ', 'purchase'),
            ('DEBIT CARD PURCHASE AT MS. SCHAFER\'S BAR, WESTPHALIA, MI ON 080225 FROM CARD#: ', 'purchase'),
            ('MERCHANT PAYMENT POHL OIL 1 - 730701 305 S WESTPHALIA ST WESTPHALIA MI ON 080125 FROM CARD#: ', 'purchase'),
            ('PYMT TO NETFLIX - 001000 NETFLIX.COM LOS GATOS CA', 'purchase'),
            ('DEBIT CARD PURCHASE AT TST*DUBLIN SQUARE, EAST LANSING, MI ON 082225 FROM CARD#: ', 'purchase'),
            ('DEBIT CARD PURCHASE AT DD *DOORDASH LITTL, 8559731040, CA ON 101225 FROM CARD#: ', 'purchase'),
            ('DEBIT CARD PURCHASE AT LAKE CITY TAPHOUSE, LAKE CITY, MI ON 071925 FROM CARD#: ', 'purchase'),
            ('DEBIT CARD PURCHASE AT TRUCK STOP, CADILLAC, MI ON 071925 FROM CARD#: ', 'purchase'),
            ('DEBIT CARD PURCHASE AT TASTY TREAT, LAKE CITY, MI ON 072125 FROM CARD#: ', 'purchase'),
            ('DEBIT CARD PURCHASE AT THE WILDFLOUR BAKE, CADILLAC, MI ON 071925 FROM CARD#: ', 'purchase'),
            ('DEBIT CARD PURCHASE AT HARPERS RESTAURANT, EAST LANSING, MI ON 071225 FROM CARD#: ', 'purchase'),
            ('RECURRING PURCHASE AT AMAZON PRIME*2A212, SEATTLE, WA ON 122525 FROM CARD#: ', 'purchase'),
            ('BEST BUY            LANSING             MI', 'purchase'),
            ('WAL-MART SUPERCENTERSAINT JOHNS         MI', 'purchase'),
            ('CTLP*GREAT LAKES MUSLANSING             MI', 'purchase')
        )    