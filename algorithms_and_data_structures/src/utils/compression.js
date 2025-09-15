/**
 * Data Compression Utilities
 * Handles compression and decompression for storage optimization
 */

/**
 * Compress data using LZ-string algorithm (browser-compatible)
 */
export async function compressData(data) {
  if (typeof data !== 'string') {
    data = JSON.stringify(data);
  }

  try {
    // Use browser's native compression if available
    if (typeof window !== 'undefined' && window.CompressionStream) {
      return await compressWithNative(data);
    }
    
    // Fallback to LZ-string style compression
    return compressLZString(data);
  } catch (error) {
    console.error('Compression failed:', error);
    throw new Error(`Compression failed: ${error.message}`);
  }
}

/**
 * Decompress data
 */
export async function decompressData(compressedData) {
  if (!compressedData) return '';

  try {
    // Try native decompression first
    if (typeof window !== 'undefined' && window.DecompressionStream && isNativeCompressed(compressedData)) {
      return await decompressWithNative(compressedData);
    }
    
    // Fallback to LZ-string decompression
    return decompressLZString(compressedData);
  } catch (error) {
    console.error('Decompression failed:', error);
    throw new Error(`Decompression failed: ${error.message}`);
  }
}

/**
 * Native browser compression using CompressionStream
 */
async function compressWithNative(data) {
  const stream = new CompressionStream('gzip');
  const writer = stream.writable.getWriter();
  const reader = stream.readable.getReader();

  // Write data
  await writer.write(new TextEncoder().encode(data));
  await writer.close();

  // Read compressed data
  const chunks = [];
  let done = false;

  while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = readerDone;
    if (value) {
      chunks.push(value);
    }
  }

  // Convert to base64 for storage
  const compressedArray = new Uint8Array(chunks.reduce((acc, chunk) => acc + chunk.length, 0));
  let offset = 0;
  chunks.forEach(chunk => {
    compressedArray.set(chunk, offset);
    offset += chunk.length;
  });

  return 'NATIVE:' + btoa(String.fromCharCode(...compressedArray));
}

/**
 * Native browser decompression using DecompressionStream
 */
async function decompressWithNative(compressedData) {
  const base64Data = compressedData.substring(7); // Remove 'NATIVE:' prefix
  const binaryString = atob(base64Data);
  const bytes = new Uint8Array(binaryString.length);
  
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  const stream = new DecompressionStream('gzip');
  const writer = stream.writable.getWriter();
  const reader = stream.readable.getReader();

  // Write compressed data
  await writer.write(bytes);
  await writer.close();

  // Read decompressed data
  const chunks = [];
  let done = false;

  while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = readerDone;
    if (value) {
      chunks.push(value);
    }
  }

  // Convert back to string
  const decompressedArray = new Uint8Array(chunks.reduce((acc, chunk) => acc + chunk.length, 0));
  let offset = 0;
  chunks.forEach(chunk => {
    decompressedArray.set(chunk, offset);
    offset += chunk.length;
  });

  return new TextDecoder().decode(decompressedArray);
}

/**
 * Check if data was compressed with native compression
 */
function isNativeCompressed(data) {
  return typeof data === 'string' && data.startsWith('NATIVE:');
}

/**
 * LZ-string style compression (simplified implementation)
 */
function compressLZString(data) {
  if (!data) return '';

  const dictionary = {};
  const result = [];
  let dictSize = 256;
  let current = '';
  
  // Initialize dictionary with single characters
  for (let i = 0; i < 256; i++) {
    dictionary[String.fromCharCode(i)] = i;
  }

  for (let i = 0; i < data.length; i++) {
    const char = data[i];
    const combined = current + char;

    if (dictionary.hasOwnProperty(combined)) {
      current = combined;
    } else {
      result.push(dictionary[current]);
      dictionary[combined] = dictSize++;
      current = char;
    }
  }

  if (current !== '') {
    result.push(dictionary[current]);
  }

  // Convert to base64 encoded string
  return 'LZ:' + btoa(JSON.stringify(result));
}

/**
 * LZ-string style decompression
 */
function decompressLZString(compressedData) {
  if (!compressedData || !compressedData.startsWith('LZ:')) {
    return compressedData; // Return as-is if not LZ compressed
  }

  try {
    const base64Data = compressedData.substring(3); // Remove 'LZ:' prefix
    const data = JSON.parse(atob(base64Data));
    
    if (!Array.isArray(data) || data.length === 0) {
      return '';
    }

    const dictionary = {};
    const result = [];
    let dictSize = 256;
    
    // Initialize dictionary with single characters
    for (let i = 0; i < 256; i++) {
      dictionary[i] = String.fromCharCode(i);
    }

    let previous = dictionary[data[0]];
    result.push(previous);

    for (let i = 1; i < data.length; i++) {
      let current;
      
      if (dictionary.hasOwnProperty(data[i])) {
        current = dictionary[data[i]];
      } else if (data[i] === dictSize) {
        current = previous + previous[0];
      } else {
        throw new Error('Invalid compressed data');
      }

      result.push(current);
      dictionary[dictSize++] = previous + current[0];
      previous = current;
    }

    return result.join('');
  } catch (error) {
    console.error('LZ decompression failed:', error);
    throw error;
  }
}

