import streamlit as st
from openai import OpenAI
import httpx


# set API key in order to call the API of OpenAI
client = OpenAI(
    base_url="https://api.chatgptid.net/v1", 
    api_key="sk-xilClnLdQ21I8r9hAaC24bAdBbB94e139f23C5BeAf286cFd",
    http_client=httpx.Client(
        base_url="https://api.chatgptid.net/v1",
        follow_redirects=True,
    ),
)

# The list of books I read
books =[
    {"title": "Dune", "author": "Frank Herbert"},
    {"title": "1984", "author": "George Orwell"},
    {"title": "Brave New World", "author": "Aldous Huxley"},
    {"title": "Fahrenheit 451", "author": "Ray Bradbury"},
    {"title": "The War of the Worlds", "author": "H.G. Wells"},
    {"title": "The Time Machine", "author": "H.G. Wells"},
    {"title": "Foundation", "author": "Isaac Asimov"},
    {"title": "Neuromancer", "author": "William Gibson"},
    {"title": "Snow Crash", "author": "Neal Stephenson"},
    {"title": "The Hitchhiker's Guide to the Galaxy", "author": "Douglas Adams"}
]

# The rules to be sent to openAI ask for some recommended books based on what has been read, along with a recommendation algorithm and explanation. 
# Including Format requirements for the returned recommendation results.
recommend_rules = ("With according to my reading history recommended to me another 4 books, "
     "reading history I will be sent to you as a list,"
     "You need to explain the method and detailed reason you recommend it, the method means what algorithm do you use to do this recommendation, you must briefly explain how the algorithm run in reason part. make sure that the reason you provide align with the method you give"
     "the format of result of recommended books must be as follow:"
     + """[{"title": "title", "author": "author","method": "recommend method", "reason": "detailed recommend  reason" },
            {"title": "title", "author": "author","method": "recommend method", "reason": "detailed recommend  reason"},
            {"title": "title", "author": "author","method": "recommend method", "reason": "detailed recommend  reason"},
            {"title": "title", "author": "author","method": "recommend method", "reason": "detailed recommend  reason"}]""")

# Send rules and books to OpenAI to get recommended books from LLM.
def get_recommended_books(books_read):
    responde_result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{recommend_rules}"},
            {"role": "system", "content": "Ensure that the reason you provide align with the method you give!!"},
            {"role": "user", "content": f"my reading history: {books_read}"},
            {"role": "system", "content": "Be sure to provide answers as described above, and only provide the results in the required format, do not reply with any other text!"},
            {"role": "system", "content": "you must use the format above!!"},
        ]
    )
    # Extract the txt of recommended books
    recommended_books_txt = responde_result.choices[0].message.content
    # Convert the returned answers into a list
    return eval(recommended_books_txt)




# The rules to be sent to openAI ask for some recommended books based on the user's requirement, along with a recommendation algorithm and explanation. 
# Including Format requirements for the returned recommendation results.
other_recommend_rules = ("With according to my requirement recommended to me another 4 books, "
     "reading history I will be sent to you as a list,"
     "You need to explain the method and detailed reason you recommend it in 'reason',You must fully describe the reasons for recommending the book in terms of content, sales, ratings, etc. that"
     "the formatthe of result of recommended books must be as follow:"
     + """[{"title": "title", "author": "author", "reason": "detailed recommend  reason"},
            {"title": "title", "author": "author", "reason": "detailed recommend  reason"},
            {"title": "title", "author": "author", "reason": "detailed recommend  reason"},
            {"title": "title", "author": "author", "reason": "detailed recommend  reason"}]""")


# Call the API of Open AI, Get recommended books based on the requirement of user
def get_customized_recommended_books(command_from_user):
    responde_result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{other_recommend_rules}, in the reason you must explain the reason for the recommendation in terms of where it meets my requirements."},
            {"role": "user", "content": f"{command_from_user}"},
            {"role": "system", "content": "Be sure to provide answers as described above, and only provide the results in the required format, do not reply with any other text!"},
            {"role": "system", "content": "you must use the format above!!"}

        ]
    )

    # Extract the txt of recommended books
    customized_recommended_books_txt = responde_result.choices[0].message.content
    # Convert the result to list
    return eval(customized_recommended_books_txt)



# Streamlit
def main():
    # Initialize session_state
    if 'books_read' not in st.session_state:
        st.session_state['books_read'] = books
    if 'recommended_books' not in st.session_state:
        st.session_state['recommended_books'] = get_recommended_books(st.session_state['books_read'])

    st.title("Book recommendation system")

    # Reading History part
    st.header("Reading History")
    books_read = st.session_state.books_read

    # Display up to 4 books per row dynamically
    for i in range(0, len(books_read), 4):
        cols = st.columns(4)
        for col, book in zip(cols, books_read[i:i+4]):
            with col.container():
                st.markdown("---")
                st.write(f"**{book['title']}**")
                st.write(book["author"])
                st.markdown("---")

    # Add new book, allowing user to add books the have read
    st.header("Add a New Book")
    new_book_title = st.text_input("Book Title")
    new_book_author = st.text_input("Book Author")
    new_add_book_button = st.button('Add Book')

    if new_add_book_button:
        if new_book_title and new_book_author:
            new_book = {"title": new_book_title, "author": new_book_author}
            st.session_state.books_read.append(new_book)
            st.success("Book added successfully!")
            st.session_state.recommended_books = get_recommended_books(st.session_state.books_read)
            #print(books_read)
            st.experimental_rerun()
        else:
            st.error("Please fill in all fields.")
    st.divider() 

    # Book recommendation based on the reading history of user.
    st.header("Recommended Books")
    recommended_books = st.session_state.recommended_books

    # Display recommended books per row dynamically, 4 books totally.
    for i in range(0, len(recommended_books), 4):
        cols = st.columns(4)
        for col, book in zip(cols, recommended_books[i:i+4]):
            with col.container():
                st.markdown("---")
                st.write(f"**{book['title']}**")
                st.write(book["author"])
                #st.write("Argorithem : content-based")
                st.write(f"**Algorithm** : {book['method']}")
                st.write(f"**Reason** : *{book['reason']}*")
                st.markdown("---")
    
    # Get customized recommendation
    st.header("'I don't like your recommendation'")
    new_requirement_txt = st.text_input("Your requirement")
    new_get_recommendation_button = st.button('Get more recommendation')

    # Display recommended books based on requirement per row dynamically, 4 books totally.
    if new_get_recommendation_button:
        # Get customized recommended books from LLM
        other_recommend_books = get_customized_recommended_books(new_requirement_txt)
        print(other_recommend_books)
        for i in range(0, len(other_recommend_books), 4):
            cols = st.columns(4)
            for col, book in zip(cols, other_recommend_books[i:i+4]):
                with col.container():
                    st.markdown("---")
                    st.write(f"**{book['title']}**")
                    st.write(book["author"])
                    st.write("**Argorithem** : based on your requirement")
                    st.write(f"*{book['reason']}*")
                    st.markdown("---")


main()