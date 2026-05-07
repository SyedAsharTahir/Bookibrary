// src/components/DataTable.jsx
import React from "react";

const DataTable = ({
  columns,
  data,
  onDelete,
  emptyMessage = "No records found.",
  children,
}) => (
  <div className="border border-border shadow-md overflow-x-auto">
    <table className="min-w-full">
      <thead>
        <tr className="bg-primary text-white text-sm">
          {columns.map((col, i) => (
            <th key={i} className="p-3 border-r border-border">
              {col}
            </th>
          ))}
          {onDelete && <th className="p-3">Actions</th>}
        </tr>
      </thead>
      <tbody>
        {data.length === 0 ? (
          <tr>
            <td
              colSpan={columns.length + (onDelete ? 1 : 0)}
              className="p-6 text-center text-sm text-gray-500"
            >
              {emptyMessage}
            </td>
          </tr>
        ) : (
          React.Children.map(children, (child, index) => (
            <tr className="border-b border-border text-sm text-center hover:bg-muted">
              {child.props.children}
              {onDelete && (
                <td className="p-3">
                  <button
                    onClick={() => onDelete(data[index].id)}
                    className="bg-destructive text-white px-3 py-1 text-xs border border-border hover:opacity-90"
                  >
                    Delete
                  </button>
                </td>
              )}
            </tr>
          ))
        )}
      </tbody>
    </table>
  </div>
);

export default DataTable;