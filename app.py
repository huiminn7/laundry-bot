import streamlit as st
from datetime import datetime, timedelta
from supabase import create_client
from streamlit_autorefresh import st_autorefresh 
import streamlit.components.v1 as components

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="UM Laundry Tracker", page_icon="🧺", layout="wide")

# === FIXED: Set to 60000 (60 seconds) so it doesn't break ===
st_autorefresh(interval=60000, key="datarefresh")
# ============================================================

st.title("🧺 Universiti Malaya Laundry Tracker")

# Dropdown to choose Kolej Kediaman
selected_kk = st.selectbox(
    "🏢 Choose your Kolej Kediaman:",
    ["KK12", "KK10", "KK1"]
)

st.subheader(f"Real-time machine availability for {selected_kk}")

# Fetch data filtered by the selected KK
def load_machines(kk):
    response = supabase.table('machines').select('*').eq('kk_name', kk).execute()
    return {row['name']: row for row in response.data}

machines = load_machines(selected_kk)
sorted_machines = sorted(machines.items())

if not sorted_machines:
    st.info(f"No washing machines registered for {selected_kk} yet.")
else:
    st.write("### 🧺 Washing Machines")
    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]

    for i, (name, data) in enumerate(sorted_machines):
        col_index = i % 3 
        
        with columns[col_index]:
            with st.container(border=True): 
                if data['status'] == 'available':
                    st.success(f"**{name.replace('_', ' ')}**")
                    st.write("🟢 Ready to use")
                    
                    if st.button(f"🔒 Lock Machine", key=f"lock_{name}_{selected_kk}", use_container_width=True):
                        # Currently set to 1 minute for fast testing! Change to 45 later.
                        end_time = datetime.now() + timedelta(minutes=1)
                        supabase.table('machines').update({
                            'status': 'busy',
                            'username': 'Web User',
                            'end_time': end_time.isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }).eq('name', name).eq('kk_name', selected_kk).execute() 
                        st.rerun()
                else:
                    st.error(f"**{name.replace('_', ' ')}**")
                    st.write("🔴 In use")
                    
                    # === BULLETPROOF JAVASCRIPT COUNTDOWN ===
                    if data.get('end_time'):
                        try:
                            # 1. Python calculates the exact remaining seconds (bypasses timezone desyncs)
                            end_time_str = data['end_time'].replace('Z', '+00:00')
                            parsed_end_time = datetime.fromisoformat(end_time_str).replace(tzinfo=None)
                            remaining_seconds = int((parsed_end_time - datetime.now()).total_seconds())
                            
                            # 2. Tell the browser to just count down from those exact seconds
                            js_timer = f"""
                            <div id="timer_{name}" style="font-family: sans-serif; color: #ff4b4b; font-weight: bold; margin-bottom: 5px;"></div>
                            <script>
                                var remainingMs = {remaining_seconds} * 1000;
                                var x = setInterval(function() {{
                                    if (remainingMs <= 0) {{
                                        clearInterval(x);
                                        document.getElementById("timer_{name}").innerHTML = "⏳ Finishing up...";
                                    }} else {{
                                        var minutes = Math.floor((remainingMs % (1000 * 60 * 60)) / (1000 * 60));
                                        var seconds = Math.floor((remainingMs % (1000 * 60)) / 1000);
                                        document.getElementById("timer_{name}").innerHTML = "⏳ " + minutes + "m " + seconds + "s left";
                                        remainingMs -= 1000; // Tick down 1 second
                                    }}
                                }}, 1000);
                            </script>
                            """
                            components.html(js_timer, height=35)
                        except Exception:
                            pass
                    # ========================================
                            
                    if data.get('username'):
                        st.caption(f"👤 @{data['username']}")
                        
                    if st.button(f"🔓 Unlock", key=f"free_{name}_{selected_kk}", use_container_width=True):
                        supabase.table('machines').update({
                            'status': 'available',
                            'username': '',
                            'end_time': None,
                            'updated_at': datetime.now().isoformat()
                        }).eq('name', name).eq('kk_name', selected_kk).execute() 
                        st.rerun()