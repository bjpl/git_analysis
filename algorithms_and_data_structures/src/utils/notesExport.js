/**
 * Notes export utilities
 */

import { formatTimestamp, extractPlainText } from './helpers';

/**
 * Export notes in various formats
 * @param {Array} notes - Notes to export
 * @param {Object} options - Export options
 * @returns {Promise} Export promise
 */
export const exportNotes = async (notes, options = {}) => {
  const {
    format = 'markdown',
    includeMetadata = true,
    lessonId = '',
    filename = `notes-${new Date().toISOString().split('T')[0]}`,
    downloadAsFile = true
  } = options;

  let content = '';
  let mimeType = 'text/plain';
  let fileExtension = '.txt';

  switch (format) {
    case 'markdown':
      content = exportAsMarkdown(notes, includeMetadata, lessonId);
      mimeType = 'text/markdown';
      fileExtension = '.md';
      break;
    case 'json':
      content = exportAsJSON(notes, includeMetadata);
      mimeType = 'application/json';
      fileExtension = '.json';
      break;
    case 'csv':
      content = exportAsCSV(notes, includeMetadata);
      mimeType = 'text/csv';
      fileExtension = '.csv';
      break;
    case 'html':
      content = exportAsHTML(notes, includeMetadata, lessonId);
      mimeType = 'text/html';
      fileExtension = '.html';
      break;
    default:
      content = exportAsPlainText(notes, includeMetadata);
  }

  if (downloadAsFile) {
    downloadFile(content, `${filename}${fileExtension}`, mimeType);
  }

  return {
    content,
    mimeType,
    filename: `${filename}${fileExtension}`
  };
};

/**
 * Export notes as Markdown
 */
const exportAsMarkdown = (notes, includeMetadata, lessonId) => {
  let content = '';
  
  if (lessonId) {
    content += `# Notes for ${lessonId}\n\n`;
  } else {
    content += '# My Notes\n\n';
  }
  
  if (includeMetadata) {
    content += `*Exported on: ${new Date().toLocaleString()}*\n`;
    content += `*Total notes: ${notes.length}*\n\n`;
    content += '---\n\n';
  }
  
  notes.forEach((note, index) => {
    const title = note.title || extractTitleFromContent(note.content);
    const timestamp = formatTimestamp(note.timestamp);
    
    content += `## ${title}\n\n`;
    
    if (includeMetadata) {
      content += `*Created: ${timestamp.full}*\n\n`;
      
      if (note.tags && note.tags.length > 0) {
        content += `**Tags:** ${note.tags.map(tag => `#${tag}`).join(', ')}\n\n`;
      }
    }
    
    content += `${note.content}\n\n`;
    
    if (index < notes.length - 1) {
      content += '---\n\n';
    }
  });
  
  return content;
};

/**
 * Export notes as JSON
 */
const exportAsJSON = (notes, includeMetadata) => {
  const data = {
    exportedAt: new Date().toISOString(),
    totalNotes: notes.length,
    notes: notes.map(note => ({
      id: note.id,
      title: note.title || extractTitleFromContent(note.content),
      content: note.content,
      timestamp: note.timestamp,
      tags: note.tags || [],
      ...(includeMetadata && {
        wordCount: note.wordCount,
        lessonId: note.lessonId,
        isBookmarked: note.isBookmarked,
        hasReminder: note.hasReminder,
        isShared: note.isShared
      })
    }))
  };
  
  return JSON.stringify(data, null, 2);
};

/**
 * Export notes as CSV
 */
