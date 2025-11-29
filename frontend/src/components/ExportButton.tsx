import { Download } from 'lucide-react';
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';

interface ExportButtonProps {
    data: any[];
    filename: string;
    format?: 'csv' | 'excel';
}

export function ExportButton({ data, filename, format = 'csv' }: ExportButtonProps) {
    const handleExport = () => {
        if (format === 'csv') {
            exportToCSV(data, filename);
        } else {
            exportToExcel(data, filename);
        }
    };

    const exportToCSV = (data: any[], filename: string) => {
        if (data.length === 0) return;

        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row =>
                headers.map(header => {
                    const value = row[header];
                    // Escape quotes and wrap in quotes if contains comma
                    if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                        return `"${value.replace(/"/g, '""')}"`;
                    }
                    return value;
                }).join(',')
            )
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
        saveAs(blob, `${filename}.csv`);
    };

    const exportToExcel = (data: any[], filename: string) => {
        const worksheet = XLSX.utils.json_to_sheet(data);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Dados');
        XLSX.writeFile(workbook, `${filename}.xlsx`);
    };

    return (
        <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
            <Download className="w-4 h-4" />
            Exportar {format === 'csv' ? 'CSV' : 'Excel'}
        </button>
    );
}
