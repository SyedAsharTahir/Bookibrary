import React, { useEffect, useState } from "react";
import API from "../api/axios";
import DataTable from "../components/DataTable";
import LoadingSpinner from "../components/LoadingSpinner";
import TableSkeleton from "../components/TableSkeleton";
import { getRole } from "../auth";

function Books() {
    const [books, setBooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const role = getRole();
    const canManageBooks = role === "admin" || role === "librarian";
    const [form, setForm] = useState({
        title: '', author: '', isbn: '', quantity: 1, published_date: ''
    });

    const fetchBooks = () => {
        setLoading(true);
        API.get('books/')
            .then(response => setBooks(response.data))
            .catch(error => console.log(error))
            .finally(() => setLoading(false));
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
        if (!canManageBooks) {
            setError("Only admin or librarian can add books.");
            return;
        }

        setError("");
        const payload = {
            ...form,
            quantity: Number(form.quantity) || 1,
        };

        if (form.author === "") {
            payload.author = null;
        } else {
            const parsedAuthor = Number(form.author);
            if (Number.isNaN(parsedAuthor)) {
                setError("Author must be a numeric author ID (example: 1).");
                return;
            }
            payload.author = parsedAuthor;
        }

        API.post('books/', payload).then(() => {
            fetchBooks();
            setForm({ title: '', author: '', isbn: '', quantity: 1, published_date: '' });
        }).catch(error => {
            const message =
                error?.response?.data?.detail ||
                JSON.stringify(error?.response?.data) ||
                "Failed to add book.";
            setError(message);
        });
    }

return (
        <div>
            <h1 className="text-3xl font-bold mb-6">📖 Books</h1>
            
            {/* Form Section */}
            <div className="bg-card border border-border p-6 mb-8 shadow-md">
                <h2 className="text-xl font-semibold mb-4">Add New Book</h2>
                {error && (
                    <div className="mb-4 rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700">
                        {error}
                    </div>
                )}
                {!canManageBooks && (
                    <div className="mb-4 rounded border border-yellow-300 bg-yellow-50 p-3 text-sm text-yellow-700">
                        Your role cannot add books. Login as admin or librarian.
                    </div>
                )}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input name="title" placeholder="Title" value={form.title} onChange={Change}
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="author" placeholder="Author ID (optional)" value={form.author} onChange={Change}
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
            {loading ? (
                <div className="space-y-3">
                    <LoadingSpinner text="Loading books..." />
                    <TableSkeleton rows={5} columns={7} />
                </div>
            ) : (
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
            )}
        </div>
    );
}

export default Books;