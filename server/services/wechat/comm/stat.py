# coding=utf-8
from __future__ import absolute_import

import datetime
import json

from ..core import WeChatAccess, WeChatError


class WeChatCommStatAPI(WeChatAccess):
    PREFIX_STAT_SUBSCRIBES = 'WECHAT_API:STAT_SUBSCRIBES/'

    @property
    def key_stat_subscribes(self):
        return '{}{}'.format(self.PREFIX_STAT_SUBSCRIBES, self.app_id)

    def summary_subscribers(self, begin_date, end_date):
        path = '/datacube/getusersummary'
        data = {
            'begin_date': str(begin_date),
            'end_date': str(end_date)
        }
        data = self._request('POST', path, data=data)
        return data.get('list') or []

    def cumulate_subscribers(self, begin_date, end_date):
        path = '/datacube/getusercumulate'
        data = {
            'begin_date': str(begin_date),
            'end_date': str(end_date)
        }
        data = self._request('POST', path, data=data)
        return data.get('list') or []

    def statistics(self, refresh=False):
        if not self.app_id or not self.app_secret:
            raise WeChatError.OPError('none app_id or app_secret')
        today = datetime.date.today()
        key = '{}/{}'.format(self.key_stat_subscribes,
                             today.strftime('%Y-%m-%d'))
        stat_data = self.redis_read.get(key)
        if stat_data and not refresh:
            try:
                return dict(json.loads(stat_data))
            except Exception:
                pass

        end_date = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        begin_date = (today - datetime.timedelta(days=7)).strftime('%Y-%m-%d')

        cumulate = self.cumulate_subscribers(end_date, end_date)  # one day.

        last = cumulate[-1] if cumulate else {}
        total_followers = last.get('cumulate_user', 0)

        summaries = self.summary_subscribers(begin_date, end_date)
        added = 0
        cancelled = 0

        for s in summaries:
            added += s.get('new_user') or 0
            cancelled += s.get('cancel_user') or 0

        growth = added - cancelled

        output = {
            'followers': total_followers,
            'growth': growth,
            'added': added,
            'cancelled': cancelled
        }
        self.redis_write.setex(key, json.dumps(output), 3600 * 24)
        return output
