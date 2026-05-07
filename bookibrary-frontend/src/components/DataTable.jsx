// src/components/DataTable.jsx
import React from "react";

const DataTable = ({
  columns,
  data,
  onDelete,
  emptyMessage = "No records found.",
  children,
}) => (
  <div className="overflow-x-auto rounded-xl border border-border bg-card shadow-md">
    <table className="min-w-full">
      <thead>
        <tr className="bg-primary text-left text-sm text-white">
          {columns.map((col, i) => (
            <th key={i} className="px-4 py-3 font-semibold last:border-r-0 border-r border-white/20">
              {col}
            </th>
          ))}
          {onDelete && <th className="px-4 py-3 font-semibold">Actions</th>}
        </tr>
      </thead>
      <tbody>
        {data.length === 0 ? (
          <tr>
            <td
              colSpan={columns.length + (onDelete ? 1 : 0)}
              className="p-8 text-center text-sm text-slate-500"
            >
              {emptyMessage}
            </td>
          </tr>
        ) : (
          React.Children.map(children, (child, index) => (
            <tr key={data[index]?.id ?? index} className="border-b border-border text-sm hover:bg-muted/70">
              {child.props.children}
              {onDelete && (
                <td className="p-3">
                  <button
                    onClick={() => onDelete(data[index].id)}
                    className="rounded-md bg-destructive px-3 py-1 text-xs font-medium text-white hover:opacity-90"
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