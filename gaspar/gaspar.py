import logging
import os
import sys
from urllib import parse

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, MessageHandler, CommandHandler, filters, CallbackQueryHandler, CallbackContext

from .torrent_clients import add_client, detect_client, easy_send
from .notify import update_watcher
from .rutracker import Torrent
from .tools import format_topic

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

token = os.environ.get('TG_TOKEN')
if not token:
    log.error("Env var TG_TOKEN isn't set.")
    sys.exit(1)


def main():
    """Run bot."""

    def add(update, context):
        if 'https://rutracker.org' in update.message.text:
            try:
                tor_id = parse.parse_qs(parse.urlsplit(update.message.text).query)['t'][0]
            except KeyError:
                log.warning("URL provided doesn't contains any torrent id.")
                update.message.reply_text("URL provided doesn't contains any torrent id.")
                return
        else:
            update.message.reply_text("Send me a URL to rutracker.org topic.")
            return
        log.info(
            "Got /add request from user [%s] %s",
            update.message.chat['id'],
            update.message.from_user.username)
        torrent = Torrent(tor_id)
        torrent.db.save_tor(torrent.meta)
        torrent.db.save_user(update.message.chat)
        torrent.db.save_alert(update.message.chat['id'], torrent.meta['id'])
        msg = format_topic(
            torrent.meta['id'],
            torrent.meta['topic_title'],
            torrent.meta['size'],
            torrent.meta['info_hash'],
            torrent.meta['reg_time'],
            pre='You will be alerted about\n')
        keyboard = []
        if torrent.db.get_client_rpc(update.message.chat['id']):
            keyboard.append([
                InlineKeyboardButton("Add torrent to RPC client?", callback_data=f"start_rpc.{torrent.meta['id']}"),
                InlineKeyboardButton("Don't!", callback_data=f"close.{torrent.meta['id']}"), ],
            )

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=reply_markup)

    def list_alerts(update, context):
        per_page = 5
