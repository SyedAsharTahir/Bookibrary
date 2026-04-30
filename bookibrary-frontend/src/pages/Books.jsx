import React, { useEffect, useState } from "react";
import API from "../api/axios";
import DataTable from "../components/DataTable";

function Books() {
    const [books, setBooks] = useState([]);
    const [form, setForm] = useState({
        title: '', author: '', isbn: '', quantity: 1, published_date: ''
    });

    const fetchBooks = () => {
        API.get('books/').then(response => setBooks(response.data)).catch(error => console.log(error));
    }
    const Change = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    }
    useEffect(() => {
        fetchBooks();
    }, [])
    const Del = (id) => {
        API.delete(`books/${id}/`).then(() => fetchBooks()).catch(error => console.log(error));
    }
    const SendToDjango = () => {
        API.post('books/', form).then(() => {
            fetchBooks();
            setForm({ title: '', author: '', isbn: '', quantity: 1, published_date: '' });
        }).catch(error => console.log(error));
    }

return (
        <div>
            <h1 className="text-3xl font-bold mb-6">📖 Books</h1>
            
            {/* Form Section */}
            <div className="bg-card border border-border p-6 mb-8 shadow-md">
                <h2 className="text-xl font-semibold mb-4">Add New Book</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input name="title" placeholder="Title" value={form.title} onChange={Change}
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="author" placeholder="Author" value={form.author} onChange={Change}
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="isbn" placeholder="ISBN" value={form.isbn} onChange={Change}
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="quantity" placeholder="Quantity" value={form.quantity} onChange={Change} type="number"
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="published_date" value={form.published_date} onChange={Change} type="date"
                        className="border border-border p-2 focus:outline-primary" />
                </div>
                <button onClick={SendToDjango}
                    className="mt-4 bg-primary text-white px-6 py-2 border border-border font-medium hover:opacity-90">
                    Add Book
                </button>
            </div>

            {/* Books Table - Now using the DataTable Component */}
           <DataTable 
    columns={['ID', 'Title', 'Author', 'ISBN', 'Qty', 'Published']}
    data={books}
    onDelete={Del}
>
    {books.map(book => (
        <React.Fragment key={book.id}>
            <td className="p-3 border-r border-border">{book.id}</td>
            <td className="p-3 border-r border-border">{book.title}</td>
            <td className="p-3 border-r border-border">{book.author}</td>
            <td className="p-3 border-r border-border">{book.isbn}</td>
            <td className="p-3 border-r border-border">{book.quantity}</td>
            <td className="p-3 border-r border-border">{book.published_date}</td>
        </React.Fragment>
    ))}
</DataTable>
        </div>
    );
}

export default Books;