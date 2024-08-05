import json
import sys 
import threading
from confluent_kafka import Consumer
from confluent_kafka import KafkaError
from confluent_kafka import KafkaException
from core.models import *


def set_balances(user):
    # set user balance
    user.ton_balance = 0
    user.goy_balance = 1
    user.save()

    # - при оплате 1 тон начисляем 1 гой и 0 тон
    # - за каждого приглашенного гоя начисляем 0.5 тон и 1 гой
    # - за гоя гоя начисляем 0.25 тон и 0.5 гоя

    # set refs balances
    try: 
        ref_user = user.who_invited
        ref_user.ton_balance = ref_user.ton_balance + 0.5
        ref_user.goy_balance = ref_user.goy_balance + 1
        ref_user.save()
    except:
        pass

    # set super_refs balances
    try: 
        super_ref_user = ref_user.who_invited
        super_ref_user.ton_balance = super_ref_user.ton_balance + 0.25
        super_ref_user.goy_balance = super_ref_user.goy_balance + 0.5
        super_ref_user.save()
    except:
        pass


running=True
conf = {
    'bootstrap.servers': "89.111.155.161:9092",
    'auto.offset.reset': 'smallest',
    'group.id': "1",
    'api.version.request': False,
    'socket.timeout.ms': 60000,
    'session.timeout.ms': 6000
}
topic='user-payments'

class UserCreatedListener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.consumer = Consumer(conf)
        
    def run(self):
        print ('Created Listener')
        try:
            self.consumer.subscribe([topic])
            while running:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
                else:
                    print('---------> Got message')
                    message = json.loads(msg.value().decode('utf-8'))
                    print(message)
                    
                    ton_amount = float(message['tonAmount'])
                    sender_adress = message['senderAddress']
                    tg_user_id = int(message['messageText'])

                    user = None
                    try:
                        user = User.objects.get(tg_user_id=tg_user_id)
                    except:
                        pass

                    if user is None:
                        continue

                    if user.has_paid:
                        continue

                    if ton_amount >= 1:
                        set_balances(user)
                        user.wallet_address = sender_adress
                        user.has_paid = True
                        user.save()

        finally:
            self.consumer.close()