/**
 * Calculate compression ratio
 */
export function getCompressionRatio(originalSize, compressedSize) {
  if (!originalSize || originalSize === 0) return 0;
  return (1 - compressedSize / originalSize) * 100;
}

/**
 * Estimate compression benefit
 */
export function estimateCompressionBenefit(data) {
  if (typeof data !== 'string') {
    data = JSON.stringify(data);
  }

  const originalSize = data.length * 2; // UTF-16 encoding
  
  // Simple heuristic based on repetition and patterns
  const uniqueChars = new Set(data).size;
  const repetitionFactor = data.length / uniqueChars;
  
  let estimatedRatio = 0;
  
  if (repetitionFactor > 10) {
    estimatedRatio = 70; // High compression expected
  } else if (repetitionFactor > 5) {
    estimatedRatio = 50; // Medium compression
  } else if (repetitionFactor > 2) {
    estimatedRatio = 30; // Low compression
  } else {
    estimatedRatio = 10; // Very low compression
  }

  const estimatedCompressedSize = originalSize * (1 - estimatedRatio / 100);

  return {
    originalSize,
    estimatedCompressedSize,
    estimatedRatio,
    worthCompressing: estimatedRatio > 20 && originalSize > 1024 // Worth it if >20% reduction and >1KB
  };
}

/**
 * Smart compression that decides whether to compress based on data characteristics
 */
export async function smartCompress(data, threshold = 1024) {
  const dataStr = typeof data === 'string' ? data : JSON.stringify(data);
  
  if (dataStr.length < threshold) {
    return { data: dataStr, compressed: false };
  }

  const benefit = estimateCompressionBenefit(dataStr);
  
  if (!benefit.worthCompressing) {
    return { data: dataStr, compressed: false };
  }

  try {
    const compressedData = await compressData(dataStr);
    const actualRatio = getCompressionRatio(dataStr.length * 2, compressedData.length * 2);
    
    // Only use compression if we achieved significant reduction
    if (actualRatio > 15) {
      return { 
        data: compressedData, 
        compressed: true, 
        originalSize: dataStr.length * 2,
        compressedSize: compressedData.length * 2,
        ratio: actualRatio
      };
    }
  } catch (error) {
    console.warn('Compression failed, using uncompressed data:', error);
  }

  return { data: dataStr, compressed: false };
}

/**
 * Smart decompression that handles both compressed and uncompressed data
 */
export async function smartDecompress(data, isCompressed = null) {
  if (!data) return '';

  // Auto-detect compression if not specified
  if (isCompressed === null) {
    isCompressed = typeof data === 'string' && (data.startsWith('LZ:') || data.startsWith('NATIVE:'));
  }

  if (!isCompressed) {
    return typeof data === 'string' ? data : JSON.stringify(data);
  }

  try {
    return await decompressData(data);
  } catch (error) {
    console.error('Smart decompression failed:', error);
    // Return original data if decompression fails
    return typeof data === 'string' ? data : JSON.stringify(data);
  }
}

/**
 * Benchmark compression performance
 */
export async function benchmarkCompression(testData) {
  const dataStr = typeof testData === 'string' ? testData : JSON.stringify(testData);
  const results = {
    originalSize: dataStr.length * 2,
    methods: {}
  };

  // Test LZ compression
  try {
    const start = performance.now();
    const compressed = compressLZString(dataStr);
    const compressTime = performance.now() - start;
    
    const decompressStart = performance.now();
    const decompressed = decompressLZString(compressed);
    const decompressTime = performance.now() - decompressStart;
    
    results.methods.lz = {
      compressedSize: compressed.length * 2,
      ratio: getCompressionRatio(results.originalSize, compressed.length * 2),
      compressTime,
      decompressTime,
      success: decompressed === dataStr
    };
  } catch (error) {
    results.methods.lz = { error: error.message };
  }

  // Test native compression if available
  if (typeof window !== 'undefined' && window.CompressionStream) {
    try {
      const start = performance.now();
      const compressed = await compressWithNative(dataStr);
      const compressTime = performance.now() - start;
      
      const decompressStart = performance.now();
      const decompressed = await decompressWithNative(compressed);
      const decompressTime = performance.now() - decompressStart;
      
      results.methods.native = {
        compressedSize: compressed.length * 2,
        ratio: getCompressionRatio(results.originalSize, compressed.length * 2),
        compressTime,
        decompressTime,
        success: decompressed === dataStr
      };
    } catch (error) {
      results.methods.native = { error: error.message };
    }
  }

  return results;
}