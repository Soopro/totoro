# coding=utf-8
from __future__ import absolute_import

import datetime
import json

from ..core import WeChatAccess, WeChatError


class WeChatMinaStatAPI(WeChatAccess):
    PREFIX_STAT_SUBSCRIBES = 'WECHAT_API:STAT_MINI/'

    @property
    def key_stat_mini(self):
        return '{}{}'.format(self.PREFIX_STAT_SUBSCRIBES, self.app_id)

    def _get_month_range(self, month=None, year=None, format=None):
        if not year or not month:
            datenow = datetime.datetime.now() - datetime.timedelta(days=31)
            if not year:
                year = datenow.year
            if not month:
                month = datenow.month
        start_day = datetime.date(year, month, 1)
        next_month = start_day.replace(day=28) + datetime.timedelta(days=4)
        end_day = next_month - datetime.timedelta(days=next_month.day)
        if isinstance(format, basestring):
            return (start_day.strftime(format), end_day.strftime(format))
        else:
            return (start_day, end_day)

    def _get_last_day(self, format=None):
        last_day = datetime.date.today() - datetime.timedelta(days=2)
        # take before 2 days, incase just cross a day, ex. 00:10 am.
        # otherwise the stupid remote api will return error.
        if isinstance(format, basestring):
            return last_day.strftime(format)
        else:
            return last_day

    def daily_summary_trend(self, date_str=None):
        path = '/datacube/getweanalysisappiddailysummarytrend'
        if not date_str:
            date_str = self._get_last_day('%Y%m%d')
        data = {
            'begin_date': str(date_str),
            'end_date': str(date_str)
        }
        res = self._request('POST', path, data=data)
        return res.get('list', [])[-1] or {}

    def daily_visit_trend(self, date_str=None):
        path = '/datacube/getweanalysisappiddailyvisittrend'
        if not date_str:
            date_str = self._get_last_day('%Y%m%d')
        data = {
            'begin_date': str(date_str),
            'end_date': str(date_str)
        }
        res = self._request('POST', path, data=data)
        return res.get('list', [])[-1] or {}

    def monthly_visit_trend(self, month=None, year=None):
        path = '/datacube/getweanalysisappidmonthlyvisittrend'
        begin_date, end_date = self._get_month_range(month=month,
                                                     year=year,
                                                     format='%Y%m%d')
        data = {
            'begin_date': str(begin_date),
            'end_date': str(end_date)
        }
        res = self._request('POST', path, data=data)
        return res.get('list', [])[-1] or {}

    def statistics(self, refresh=False):
        if not self.app_id or not self.app_secret:
            raise WeChatError.OPError('none app_id or app_secret')
        today = datetime.date.today()
        key = '{}/{}'.format(self.key_stat_mini, today.strftime('%Y-%m-%d'))
        stat_data = self.redis_read.get(key)
        if stat_data and not refresh:
            try:
                return dict(json.loads(stat_data))
            except Exception:
                pass

        daily_summary = self.daily_summary_trend()
        total_visits = daily_summary.get('visit_total', 0)

        monthly_trend = self.monthly_visit_trend()
        added = monthly_trend.get('visit_uv_new', 0)
        uv = monthly_trend.get('visit_uv', 0)
        pv = monthly_trend.get('visit_pv', 0)
        stay_time = monthly_trend.get('stay_time_session', 0)

        output = {
            'visits': total_visits,
            'growth': added,
            'stay_time': stay_time,
            'uv': uv,
            'pv': pv,
        }
        self.redis_write.setex(key, json.dumps(output), 3600 * 24)
        return output
