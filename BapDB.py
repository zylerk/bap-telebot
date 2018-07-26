# coding: utf-8

import os
import datetime
import MySQLdb

from base import BaseClass

class DB(BaseClass):
    # These environment variables are configured in app.yaml.
    CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
    CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
    CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.last_time = 0
        super(DB, self).__init__()

    def close(self):
        if self.conn is not 0:
            self.conn.close()
        return

    def connect(self):
        try:
            # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
            # will be set to 'Google App Engine/version'.
            if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
                # Connect using the unix socket located at
                # /cloudsql/cloudsql-connection-name.
                cloudsql_unix_socket = os.path.join(
                    '/cloudsql', DB.CLOUDSQL_CONNECTION_NAME)

                self.conn = MySQLdb.connect(
                    unix_socket=cloudsql_unix_socket,
                    user=DB.CLOUDSQL_USER,
                    passwd=DB.CLOUDSQL_PASSWORD)

                self.cursor = self.conn.cursor()

            # If the unix socket is unavailable, then try to connect using TCP. This
            # will work if you're running a local MySQL server or using the Cloud SQL
            # proxy, for example:
            #
            #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
            #
            else:
                self.conn = MySQLdb.connect(host='127.0.0.1', user=DB.CLOUDSQL_USER, passwd=DB.CLOUDSQL_PASSWORD)
                self.cursor = self.conn.cursor()
        except:
            return self.error('connection error')

        return self.ok()

    def check_open(self):
        if self.conn is None:
            return False
        elif self.conn.open:
            return True
        else:
            return False


class BapDB(DB):
    def __init__(self):
        super(BapDB, self).__init__()

    def getInfo(self, vfx):

        if self.check_open() is False:
            self.connect()

        try:

            cursor = self.cursor
            current_spread = 0.0

            q_str = 'select Time, {0}_bittrex_usd, {0}_bithumb_usd, fx_usdkrw,{0}_gap_bittrex_bithumb, {0}_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1'.format(vfx)
            cursor.execute(q_str)
            rows = cursor.fetchall()
            result = ""
            for r in rows:
                time_seoul = r[0] + datetime.timedelta(hours=9)
                r_str = u'서울시간={v_time}\n비트렉스={v_bittrex:,.0f}\n빗섬={v_bithumb:,.0f} ({v_bithumb_krw:,.0f})\n갭={v_gap:,.0f}  스프레드={v_spread:.1f}%' \
                    .format(v_time=time_seoul, v_bittrex=r[1], v_bithumb=r[2], v_bithumb_krw=r[2] * r[3], v_gap=r[4], v_spread=r[5] * 100)
                current_spread = r[5]
                result += r_str + '\n'

            q_str = 'select min({0}_spread_bittrex_bithumb), avg({0}_spread_bittrex_bithumb), max({0}_spread_bittrex_bithumb) from bap.Price  where Time > adddate(CURRENT_DATE, -7)'.format(vfx)

            cursor.execute(q_str)
            rows = cursor.fetchall()
            for r in rows:
                r_str = u'최근7일 스프레드 동향\n최소={v_min:,.1f}% / 평균={v_avg:,.1f}% / 최대={v_max:,.1f}% : 현재={v_current:,.1f}% ' \
                    .format(v_min=r[0] * 100, v_avg=r[1] * 100, v_max=r[2] * 100, v_current=current_spread * 100)
                result += r_str + '\n'

            cursor.execute('select count(Time) from bap.Price  where Time > adddate(CURRENT_DATE, -7)')
            row_total = cursor.fetchone()

            q_str = 'select count(Time) from bap.Price  where Time > adddate(CURRENT_DATE, -7) and {v_vfx}_spread_bittrex_bithumb >= {v_spread}'\
                .format(v_vfx = vfx, v_spread=current_spread)

            cursor.execute(q_str)
            row_current = cursor.fetchone()

            where_percent = float(row_current[0]) / float(row_total[0])
            result += u'{0:.0f}% 구간에 위치'.format(where_percent * 100) + '\n'

        except Exception as e:
            return DB.STATE_ERROR, 'error getInfo {0}'.format(e.__str__())

        return 1, result

    def getAll(self):
        if self.check_open() is False:
            self.connect()

        cursor = self.cursor
        res = {}
        cursor.execute(
            'select Time, xrp_bittrex_usd, xrp_bithumb_usd, fx_usdkrw, xrp_gap_bittrex_bithumb, xrp_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1')
        res['XRP'] = cursor.fetchall()
        cursor.execute(
            'select Time, eth_bittrex_usd, eth_bithumb_usd, fx_usdkrw, eth_gap_bittrex_bithumb, eth_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1')
        res['ETH'] = cursor.fetchall()
        cursor.execute(
            'select Time, btc_bittrex_usd, btc_bithumb_usd, fx_usdkrw,btc_gap_bittrex_bithumb, btc_spread_bittrex_bithumb  from bap.Price order by Time desc limit 1')
        res['BTC'] = cursor.fetchall()

        time_seoul = res['BTC'][0][0] + datetime.timedelta(hours=9)
        r_str = u'서울시간={0}\n'.format(time_seoul)

        def makeResult(vfx):
            str = vfx + '> '
            if vfx is 'XRP':
                str += u'{v_bittrex:,.3f} ({v_bithumb_krw:,.0f}) {v_spread:.1f}%\n' \
                    .format(v_bittrex=res[vfx][0][1], v_bithumb_krw=res[vfx][0][2] * res[vfx][0][3],
                            v_spread=res[vfx][0][5] * 100)
            else:
                str += u'{v_bittrex:,.0f} ({v_bithumb_krw:,.0f}) {v_spread:.1f}%\n' \
                    .format(v_bittrex=res[vfx][0][1], v_bithumb_krw=res[vfx][0][2] * res[vfx][0][3],
                            v_spread=res[vfx][0][5] * 100)
            return str

        r_str += makeResult('BTC')
        r_str += makeResult('ETH')
        r_str += makeResult('XRP')

        diff_spread = u'BTC기준 상대스프레드 ETH={0:.1f}% XRP={1:.1f}%'.format(
            (res['ETH'][0][5] - res['BTC'][0][5]) * 100, (res['XRP'][0][5] - res['BTC'][0][5]) * 100)

        r_str += diff_spread

        # r_str = u'서울시간={v_time}\nBTC={v_btc:,.0f} ({v_btc_krw:,.0f} {v_spread:.1f}%\n'\
        #     .format(v_time=time_seoul, v_btc= res['BTC'][1], v_btc_krw= res['BTC'][2]*res['BTC'][3], v_spread=r[2]*r[3],v_spread=r[5]*100)

        return 1, r_str



