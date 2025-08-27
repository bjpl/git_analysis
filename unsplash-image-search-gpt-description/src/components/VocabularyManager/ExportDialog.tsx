import React, { useState, useCallback } from 'react';
import { Download, FileText, Database, BookOpen, Settings, CheckCircle } from 'lucide-react';
import { ExportFormat } from '../../types';
import { useVocabulary } from '../../hooks/useVocabulary';
import { vocabularyService } from '../../services/vocabularyService';
import { Button } from '../Shared/Button/Button';
import { Card } from '../Shared/Card/Card';

interface ExportDialogProps {
  onClose: () => void;
}

export function ExportDialog({ onClose }: ExportDialogProps) {
  const { vocabularyItems, stats } = useVocabulary();
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>(ExportFormat.CSV);
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [customOptions, setCustomOptions] = useState({
    includeStats: true,
    includeImages: false,
    includeExamples: true,
    onlyMastered: false,
    includeNotes: true,
    includeProgress: true
  });

  const exportFormats = [
    {
      value: ExportFormat.CSV,
      label: 'CSV (Excel)',
      description: 'Spreadsheet format, perfect for Excel or Google Sheets',
      icon: <FileText className="w-5 h-5" />,
      recommended: 'Great for data analysis and backup'
    },
    {
      value: ExportFormat.JSON,
      label: 'JSON',
      description: 'Complete data export with all metadata',
      icon: <Database className="w-5 h-5" />,
      recommended: 'Best for complete backup and migration'
    },
    {
      value: ExportFormat.ANKI,
      label: 'Anki Deck',
      description: 'Import directly into Anki for spaced repetition',
      icon: <BookOpen className="w-5 h-5" />,
      recommended: 'Perfect for Anki users'
    }
  ];

  const handleExport = useCallback(async () => {
    setIsExporting(true);
    
    try {
      const blob = await vocabularyService.exportVocabulary(selectedFormat);
      
      // Create download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Set filename based on format
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `vocabulary_${timestamp}.${selectedFormat}`;
      a.download = filename;
      
      // Trigger download
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      setExportSuccess(true);
      
      // Auto-close after success
      setTimeout(() => {
        onClose();
      }, 2000);
      
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  }, [selectedFormat, onClose]);

  const getFilteredItemCount = () => {
    if (customOptions.onlyMastered) {
      return vocabularyItems.filter(item => item.masteryLevel === 'mastered').length;
    }
    return vocabularyItems.length;
  };

  const getExportPreview = () => {
    switch (selectedFormat) {
      case ExportFormat.CSV:
        return {
          headers: ['Word', 'Translation', 'Category', 'Difficulty', 'Mastery Level', 'Times Reviewed', 'Accuracy', 'Notes'],
          sample: [
            ['casa', 'house', 'Nouns', '3', 'mastered', '12', '92%', 'Basic vocabulary'],
            ['correr', 'to run', 'Verbs', '4', 'review', '8', '75%', 'Exercise related']
          ]
        };
      case ExportFormat.JSON:
        return {
          structure: {
            metadata: {
              exportedAt: '2024-01-15T10:30:00Z',
              totalItems: getFilteredItemCount(),
              version: '1.0'
            },
            items: [
              {
                id: 'uuid',
                word: 'casa',
                translation: 'house',
                examples: ['...'],
                stats: '{ mastery, reviews, ... }'
              }
            ]
          }
        };
      case ExportFormat.ANKI:
        return {
          deckName: 'Spanish Vocabulary',
          cardFormat: 'Front: Spanish word | Back: English translation + examples',
          fields: ['Spanish', 'English', 'Examples', 'Notes', 'Audio']
        };
      default:
        return null;
    }
  };

  const preview = getExportPreview();

  if (exportSuccess) {
    return (
      <div className="text-center py-8">
        <div className="mb-4">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Export Successful!
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Your vocabulary has been exported successfully.
        </p>
        <Button variant="primary" onClick={onClose}>
          Close
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Export Vocabulary
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Export your vocabulary collection in various formats for backup or use with other applications.
        </p>
      </div>

      {/* Export Format Selection */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Choose Export Format
        </h3>
        
        <div className="space-y-3">
          {exportFormats.map((format) => (
            <label
              key={format.value}
              className={`flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all ${
                selectedFormat === format.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900 dark:border-blue-400'
                  : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
              }`}
            >
              <input
                type="radio"
                value={format.value}
                checked={selectedFormat === format.value}
                onChange={(e) => setSelectedFormat(e.target.value as ExportFormat)}
                className="sr-only"
              />
              
              <div className="flex-shrink-0 mr-3 mt-1">
                {format.icon}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    {format.label}
                  </h4>
                  {selectedFormat === format.value && (
                    <CheckCircle className="w-5 h-5 text-blue-500" />
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {format.description}
                </p>
                <p className="text-xs text-blue-600 dark:text-blue-400">
                  {format.recommended}
                </p>
              </div>
            </label>
          ))}
        </div>
      </Card>

      {/* Export Options */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Export Options</h3>
        
        <div className="space-y-3">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={customOptions.includeStats}
              onChange={(e) => setCustomOptions(prev => ({ ...prev, includeStats: e.target.checked }))}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Include learning statistics (reviews, accuracy, streaks)
            </span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={customOptions.includeExamples}
              onChange={(e) => setCustomOptions(prev => ({ ...prev, includeExamples: e.target.checked }))}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Include example sentences
            </span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={customOptions.includeNotes}
              onChange={(e) => setCustomOptions(prev => ({ ...prev, includeNotes: e.target.checked }))}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Include personal notes
            </span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={customOptions.includeImages}
              onChange={(e) => setCustomOptions(prev => ({ ...prev, includeImages: e.target.checked }))}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Include image URLs
            </span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={customOptions.onlyMastered}
              onChange={(e) => setCustomOptions(prev => ({ ...prev, onlyMastered: e.target.checked }))}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Export only mastered words
            </span>
          </label>
        </div>
      </Card>

      {/* Export Preview */}
      {preview && (
        <Card className="p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Preview</h3>
          
          {selectedFormat === ExportFormat.CSV && preview.headers && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 dark:bg-gray-800">
                    {preview.headers.map((header, index) => (
                      <th key={index} className="px-3 py-2 text-left font-medium text-gray-700 dark:text-gray-300">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.sample?.map((row, rowIndex) => (
                    <tr key={rowIndex} className="border-t border-gray-200 dark:border-gray-600">
                      {row.map((cell, cellIndex) => (
                        <td key={cellIndex} className="px-3 py-2 text-gray-600 dark:text-gray-400">
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          
          {selectedFormat === ExportFormat.JSON && preview.structure && (
            <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg text-xs overflow-x-auto">
              <code>{JSON.stringify(preview.structure, null, 2)}</code>
            </pre>
          )}
          
          {selectedFormat === ExportFormat.ANKI && preview.deckName && (
            <div className="space-y-2 text-sm">
              <p><strong>Deck Name:</strong> {preview.deckName}</p>
              <p><strong>Card Format:</strong> {preview.cardFormat}</p>
              <p><strong>Fields:</strong> {preview.fields?.join(', ')}</p>
            </div>
          )}
        </Card>
      )}

      {/* Export Summary */}
      <Card className="p-6 mb-6 bg-blue-50 dark:bg-blue-900 border-blue-200 dark:border-blue-700">
        <div className="flex items-start gap-3">
          <Download className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-1">
              Export Summary
            </h4>
            <div className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              <p>Format: <strong>{exportFormats.find(f => f.value === selectedFormat)?.label}</strong></p>
              <p>Items to export: <strong>{getFilteredItemCount().toLocaleString()}</strong> vocabulary items</p>
              <p>File size: <strong>~{Math.round(getFilteredItemCount() * 0.2)}KB</strong> (estimated)</p>
              {stats && (
                <p>Categories: <strong>{Object.keys(stats.categoryBreakdown).length}</strong> different categories</p>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3">
        <Button
          variant="outline"
          onClick={onClose}
          disabled={isExporting}
        >
          Cancel
        </Button>
        
        <Button
          variant="primary"
          onClick={handleExport}
          disabled={isExporting || getFilteredItemCount() === 0}
        >
          {isExporting ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Exporting...
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export {getFilteredItemCount().toLocaleString()} Items
            </div>
          )}
        </Button>
      </div>

      {/* Help Text */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <h4 className="font-medium text-gray-900 dark:text-white mb-2">Need Help?</h4>
        <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
          <p><strong>CSV:</strong> Open with Excel, Google Sheets, or any spreadsheet application</p>
          <p><strong>JSON:</strong> Technical format that preserves all data and can be re-imported</p>
          <p><strong>Anki:</strong> Use Tools → Import in Anki and select the downloaded file</p>
        </div>
      </div>
    </div>
  );
}