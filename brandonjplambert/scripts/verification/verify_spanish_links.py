"""
Production-ready script for verifying and enriching Spanish social media links
Usage: python verify_spanish_links.py input.csv --output verified_data.json --api-keys keys.json
"""

import asyncio
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import logging

from spanish_links_verifier import (
    DatasetVerifier, LinkMetadata, Platform, VerificationStatus
)
# Add parent directories to path for cross-directory imports
sys.path.append(str(Path(__file__).parent.parent / "data-processing"))

from advanced_enrichment import (
    ContentAnalyzer, EmailFinder, LocationExtractor,
    SemanticMatcher, DataQualityScorer, BatchProcessor
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('verification.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SpanishLinksProcessor:
    """Main processor for Spanish links verification and enrichment"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.verifier = DatasetVerifier(
            youtube_api_key=config.get('youtube_api_key')
        )
        self.batch_processor = BatchProcessor(
            batch_size=config.get('batch_size', 50),
            max_concurrent=config.get('max_concurrent', 10)
        )
        self.quality_scorer = DataQualityScorer()
        self.results = []
        self.statistics = {
            'total_processed': 0,
            'verified_active': 0,
            'spanish_confirmed': 0,
            'high_quality': 0,
            'emails_found': 0,
            'locations_found': 0,
            'cross_platform_links': 0
        }
    
    async def process_file(self, input_file: str, output_file: str):
        """Process input file and save results"""
        logger.info(f"Starting processing of {input_file}")
        
        urls = self._load_input_file(input_file)
        logger.info(f"Loaded {len(urls)} URLs from input file")
        
        results = await self.verifier.verify_and_enrich(
            urls, 
            batch_size=self.config.get('batch_size', 50)
        )
        
        enriched_results = await self._enrich_results(results)
        
        self._calculate_statistics(enriched_results)
        
        self._save_results(enriched_results, output_file)
        
        self._print_summary()
        
        return enriched_results
    
    def _load_input_file(self, input_file: str) -> List[str]:
        """Load URLs from various input formats"""
        file_path = Path(input_file)
        urls = []
        
        if file_path.suffix == '.csv':
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip():
                        urls.append(row[0].strip())
        
        elif file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    urls = [item if isinstance(item, str) else item.get('url', '') 
                           for item in data]
                elif isinstance(data, dict):
                    urls = data.get('urls', [])
        
        elif file_path.suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        
        elif file_path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            url_column = None
            for col in df.columns:
                if 'url' in col.lower() or 'link' in col.lower():
                    url_column = col
                    break
            if url_column:
                urls = df[url_column].dropna().tolist()
            else:
                urls = df.iloc[:, 0].dropna().tolist()
        
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        urls = [url for url in urls if url and isinstance(url, str)]
        
        return urls
    
    async def _enrich_results(self, results: List[LinkMetadata]) -> List[Dict[str, Any]]:
        """Enrich results with additional analysis"""
        enriched = []
        
        for metadata in results:
            enriched_data = self._metadata_to_dict(metadata)
            
            if metadata.bio:
                categories = ContentAnalyzer.categorize_content(metadata.bio)
                enriched_data['content_categories'] = categories
                
                hashtags = ContentAnalyzer.extract_hashtags(metadata.bio)
                enriched_data['hashtags'] = hashtags
                
                emails = EmailFinder.find_emails(metadata.bio)
                if emails:
                    enriched_data['discovered_emails'] = emails
                    self.statistics['emails_found'] += 1
            
            if metadata.bio or metadata.display_name:
                location = LocationExtractor.extract_location(
                    f"{metadata.bio or ''} {metadata.display_name or ''}"
                )
                if location:
                    enriched_data['extracted_location'] = location
                    self.statistics['locations_found'] += 1
            
            if metadata.follower_count and metadata.post_count:
                engagement = ContentAnalyzer.calculate_engagement_metrics(
                    metadata.follower_count,
                    0,
                    0,
                    metadata.post_count
                )
                enriched_data['engagement_metrics'] = engagement
            
            quality_scores = self.quality_scorer.calculate_comprehensive_score(enriched_data)
            enriched_data['quality_scores'] = quality_scores
            
            if metadata.external_links:
                self.statistics['cross_platform_links'] += 1
            
            enriched.append(enriched_data)
        
        return enriched
    
    def _metadata_to_dict(self, metadata: LinkMetadata) -> Dict[str, Any]:
        """Convert LinkMetadata to dictionary"""
        return {
            'url': metadata.url,
            'platform': metadata.platform.value,
            'username': metadata.username,
            'display_name': metadata.display_name,
            'bio': metadata.bio,
            'follower_count': metadata.follower_count,
            'following_count': metadata.following_count,
            'post_count': metadata.post_count,
            'verification_status': metadata.verification_status.value,
            'is_spanish': metadata.is_spanish,
            'language_confidence': metadata.language_confidence,
            'location': metadata.location,
            'external_links': metadata.external_links,
            'email': metadata.email,
            'phone': metadata.phone,
            'verified_badge': metadata.verified_badge,
            'last_verified': metadata.last_verified.isoformat() if metadata.last_verified else None,
            'quality_score': metadata.quality_score,
            'enrichment_sources': metadata.enrichment_sources,
            'error_message': metadata.error_message
        }
    
    def _calculate_statistics(self, results: List[Dict[str, Any]]):
        """Calculate processing statistics"""
        self.statistics['total_processed'] = len(results)
        
        for result in results:
            if result['verification_status'] == 'active':
                self.statistics['verified_active'] += 1
            
            if result.get('is_spanish'):
                self.statistics['spanish_confirmed'] += 1
            
            quality_score = result.get('quality_scores', {}).get('overall', 0)
            if quality_score > 0.7:
                self.statistics['high_quality'] += 1
    
    def _save_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save results to output file"""
        output_path = Path(output_file)
        
        if output_path.suffix == '.json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'processed_at': datetime.now().isoformat(),
                        'total_records': len(results),
                        'statistics': self.statistics
                    },
                    'results': results
                }, f, ensure_ascii=False, indent=2)
        
        elif output_path.suffix == '.csv':
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False, encoding='utf-8')
        
        elif output_path.suffix in ['.xlsx', '.xls']:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df = pd.DataFrame(results)
                df.to_excel(writer, sheet_name='Verified Links', index=False)
                
                stats_df = pd.DataFrame([self.statistics])
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        else:
            raise ValueError(f"Unsupported output format: {output_path.suffix}")
        
        logger.info(f"Results saved to {output_path}")
    
    def _print_summary(self):
        """Print processing summary"""
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        total = self.statistics['total_processed']
        if total > 0:
            print(f"Total URLs Processed: {total}")
            print(f"Active Accounts: {self.statistics['verified_active']} "
                  f"({self.statistics['verified_active']/total*100:.1f}%)")
            print(f"Spanish Confirmed: {self.statistics['spanish_confirmed']} "
                  f"({self.statistics['spanish_confirmed']/total*100:.1f}%)")
            print(f"High Quality (>70%): {self.statistics['high_quality']} "
                  f"({self.statistics['high_quality']/total*100:.1f}%)")
            print(f"Emails Discovered: {self.statistics['emails_found']}")
            print(f"Locations Extracted: {self.statistics['locations_found']}")
            print(f"Cross-Platform Links: {self.statistics['cross_platform_links']}")
        
        print("="*60 + "\n")


