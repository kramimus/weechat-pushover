# -*- coding: utf-8 -*-
#
# Author: Caspar Clemens Mierau <ccm@screenage.de>
# Homepage: https://github.com/leitmedium/weechat-pushover
# Derived from: notifo
#   Author: ochameau <poirot.alex AT gmail DOT com>
#   Homepage: https://github.com/ochameau/weechat-notifo
# An from: notify
#   Author: lavaramano <lavaramano AT gmail DOT com>
#   Improved by: BaSh - <bash.lnx AT gmail DOT com>
#   Ported to Weechat 0.3.0 by: Sharn - <sharntehnub AT gmail DOT com)
# And from: notifo_notify
#   Author: SAEKI Yoshiyasu <laclef_yoshiyasu@yahoo.co.jp>
#   Homepage: http://bitbucket.org/laclefyoshi/weechat/
#
# This plugin sends push notifications to your iPhone or Android smartphone
# by using pushover.net. In order to use it, please follow these steps:
#
# 1. Register an account at http://pushover.net
# 2. Create a new application at https://pushover.net/apps/build
# 3. Note the "token" for your new application (referenced as TOKEN later on)
# 4. From the Dashboard at https://pushover.net note your "User key" (referenced as USERKEY later on)
# 5. Install the pushover app on your iPhone/Android and login
# 6. put "pushover.py" to ~/.weechat/python
# 7. start the plugin with "/python load pushover.py"
# 8. Set user key and token by doing
# 9. /set plugins.var.python.pushover.user USERKEY
# 10. /set plugins.var.python.pushover.token TOKEN
#
# On security: This plugin does not use end-to-end-encryption. Please see
# the security related FAQ at pushover.net for details
#
# Requires Weechat 0.3.0, curl
# Released under GNU GPL v2, see LICENSE file for details
#
# 2012-10-26, au <poirot.alex@gmail.com>:
#     version 0.1: merge notify.py and notifo_notify.py in order to avoid
#                  sending notifications when channel or private buffer is
#                  already opened
# 2013-06-27, au <ccm@screenage.de>:
#     version 0.2: replace blocking curl call
# 2013-09-10, au <matt.dickoff@gmail.com>:
#     version 0.3: added custom pushover sound support, enable plugin on/off,
#                  turn highlights/private message on/off, various formatting


import weechat
import string
import os
import urllib
import urllib2


default_settings = {
    "user": ("", "User/Group key"),
    "token": ("", "API token/key"),
    "sound": ("", "Notification sound (blank for default).  See pushover website for sound options."),
    "enabled": ("on", "Turn plugin on/off"),
    "show_highlight": ("on", "Send notification on highlight"),
    "show_priv_msg": ("on", "Send notification on private message")
}

required_settings = {
    "user",
    "token"
}


def init_settings():
    # Setup default options for pushover
    for option, (default, desc) in default_settings.iteritems():
        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, default)
            weechat.config_set_desc_plugin(option, desc)
    for option in required_settings:
        if weechat.config_get_plugin(option) == "":
            weechat.prnt("", "pushover: Please set option: %s" % option)
            weechat.prnt("", "pushover: /set plugins.var.python.pushover.%s STRING" % option)


def notify_show(data, bufferp, uber_empty, tagsn, isdisplayed,
                ishighlight, prefix, message):

    if weechat.config_get_plugin("enabled") == "off":
        return weechat.WEECHAT_RC_OK

    # get local nick for buffer
    mynick = weechat.buffer_get_string(bufferp, "localvar_nick")

    # only notify if the message was not sent by myself
    if (weechat.buffer_get_string(bufferp, "localvar_type") == "private" and 
        prefix != mynick and 
        weechat.config_get_plugin("show_priv_msg") == "on"):
        
        show_notification(prefix, prefix, message)

    elif ishighlight == "1" and weechat.config_get_plugin("show_highlight") == "on":
        buf = (weechat.buffer_get_string(bufferp, "short_name") or
               weechat.buffer_get_string(bufferp, "name"))
        show_notification(buf, prefix, message)

    return weechat.WEECHAT_RC_OK


def show_notification(chan, nick, message):
    PUSHOVER_USER = weechat.config_get_plugin("user")
    PUSHOVER_API_SECRET = weechat.config_get_plugin("token")
    PUSHOVER_SOUND = weechat.config_get_plugin("sound")
    if PUSHOVER_USER != "" and PUSHOVER_API_SECRET != "":
        url = "https://api.pushover.net/1/messages.json"
        message = '<' + nick + '> ' + message
        postdata = urllib.urlencode({'token': PUSHOVER_API_SECRET,
                                     'user': PUSHOVER_USER,
                                     'message': message,
                                     'title': 'weechat: ' + chan,
                                     'sound': PUSHOVER_SOUND})
        version = weechat.info_get("version_number", "") or 0
        # use weechat.hook_process_hashtable only with weechat version >= 0.3.7
        if int(version) >= 0x00030700:
            hook1 = weechat.hook_process_hashtable("url:" + url, 
                                                   {"postfields": postdata}, 
                                                   2000, 
                                                   "", 
                                                   "")
        else:
            urllib2.urlopen(url, postdata)

if __name__ == '__main__':
    weechat.register("pushover", "Caspar Clemens Mierau <ccm@screenage.de>", "0.3", "GPL",
                     "pushover: Send push notifications to you iPhone/Android about your private message and highlights.", "", "")
    init_settings()
    # Hook privmsg/highlights
    weechat.hook_print("", "irc_privmsg", "", 1, "notify_show", "")
