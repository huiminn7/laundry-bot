import asyncio
from datetime import datetime
from telegram import Bot
from supabase import create_client

# ========== CONFIG ==========
try:
    from config import TOKEN, SUPABASE_URL, SUPABASE_KEY
except ImportError:
    print("❌ Error: config.py not found.")
    exit(1)

bot = Bot(token=TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def check_reminders():
    print("⏳ Laundry Reminder Engine is online and watching the clock...")
    
    while True:
        try:
            now = datetime.now().isoformat()
            
            # Find alarms that are finished
            response = supabase.table('reminders').select('*').lte('end_time', now).execute()
            expired_reminders = response.data
            
            for reminder in expired_reminders:
                chat_id = reminder['chat_id']
                machine_num = reminder.get('machine_id', 'Unknown')
                
                # 1. Fire the push notification to Telegram
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"🔔 *BEEP BEEP!*\n\nYour laundry in Washer {machine_num} is finished!\n\nThe machine has been auto-unlocked for the next user.",
                        parse_mode="Markdown"
                    )
                    print(f"✅ Notified user {chat_id}")
                except Exception as e:
                    print(f"❌ Failed to text chat_id {chat_id}: {e}")
                
                # 2. === THE AUTO-UNLOCK MAGIC ===
                # This finds the exact machine this user locked and resets it perfectly!
                try:
                    supabase.table('machines').update({
                        'status': 'available',
                        'user_id': '',
                        'username': '',
                        'end_time': None
                    }).eq('user_id', str(chat_id)).execute()
                    print(f"🔓 Auto-unlocked machine for user {chat_id}")
                except Exception as e:
                    print(f"❌ Failed to auto-unlock machine: {e}")
                
                # 3. Delete the reminder so it doesn't spam
                supabase.table('reminders').delete().eq('id', reminder['id']).execute()
                
        except Exception as e:
            print(f"⚠️ Warning in background loop: {e}")
            
        # Wait 60 seconds before checking again
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(check_reminders())