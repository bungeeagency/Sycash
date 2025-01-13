import easy_db
import time
from datetime import datetime

db = easy_db.DataBase('SyDB.db')
EVENT_TYPES={0: 'money_sent', 1: 'money_received', 2: 'infos_changed', 3: 'new_user', 4: 'user_login', 5: 'user_failed_otp', 6: 'user_deposit', 7: 'user_withdraw_call'}

def _timestamp(delay=0):
    return int(time.time())+delay*60*60

def create_db():
    
    db.create_table('users',{"tag":str,"mail":str,"balance":int,"paypal":str,"iban":str,"btc_addr":str,"verified":bool})
    db.create_table('events', {"type":str,"caller":str,"date":str,"event":str})

def get_user(tag):
    infos=db.pull_where('users', "tag='"+tag+"'")
    return infos

def exist(tag):
    infos=db.pull_where('users', "tag='"+tag+"'")
    if len(infos)==0:
        return False
    return True

def mail_used(mail):
    infos=db.pull_where('users', "mail='"+mail+"'")
    print(type(infos))
    print(len(infos))
    print(infos)
    if not infos:
        return False
    return True

def add_to_bal(tag,amount):
    nb=amount+float(get_user_bal(tag))
    db.update('users', 'tag', tag, 'balance', nb)
    print('Successfully added '+str(amount)+" EU to "+tag+" balance.")

def ret_to_bal(tag,amount):
    nb=float(get_user_bal(tag))-amount
    db.update('users', 'tag', tag, 'balance', nb)
    print('Successfully retired '+str(amount)+" EU to "+tag+" balance.")

def get_user_bal(tag):
    infos=db.pull_where('users', "tag='"+tag+"'")
    return infos[0]["balance"]

def create_user(tag,mail):
    db.append('users',{"tag":tag,"mail":mail,"balance":0})

def verify(tag):
    db.update('users', 'tag', tag, 'verified', True)

def get_verif_state(tag):
    infos=db.pull_where('users', "tag='"+tag+"'")
    return infos[0]["verified"]

def update_winfos(tag,ppl,bank,btc):
    db.update('users', 'tag', tag, 'paypal', ppl)
    db.update('users', 'tag', tag, 'iban', bank)
    db.update('users', 'tag', tag, 'btc_addr', btc)

def get(tag):
    try:
        return db.pull_where('users', "tag='"+tag+"'")[0]
    except:
        return False

def valid_session(tag):
    infos=get(tag)
    if infos['timestamp']==None:
        return False
    elif int(float(infos["timestamp"]))<time.time():
        return False
    return True

def set_session(tag,delay):
    db.update('users', 'tag', tag, 'timestamp', _timestamp(delay))

def log(event_type,caller,event):
    type=EVENT_TYPES[event_type]
    db.append("events",{"type":type,"caller":caller,"date":datetime.now(),"event":event})

def change_mail(tag,new):
    db.update('users', 'tag', tag, 'mail', new)