#       log.info("list_alerts update.callback_query: %s", update.callback_query.message)
        try:
            query = int(update.callback_query.data.split('.')[-1])
            chat_id = update.callback_query.message.chat['id']
            username = update.callback_query.message.chat['username']
            reply = True
        except:
            query = 0
            username = update.message.from_user.username
            chat_id = update.message.chat['id']
            reply = False
        log.info(
            "Got /list request from user [%s] %s",
            chat_id,
            username)
        alerts = Torrent().db.get_alerts(chat_id)
        if len(alerts) == 0:
            update.message.reply_text("You have no configured alerts.")
            return True
        msg = f"<b>Configured {len(alerts)} alerts:</b>\n"
        log.info("interval: %s:%s", query, per_page+query)
        item_num = query + 1
        for alert in alerts[query:per_page+query]:
            msg += format_topic(
                alert['id'],
                alert['topic_title'],
                alert['size'],
                alert['info_hash'],
                alert['reg_time'],
                pre="\n",
                item_num=item_num)
            item_num += 1
        log.info("list_alerts: %s", len(msg))
        if len(alerts) > 5:
            if len(alerts[query:per_page+query]) < per_page:
                keyboard = [
                  [
                    InlineKeyboardButton("<", callback_data=f"list.{query-per_page}"),
                  ]
                ]
            elif query == 0:
                keyboard = [
                  [
                    InlineKeyboardButton(">", callback_data=f"list.{query+per_page}"),
                  ]
                ]
            else:
                keyboard = [
                  [
                    InlineKeyboardButton("<", callback_data=f"list.{query-per_page}"),
                    InlineKeyboardButton(">", callback_data=f"list.{query+per_page}"),
                  ]
                ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if reply:
                update.callback_query.edit_message_text(msg, reply_markup=reply_markup,  parse_mode='HTML', disable_web_page_preview=True)
            else:
                update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True)
        else:
            update.message.reply_text(msg, parse_mode='HTML', disable_web_page_preview=True)

    def handle_client(update, context):
        u_id = update.message.chat['id']
        log.info(
            "Got /client request from user [%s] %s",
            u_id,
            update.message.from_user.username)
        if len(update.message.text.split()) > 1:
            msg = add_client(update.message.text.split()[1], u_id)
            if not msg:
                msg = "Failed. Check URL and your client."
            update.message.reply_text(msg)
        else:
            tr_client = Torrent().db.get_client_rpc(u_id)
            log.info("tr_client: %s", tr_client)
            try:
                user_pass = f"{tr_client[3]}:{tr_client[4]}@" if tr_client[3] and tr_client[4] else ""
                tr_client_check = detect_client(f"{tr_client[0]}://{user_pass}{tr_client[1]}:{tr_client[2]}{tr_client[5] if tr_client[5] != None else ''}")
            except:
                tr_client_check = False
            if tr_client and tr_client_check:
                tr_line = f"Your have configured client.\nURL: <code>{tr_client[0]}://{tr_client[1]}:{tr_client[2]}{tr_client[5] if tr_client[5] != None else ''}</code>\n" \
                          f"Client: <code>{tr_client_check}</code>\nStatus: <code>Works</code>\n" \
                          r"/delete_client"
            elif tr_client:
                tr_line = f"Your have configured client.\nURL: <code>{tr_client[0]}://{tr_client[1]}:{tr_client[2]}{tr_client[5] if tr_client[5] != None else ''}</code>\n" \
                          f"Client: <code>{tr_client_check}</code>\nStatus: <code>Conenction failed!</code>\n" \
                          r"/delete_client"
            else:
                tr_line = "You have no configured client. Send me a link to access web torrent API like https://private.qbittorrent.my. Transmission and qBittorrent are supported now."
            update.message.reply_text(tr_line, parse_mode='HTML', disable_web_page_preview=True)

    def delete_client(update, context):
        log.info(
            "Got /delete request from user [%s] %s",
            update.message.chat['id'],
            update.message.from_user.username)
        Torrent().db.drop_client_rpc(update.message.chat['id'])
        update.message.reply_text(f'Client deleted.')

    def delete(update, context):
        log.info(
            "Got /delete request from user [%s] %s",
            update.message.chat['id'],
            update.message.from_user.username)
        tor_id = update.message.text.split('_')[1]
        try:
            Torrent().db.delete_tor(update.message.chat['id'], tor_id)
            update.message.reply_text(f'Deleted {tor_id}')
        except:
            update.message.reply_text(f'Faled to delete {tor_id}')

    def button(update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        log.info("button: %s", query.data)
        u_id = query.message.chat['id']
        if any(w in query.data for w in ['close', 'start_rpc']):
            torrent_id = query.data.split('.')[1]
            torrent = Torrent(torrent_id)

            msg = format_topic(
                torrent.meta['id'],
                torrent.meta['topic_title'],
                torrent.meta['size'],
                torrent.meta['info_hash'],
                torrent.meta['reg_time'],
                pre='You will be alerted about\n')
            if query.data.split('.')[0] == "close":
                query.answer()
                query.edit_message_text(text=f"{msg}", parse_mode='HTML',
                                        disable_web_page_preview=True)
            elif query.data.split('.')[0] == "start_rpc":
                query.answer()
                easy_send(user_id=u_id, torrent_hash=torrent.meta['info_hash'])
                query.edit_message_text(text=f"{msg}📨 <b>Sent to RPC /client</b>", parse_mode='HTML',
                                        disable_web_page_preview=True)
        if 'list.' in query.data:
            query.answer()
            list_alerts(update, context)

    updater = Updater(token, use_context=True)
    update_watcher(updater.bot)

    updater.dispatcher.add_handler(MessageHandler(filters.Filters.regex(r'/list'), list_alerts))
    updater.dispatcher.add_handler(CommandHandler('client', handle_client))
    updater.dispatcher.add_handler(CommandHandler('delete_client', delete_client))
    updater.dispatcher.add_handler(MessageHandler(filters.Filters.regex(r'/delete_'), delete))
    updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, add))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


#   if __name__ == '__main__':
#       log = logging.getLogger('gaspar')
#       main()
