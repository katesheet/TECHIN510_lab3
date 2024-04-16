import os
from dataclasses import dataclass
import datetime
import sys
import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()
print(os.getenv('DATABASE_URL'))
con = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = con.cursor()

cur.execute('''
Create TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    title TEXT,
    prompt TEXT,
    is_favorite BOOLEAN,
    created_at TIMESTAMP NOT NULL
) 
''')

@dataclass
class Prompt:
    id: int = None
    title: str = ''
    prompt: str = ''
    is_favorite: bool = False
    created_at: datetime.datetime = None



def prompt_form(key, prompt=Prompt()):
    print(key)
    with st.form(key=f'prompt{key}', clear_on_submit=True):
        title = st.text_input('Title', value=prompt.title)
        prompt_text = st.text_area('Prompt', value=prompt.prompt)
        is_favorite = st.checkbox('Favorite', value=prompt.is_favorite)
        ret = st.form_submit_button('Submit')
        print(ret)
        if ret:
            print(1)
            print(Prompt(prompt.id, title, prompt_text, is_favorite, datetime.datetime.now() if prompt.created_at is None else prompt.created_at))
            return Prompt(prompt.id, title, prompt_text, is_favorite, datetime.datetime.now() if prompt.created_at is None else prompt.created_at)
        

def display_prompts(prompts):
    for p in prompts:
        with st.expander(f'{p[1]} {":star-struck:" if p[3] else ""}'):
            st.code(p[2])
            st.text(f'created at {p[4]}')
            if st.button("Delete", key=f"delete_{p[0]}"):
                cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
                con.commit()
                st.rerun()
            if st.button("Toggle Favorite", key=f"fav_{p[0]}"):
                cur.execute("UPDATE prompts SET is_favorite = NOT is_favorite WHERE id = %s", (p[0],))
                con.commit()
                st.rerun()
            

    

st.title('Prompt Storage')
st.subheader('A simple app to store and retrieve prompts')

cur.execute('SELECT COUNT(*) FROM prompts')
count = cur.fetchone()[0]

prompt = prompt_form(count+1)
if prompt:
    cur.execute("INSERT INTO prompts (title, prompt, is_favorite, created_at) VALUES (%s, %s, %s, %s)",(prompt.title, prompt.prompt, prompt.is_favorite, prompt.created_at))
con.commit()
st.success("Prompt added/updated successfully!")

st.markdown('---')

# Search, sort, and filter bar
search_query = st.text_input("Search prompts")
sort_order = st.selectbox("Sort by", ["title", "prompt", "created_at"], index=0)
filter_favorites = st.checkbox("Show favorites only")
search_button = st.button("Search")

query = "SELECT * FROM prompts"
if filter_favorites:
    query += " WHERE is_favorite = true"
if search_query:
    if filter_favorites:
        query += " AND "
    else:
        query += " WHERE "
    query += "title LIKE %s OR prompt LIKE %s"
    query += f" ORDER BY {sort_order} DESC"
    cur.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
else:
    query += f" ORDER BY {sort_order} DESC"
    cur.execute(query)

prompts = cur.fetchall()



display_prompts(prompts)

# sys.exit()