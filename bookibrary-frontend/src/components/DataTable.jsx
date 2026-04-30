// src/components/DataTable.jsx
import React from "react";

const DataTable = ({ columns, data, onDelete, children }) => (
    <div className="border border-border shadow-md overflow-x-auto">
        <table className="min-w-full">
            <thead>
                <tr className="bg-primary text-white text-sm">
                    {columns.map((col, i) => (
                        <th key={i} className="p-3 border-r border-border">{col}</th>
                    ))}
                    <th className="p-3">Actions</th>
                </tr>
            </thead>
            <tbody>
                {React.Children.map(children, (child, index) => (
                    <tr className="border-b border-border text-sm text-center hover:bg-muted">
                        {child.props.children}
                        <td className="p-3">
                            <button
                                onClick={() => onDelete(data[index].id)}
                                className="bg-destructive text-white px-3 py-1 text-xs border border-border hover:opacity-90"
                            >
                                Delete
                            </button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
);

export default DataTable;