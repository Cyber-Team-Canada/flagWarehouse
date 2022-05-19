import logging
import time
from datetime import datetime, timedelta
from queue import Queue
import json
import socket
from typing import List

import requests
from flask import Flask, current_app
from ordered_set import OrderedSet

from . import db


class OrderedSetQueue(Queue):
    """Unique queue.

    Elements cannot be repeated, so there's no need to traverse it to check.
    LIFO ordered and thread-safe.
    """

    def _init(self, maxsize):
        self.queue = OrderedSet()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()


def http_submit(flags: List[str], cursor, i, logger):
    res = requests.put(current_app.config['SUB_URL'],
                        headers={'X-Team-Token': current_app.config['TEAM_TOKEN']},
                        json=flags,
                        timeout=(current_app.config['SUB_INTERVAL'] / current_app.config['SUB_LIMIT']))
    j_res = []

    # Check if the gameserver sent a response about the flags or if it sent an error
    if res.headers['Content-Type'] == 'application/json; charset=utf-8':
        j_res = json.loads(res.text)
    else:
        logger.error(f'Received this response from the gameserver:\n\n{res.text}\n')
        return False, i

    # executemany() would be better, but it's fine like this.
    for item in j_res:
        if (current_app.config['SUB_INVALID'].lower() in item['msg'].lower() or
                current_app.config['SUB_YOUR_OWN'].lower() in item['msg'].lower() or
                current_app.config['SUB_STOLEN'].lower() in item['msg'].lower() or
                current_app.config['SUB_NOP'].lower() in item['msg'].lower()):
            cursor.execute('''
            UPDATE flags
            SET status = ?, server_response = ?
            WHERE flag = ?
            ''', (current_app.config['DB_SUB'], current_app.config['DB_ERR'], item['flag']))
        elif current_app.config['SUB_OLD'].lower() in item['msg'].lower():
            cursor.execute('''
            UPDATE flags
            SET status = ?, server_response = ?
            WHERE flag = ?
            ''', (current_app.config['DB_SUB'], current_app.config['DB_EXP'], item['flag']))
        elif current_app.config['SUB_ACCEPTED'].lower() in item['msg'].lower():
            cursor.execute('''
            UPDATE flags
            SET status = ?, server_response = ?
            WHERE flag = ?
            ''', (current_app.config['DB_SUB'], current_app.config['DB_SUCC'], item['flag']))
        i += 1
    return True, i


def tcp_submit(flags: List[str], cursor, i, logger):
    for flag in flags:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(current_app.config['SUB_INTERVAL'] / current_app.config['SUB_LIMIT'])
                s.connect((current_app.config['SUB_HOST'], current_app.config['SUB_PORT']))
                s.sendall(bytearray(flag, "utf-8") + b"\n")
                response = s.recv(1024).decode()
                logger.info(f"{flag}: {response}")
                if (current_app.config['SUB_INVALID'].lower() in response.lower() or
                        current_app.config['SUB_YOUR_OWN'].lower() in response.lower() or
                        current_app.config['SUB_STOLEN'].lower() in response.lower() or
                        current_app.config['SUB_NOP'].lower() in response.lower()):
                    cursor.execute('''
                    UPDATE flags
                    SET status = ?, server_response = ?
                    WHERE flag = ?
                    ''', (current_app.config['DB_SUB'], current_app.config['DB_ERR'], flag))
                elif current_app.config['SUB_OLD'].lower() in response.lower():
                    cursor.execute('''
                    UPDATE flags
                    SET status = ?, server_response = ?
                    WHERE flag = ?
                    ''', (current_app.config['DB_SUB'], current_app.config['DB_EXP'], flag))
                elif current_app.config['SUB_ACCEPTED'].lower() in response.lower():
                    cursor.execute('''
                    UPDATE flags
                    SET status = ?, server_response = ?
                    WHERE flag = ?
                    ''', (current_app.config['DB_SUB'], current_app.config['DB_SUCC'], flag))
                i += 1
        except:
            return False, i
    return True, i


def loop(app: Flask):
    with app.app_context():
        logger = current_app.logger  # Need to get it before sleep, otherwise it doesn't work. Don't know why.
        # Let's not make it start right away
        time.sleep(5)
        logger.info('starting.')
        database = db.get_db()
        queue = OrderedSetQueue()
        while True:
            s_time = time.time()
            expiration_time = (datetime.now() - timedelta(seconds=current_app.config['FLAG_ALIVE'])).replace(microsecond=0).isoformat(sep=' ')
            cursor = database.cursor()
            cursor.execute('''
            SELECT flag
            FROM flags
            WHERE time > ? AND status = ? AND server_response IS NULL
            ORDER BY time DESC 
            ''', (expiration_time, current_app.config['DB_NSUB']))
            for flag in cursor.fetchall():
                queue.put(flag[0])
            i = 0
            queue_length = queue.qsize()
            try:
                # Send N requests per interval
                while i < min(current_app.config['SUB_LIMIT'], queue_length):
                    # Send N flags per request
                    flags = []
                    for _ in range(min(current_app.config['SUB_PAYLOAD_SIZE'], queue_length)):
                        flags.append(queue.get())
                    if current_app.config['SUB_USE_HTTP']:
                        (success, i) = http_submit(flags, cursor, i, logger)
                    else:
                        (success, i) = tcp_submit(flags, cursor, i, logger)
                    if not success:
                        continue
            except requests.exceptions.RequestException:
                logger.error('Could not send the flags to the server, retrying...')
            finally:
                # At the end, update status as EXPIRED for flags not sent because too old
                cursor.execute('''
                                    UPDATE flags
                                    SET server_response = ?
                                    WHERE status LIKE 'NOT_SUBMITTED' AND time <= ?
                                    ''', (current_app.config['DB_EXP'], expiration_time))
                database.commit()
                duration = time.time() - s_time
                if duration < current_app.config['SUB_INTERVAL']:
                    time.sleep(current_app.config['SUB_INTERVAL'] - duration)
