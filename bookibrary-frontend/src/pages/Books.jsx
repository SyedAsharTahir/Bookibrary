import React, { useEffect, useState } from "react";
import API from "../api/axios";
import DataTable from "../components/DataTable";
import LoadingSpinner from "../components/LoadingSpinner";
import TableSkeleton from "../components/TableSkeleton";
import { getRole } from "../auth";

function Books() {
    const [books, setBooks] = useState([]);
    const [authors, setAuthors] = useState([]);
    const [categories, setCategories] = useState([]);
    const [publishers, setPublishers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const role = getRole();
    const canManageBooks = role === "admin" || role === "librarian";
    const [form, setForm] = useState({
        title: '', author_name: '', category_name: '', publisher_name: '', isbn: '', quantity: 1, published_date: '',
        description: '', summary: '', cover_url: ''
    });
    const [editingId, setEditingId] = useState(null);
        
    const fetchBooks = () => {
        setLoading(true);
        API.get('books/')
            .then(response => setBooks(response.data))
            .catch(error => console.log(error))
            .finally(() => setLoading(false));
    }

    const fetchBookLookups = () => {
        API.get('authors/').then(r => setAuthors(r.data)).catch(() => {});
        API.get('categories/').then(r => setCategories(r.data)).catch(() => {});
        API.get('publishers/').then(r => setPublishers(r.data)).catch(() => {});
    }
    const Change = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    }

    useEffect(() => {
        fetchBooks();
        fetchBookLookups();
    }, [])
    const Del = (id) => {
        API.delete(`books/${id}/`).then(() => fetchBooks()).catch(error => console.log(error));
    }
    
    const Edit = (book) => {
        setForm({
            title: book.title,
            author_name: book.author?.name || '',
            category_name: book.category?.name || '',
            publisher_name: book.publisher?.name || '',
            isbn: book.isbn || '',
            quantity: book.quantity || 1,
            published_date: book.published_date || '',
            description: book.description || '',
            summary: book.summary || '',
            cover_url: book.cover_url || ''
        });
        setEditingId(book.id);
    }
    
    const Update = () => {
        if (!canManageBooks) {
            setError("Only admin or librarian can update books.");
            return;
        }

        setError("");
        const payload = {
            title: form.title,
            isbn: form.isbn,
            quantity: Number(form.quantity) || 1,
            published_date: form.published_date || null,
            author_name: form.author_name,
            category_name: form.category_name,
            publisher_name: form.publisher_name || null,
            description: form.description,
            summary: form.summary,
            cover_url: form.cover_url,
        };

        if (!payload.title || !payload.author_name || !payload.category_name) {
            setError("Title, author, and category are required.");
            return;
        }

        API.put(`books/${editingId}/`, payload).then(() => {
            fetchBooks();
            setForm({ title: '', author_name: '', category_name: '', publisher_name: '', isbn: '', quantity: 1, published_date: '', description: '', summary: '', cover_url: '' });
            setEditingId(null);
        }).catch(error => {
            const message =
                error?.response?.data?.detail ||
                JSON.stringify(error?.response?.data) ||
                "Failed to update book.";
            setError(message);
        });
    }
    
    const Cancel = () => {
        setForm({ title: '', author_name: '', category_name: '', publisher_name: '', isbn: '', quantity: 1, published_date: '', description: '', summary: '', cover_url: '' });
        setEditingId(null);
        setError("");
    }
    const SendToDjango = () => {
        if (!canManageBooks) {
            setError("Only admin or librarian can add books.");
            return;
        }

        setError("");
        const payload = {
            title: form.title,
            isbn: form.isbn,
            quantity: Number(form.quantity) || 1,
            published_date: form.published_date || null,
            author_name: form.author_name,
            category_name: form.category_name,
            publisher_name: form.publisher_name || null,
            description: form.description,
            summary: form.summary,
            cover_url: form.cover_url,
        };

        if (!payload.title || !payload.author_name || !payload.category_name) {
            setError("Title, author, and category are required.");
            return;
        }

        API.post('books/', payload).then(() => {
            fetchBooks();
            setForm({ title: '', author_name: '', category_name: '', publisher_name: '', isbn: '', quantity: 1, published_date: '', description: '', summary: '', cover_url: '' });
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
                <h2 className="text-xl font-semibold mb-4">
                    {editingId ? 'Edit Book' : 'Add New Book'}
                </h2>
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
                        className="border border-border p-2 focus:outline-primary" required />
                    <input name="author_name" placeholder="Author Name" value={form.author_name} onChange={Change}
                        className="border border-border p-2 focus:outline-primary" required />
                    <input name="category_name" placeholder="Category" value={form.category_name} onChange={Change}
                        className="border border-border p-2 focus:outline-primary" required />
                    <input name="publisher_name" placeholder="Publisher (optional)" value={form.publisher_name} onChange={Change}
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="isbn" placeholder="ISBN" value={form.isbn} onChange={Change}
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="quantity" placeholder="Quantity" value={form.quantity} onChange={Change} type="number"
                        className="border border-border p-2 focus:outline-primary" />
                    <input name="published_date" value={form.published_date} onChange={Change} type="date"
                        className="border border-border p-2 focus:outline-primary" />
                </div>
                
                <div className="mt-4 flex gap-2">
                    <button onClick={editingId ? Update : SendToDjango}
                        className="bg-primary text-white px-6 py-2 border border-border font-medium hover:opacity-90">
                        {editingId ? 'Update Book' : 'Add Book'}
                    </button>
                    {editingId && (
                        <button onClick={Cancel}
                            className="bg-gray-500 text-white px-6 py-2 border border-border font-medium hover:opacity-90">
                            Cancel
                        </button>
                    )}
                </div>
            </div>

            {/* Books Table - Now using the DataTable Component */}
            {loading ? (
                <div className="space-y-3">
                    <LoadingSpinner text="Loading books..." />
                    <TableSkeleton rows={5} columns={8} />
                </div>
            ) : (
                <DataTable
                    columns={['Title', 'Author', 'Category', 'ISBN', 'Quantity']}
                    data={books}
                    onDelete={canManageBooks ? Del : undefined}
                    onEdit={canManageBooks ? Edit : undefined}
                >
                    {books.map(book => (
                        <React.Fragment key={book.id}>
                            <td className="p-3 border-r border-border max-w-xs truncate">{book.title}</td>
                            <td className="p-3 border-r border-border">{book.author_name || 'Unknown'}</td>
                            <td className="p-3 border-r border-border">{book.category_name || 'Uncategorized'}</td>
                            <td className="p-3 border-r border-border">{book.isbn || 'N/A'}</td>
                            <td className="p-3 border-r border-border">{book.quantity}</td>
                        </React.Fragment>
                    ))}
                </DataTable>
            )}
        </div>
    );
}

export default Books;