def load_config(config_file: str = None) -> Dict[str, Any]:
    """Load configuration from file or use defaults"""
    default_config = {
        'batch_size': 50,
        'max_concurrent': 10,
        'youtube_api_key': None,
        'cache_ttl': 3600,
        'output_format': 'json',
        'quality_threshold': 0.7,
        'language_threshold': 0.5
    }
    
    if config_file and Path(config_file).exists():
        with open(config_file, 'r') as f:
            user_config = json.load(f)
            default_config.update(user_config)
    
    return default_config


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Verify and enrich Spanish social media links'
    )
    parser.add_argument(
        'input_file',
        help='Input file containing URLs (CSV, JSON, TXT, or Excel)'
    )
    parser.add_argument(
        '--output',
        default='verified_results.json',
        help='Output file for results (default: verified_results.json)'
    )
    parser.add_argument(
        '--config',
        help='Configuration file (JSON)'
    )
    parser.add_argument(
        '--youtube-key',
        help='YouTube API key for enhanced verification'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Batch size for processing (default: 50)'
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=10,
        help='Maximum concurrent requests (default: 10)'
    )
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    if args.youtube_key:
        config['youtube_api_key'] = args.youtube_key
    if args.batch_size:
        config['batch_size'] = args.batch_size
    if args.max_concurrent:
        config['max_concurrent'] = args.max_concurrent
    
    if not Path(args.input_file).exists():
        logger.error(f"Input file not found: {args.input_file}")
        sys.exit(1)
    
    processor = SpanishLinksProcessor(config)
    
    try:
        asyncio.run(processor.process_file(args.input_file, args.output))
        logger.info("Processing completed successfully")
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()