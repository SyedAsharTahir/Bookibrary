import React from "react";

function TableSkeleton({ rows = 5, columns = 5 }) {
  return (
    <div className="border border-border shadow-md overflow-x-auto">
      <table className="min-w-full">
        <thead>
          <tr className="bg-primary text-white text-sm">
            {Array.from({ length: columns }).map((_, index) => (
              <th key={index} className="p-3 border-r border-border">
                ...
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex} className="border-b border-border">
              {Array.from({ length: columns }).map((__, colIndex) => (
                <td key={colIndex} className="p-3">
                  <div className="h-4 w-full animate-pulse rounded bg-gray-200" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TableSkeleton;
