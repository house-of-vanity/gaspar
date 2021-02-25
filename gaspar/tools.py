from datetime import datetime

def format_topic(tor_id, topic_title, size, info_hash, reg_time, pre=''):
    def sizeof_fmt(num, suffix='B'):
        num = int(num)
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
    size = sizeof_fmt(size)    
    reg_time = datetime.utcfromtimestamp(int(reg_time)
            ).strftime('%b-%d-%Y')
    msg = f"""{pre}<a href='https://rutracker.org/forum/viewtopic.php?t={tor_id}'><b>{topic_title}</b></a>
<b>💿 Size:</b>                    <code>{size}</code>
<b>#️⃣ Hash:</b>                 <code>{info_hash}</code>
<b>📅 Updated:</b>          <code>{reg_time}</code>
<b>❌ Unsubscribe:  /delete_{tor_id}</b>\n"""
    return msg