const exportAsCSV = (notes, includeMetadata) => {
  const headers = ['ID', 'Title', 'Content', 'Timestamp'];
  
  if (includeMetadata) {
    headers.push('Tags', 'Word Count', 'Lesson ID');
  }
  
  let csv = headers.join(',') + '\n';
  
  notes.forEach(note => {
    const title = (note.title || extractTitleFromContent(note.content)).replace(/"/g, '""');
    const content = extractPlainText(note.content).replace(/"/g, '""').replace(/\n/g, ' ');
    const timestamp = new Date(note.timestamp).toISOString();
    
    let row = [
      `"${note.id}"`,
      `"${title}"`,
      `"${content}"`,
      `"${timestamp}"`
    ];
    
    if (includeMetadata) {
      const tags = (note.tags || []).join('; ');
      row.push(
        `"${tags}"`,
        `"${note.wordCount || 0}"`,
        `"${note.lessonId || ''}"`
      );
    }
    
    csv += row.join(',') + '\n';
  });
  
  return csv;
};

/**
 * Export notes as HTML
 */
const exportAsHTML = (notes, includeMetadata, lessonId) => {
  let html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Notes Export</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
      color: #333;
    }
    .note {
      margin-bottom: 2rem;
      padding: 1.5rem;
      border: 1px solid #e1e5e9;
      border-radius: 8px;
      background: #fafbfc;
    }
    .note-title {
      margin: 0 0 0.5rem 0;
      color: #1a73e8;
      font-size: 1.25rem;
    }
    .note-meta {
      font-size: 0.875rem;
      color: #666;
      margin-bottom: 1rem;
    }
    .note-content {
      white-space: pre-wrap;
      font-size: 0.95rem;
    }
    .tags {
      margin-top: 1rem;
    }
    .tag {
      display: inline-block;
      background: #e8f0fe;
      color: #1a73e8;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      margin-right: 0.5rem;
    }
    .export-info {
      background: #f8f9fa;
      padding: 1rem;
      border-radius: 8px;
      margin-bottom: 2rem;
      border-left: 4px solid #1a73e8;
    }
  </style>
</head>
<body>
`;

  html += `  <h1>Notes${lessonId ? ` for ${lessonId}` : ''}</h1>\n`;
  
  if (includeMetadata) {
    html += `  <div class="export-info">
    <p><strong>Exported:</strong> ${new Date().toLocaleString()}</p>
    <p><strong>Total Notes:</strong> ${notes.length}</p>
  </div>\n`;
  }
  
  notes.forEach(note => {
    const title = note.title || extractTitleFromContent(note.content);
    const timestamp = formatTimestamp(note.timestamp);
    
    html += `  <div class="note">\n`;
    html += `    <h2 class="note-title">${escapeHtml(title)}</h2>\n`;
    
    if (includeMetadata) {
      html += `    <div class="note-meta">Created: ${timestamp.full}</div>\n`;
    }
    
    html += `    <div class="note-content">${escapeHtml(note.content)}</div>\n`;
    
    if (note.tags && note.tags.length > 0) {
      html += `    <div class="tags">\n`;
      note.tags.forEach(tag => {
        html += `      <span class="tag">#${escapeHtml(tag)}</span>\n`;
      });
      html += `    </div>\n`;
    }
    
    html += `  </div>\n`;
  });
  
  html += `</body>
</html>`;
  
  return html;
};

/**
 * Export notes as plain text
 */
const exportAsPlainText = (notes, includeMetadata) => {
  let content = 'MY NOTES\n' + '='.repeat(50) + '\n\n';
  
  if (includeMetadata) {
    content += `Exported: ${new Date().toLocaleString()}\n`;
    content += `Total Notes: ${notes.length}\n\n`;
    content += '-'.repeat(50) + '\n\n';
  }
  
  notes.forEach((note, index) => {
    const title = note.title || extractTitleFromContent(note.content);
    const timestamp = formatTimestamp(note.timestamp);
    const plainContent = extractPlainText(note.content);
    
    content += `${title.toUpperCase()}\n`;
    
    if (includeMetadata) {
      content += `Created: ${timestamp.full}\n`;
      
      if (note.tags && note.tags.length > 0) {
        content += `Tags: ${note.tags.map(tag => `#${tag}`).join(', ')}\n`;
      }
    }
    
    content += '\n' + plainContent + '\n\n';
    
    if (index < notes.length - 1) {
      content += '-'.repeat(30) + '\n\n';
    }
  });
  
  return content;
};

/**
 * Extract title from note content
 */
const extractTitleFromContent = (content) => {
  const firstLine = content.split('\n')[0].trim();
  
  // Check for markdown header
  if (firstLine.startsWith('#')) {
    return firstLine.replace(/^#+\s*/, '');
  }
  
  // Use first sentence or first 50 characters
  const firstSentence = content.split('.')[0].trim();
  return firstSentence.length > 50 
    ? firstSentence.substring(0, 47) + '...'
    : firstSentence || 'Untitled Note';
};

/**
 * Download file to user's computer
 */
const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.style.display = 'none';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Clean up the URL
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

/**
 * Escape HTML special characters
 */
const escapeHtml = (text) => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};

/**
 * Copy notes to clipboard
 * @param {Array} notes - Notes to copy
 * @param {string} format - Format for clipboard
 * @returns {Promise<boolean>} Success status
 */
export const copyNotesToClipboard = async (notes, format = 'markdown') => {
  try {
    const exportResult = await exportNotes(notes, {
      format,
      downloadAsFile: false,
      includeMetadata: false
    });
    
    await navigator.clipboard.writeText(exportResult.content);
    return true;
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    return false;
  }
};

/**
 * Share notes via Web Share API if available
 * @param {Array} notes - Notes to share
 * @param {Object} options - Share options
 * @returns {Promise<boolean>} Success status
 */
export const shareNotes = async (notes, options = {}) => {
  if (!navigator.share) {
    return false;
  }
  
  try {
    const exportResult = await exportNotes(notes, {
      format: 'markdown',
      downloadAsFile: false,
      includeMetadata: false,
      ...options
    });
    
    await navigator.share({
      title: `My Notes${options.lessonId ? ` - ${options.lessonId}` : ''}`,
      text: exportResult.content,
      ...(options.url && { url: options.url })
    });
    
    return true;
  } catch (error) {
    console.error('Failed to share notes:', error);
    return false;
  }
};