from asyncio import sleep
import base64
import os
import streamlit as st
import json

def display_pdf(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

def disable(b):
    st.session_state["disabled"] = b


def init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

def upd(key, val):
    st.session_state[key] = val

def get(key):
    if key not in st.session_state:
        return None
    return st.session_state[key]
    
def reset_score():
    st.session_state['correct'] = 0
    st.session_state['current'] = 0

def main():
    # Sidebar to select the year
    year = st.sidebar.selectbox("Select a Year", ["2012", "2013", "2014", "2015", "2016", "2017", "2018"], on_change=reset_score)
    with open('qa.json', 'r') as f:
        data = json.load(f)
    # Questions and answers for the selected year
    questions = data[f"q{year}"]
    answers = data[f"a{year}"]

    # Session state for correct answers and current question
    if 'correct' not in st.session_state:
        st.session_state['correct'] = 0

    if 'current' not in st.session_state:
        st.session_state['current'] = 0


    init('history', [])

    # Display the current question
    question = questions[st.session_state['current']]
    st.write(f"Intrebarea {question['n']}: {question['q']}")

    # Display the options
    option = st.radio("Alege o optiune:", options=[f'a. {question["a"]}', f'b. {question["b"]}', f'c. {question["c"]}'])

    placeholder = st.empty()
    btn = placeholder.button('Alege', disabled=False, key='1')

    # Check if an option has been selected
    # if (choose_btn := st.button('choose')):
    if btn:
        # Increment the current question
        placeholder.button('Continua', disabled=False, key='2')

        st.session_state['current'] += 1

        # Check if the answer is correct
        correct_answer = answers[str(question['n'])]
        if option.startswith(correct_answer):
            st.session_state['correct'] += 1
            st.markdown("<span style='color:green'>Raspuns corect!</span>", unsafe_allow_html=True)
        else:
            st.error(f"Raspuns gresit! Raspunsul corect este: {correct_answer}")

        # Display the score
        st.write(f"{st.session_state['correct']}/{st.session_state['current']} raspunsuri corecte")

        # Reset the score and current question if we've reached the end
        if st.session_state['current'] == len(questions):
            nota = st.session_state['correct']/len(questions) * 10
            anunt = f"Ai obtinut {st.session_state['correct']} din {len(questions)} de puncte pentru anul {year}. Nota {nota:.2f}"
            if nota == 10:
                anunt += ' FELICITARI!'
            st.warning(anunt)
            upd('history', [anunt] + get('history'))
            print(get('history'))
            st.session_state['correct'] = 0
            st.session_state['current'] = 0

    # Get the list of PDF files in the current directory
    pdf_files = sorted([file for file in os.listdir() if file.endswith(".pdf")], key=lambda x: x[::-1])
    if st.sidebar.checkbox('Arata PDFurile originale'):
        for pdf_file in pdf_files:
            # Extract year from the file name
            year = os.path.splitext(pdf_file)[0].split("_")[-1]

            # Determine the checkbox text based on the PDF file name
            if pdf_file.startswith("qa"):
                checkbox_text = f"intrebari si raspunsuri {year}"
            elif pdf_file.startswith("q"):
                checkbox_text = f"intrebari {year}"
            elif pdf_file.startswith("a"):
                checkbox_text = f"raspunsuri {year}"
            else:
                continue  # Skip files that don't match the desired prefixes

            # Create a checkbox with the respective text
            # checkbox = st.sidebar.checkbox(checkbox_text, key=pdf_file, on_change=lambda checked, file=pdf_file: display_pdf(file))
            checkbox_value = st.sidebar.checkbox(checkbox_text, key=pdf_file)
            if checkbox_value:
                display_pdf(pdf_file)
    if (h:= get('history')):
        st.sidebar.markdown('## Istoric')
        for line in h:
            st.sidebar.warning(line)
if __name__ == "__main__":
    main()