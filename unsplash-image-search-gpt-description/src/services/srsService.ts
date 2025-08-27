import { VocabularyItem, SRSReviewSession, ReviewType, MasteryLevel } from '../types';

/**
 * Spaced Repetition System (SRS) Service
 * 
 * Implements a sophisticated spaced repetition algorithm based on:
 * - SuperMemo SM-2 algorithm
 * - Anki's modifications
 * - Custom adjustments for vocabulary learning
 */

export interface SRSCalculationResult {
  ease: number;
  interval: number;
  masteryLevel: MasteryLevel;
  nextReviewAt: Date;
  difficultyAdjustment?: number;
}

export interface SRSConfig {
  // Base intervals (in days)
  initialInterval: number;
  graduatingInterval: number;
  easyInterval: number;
  
  // Ease factors
  initialEase: number;
  minEase: number;
  maxEase: number;
  
  // Adjustments
  easyBonus: number;
  hardPenalty: number;
  againPenalty: number;
  
  // Learning steps (in minutes)
  learningSteps: number[];
  relearningSteps: number[];
  
  // Mastery thresholds
  masteryThreshold: number;
  retentionTarget: number;
}

// Default SRS configuration optimized for vocabulary learning
const DEFAULT_CONFIG: SRSConfig = {
  initialInterval: 1,
  graduatingInterval: 4,
  easyInterval: 7,
  
  initialEase: 2.5,
  minEase: 1.3,
  maxEase: 4.0,
  
  easyBonus: 0.15,
  hardPenalty: 0.15,
  againPenalty: 0.20,
  
  learningSteps: [1, 10, 60], // 1 min, 10 min, 1 hour
  relearningSteps: [10, 60],   // 10 min, 1 hour
  
  masteryThreshold: 21,        // Days interval for mastery
  retentionTarget: 0.85        // 85% retention target
};

class SRSService {
  private config: SRSConfig;
  
  constructor(config: Partial<SRSConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Calculate the next review parameters based on performance
   */
  calculateNextReview(
    item: VocabularyItem,
    performance: 'again' | 'hard' | 'good' | 'easy',
    responseTime?: number
  ): SRSCalculationResult {
    const now = new Date();
    let { ease, interval, masteryLevel } = item;
    
    // Initialize defaults for new items
    if (ease === 0 || !ease) ease = this.config.initialEase;
    if (interval === 0 || !interval) interval = this.config.initialInterval;
    
    // Handle different performance levels
    switch (performance) {
      case 'again':
        return this.handleAgainResponse(item, now);
      case 'hard':
        return this.handleHardResponse(item, now);
      case 'good':
        return this.handleGoodResponse(item, now);
      case 'easy':
        return this.handleEasyResponse(item, now);
      default:
        throw new Error(`Invalid performance: ${performance}`);
    }
  }

  /**
   * Handle 'Again' response - card was forgotten
   */
  private handleAgainResponse(item: VocabularyItem, now: Date): SRSCalculationResult {
    const newEase = Math.max(
      this.config.minEase,
      item.ease - this.config.againPenalty
    );
    
    // Reset to learning if was in review/mastered
    const masteryLevel = item.masteryLevel === MasteryLevel.NEW 
      ? MasteryLevel.NEW 
      : MasteryLevel.LEARNING;
    
    // Use relearning steps or reset to initial
    const interval = masteryLevel === MasteryLevel.LEARNING 
      ? this.config.relearningSteps[0] / (24 * 60) // Convert minutes to days
      : this.config.initialInterval;
    
    const nextReviewAt = this.addDaysToDate(now, interval);
    
    return {
      ease: newEase,
      interval,
      masteryLevel,
      nextReviewAt,
      difficultyAdjustment: Math.min(10, item.difficulty + 1)
    };
  }

  /**
   * Handle 'Hard' response - card was difficult but remembered
   */
  private handleHardResponse(item: VocabularyItem, now: Date): SRSCalculationResult {
    const newEase = Math.max(
      this.config.minEase,
      item.ease - this.config.hardPenalty
    );
    
    let interval: number;
    let masteryLevel = item.masteryLevel;
    
    if (item.masteryLevel === MasteryLevel.NEW) {
      // Move to learning but with shorter interval
      interval = this.config.initialInterval * 0.8;
      masteryLevel = MasteryLevel.LEARNING;
    } else {
      // Reduce interval slightly
      interval = item.interval * 1.2;
    }
    
    const nextReviewAt = this.addDaysToDate(now, interval);
    
    return {
      ease: newEase,
      interval,
      masteryLevel,
      nextReviewAt
    };
  }

  /**
   * Handle 'Good' response - normal successful recall
   */
  private handleGoodResponse(item: VocabularyItem, now: Date): SRSCalculationResult {
    let interval: number;
    let masteryLevel = item.masteryLevel;
    const ease = item.ease; // No ease change for good response
    
    if (item.masteryLevel === MasteryLevel.NEW) {
      interval = this.config.graduatingInterval;
      masteryLevel = MasteryLevel.LEARNING;
    } else if (item.masteryLevel === MasteryLevel.LEARNING && item.streak >= 2) {
      interval = this.config.graduatingInterval;
      masteryLevel = MasteryLevel.REVIEW;
    } else {
      // Apply ease factor
      interval = item.interval * ease;
      
      // Check for mastery
      if (interval >= this.config.masteryThreshold && item.streak >= 5) {
        masteryLevel = MasteryLevel.MASTERED;
      }
    }
    
    const nextReviewAt = this.addDaysToDate(now, interval);
    
    return {
      ease,
      interval,
      masteryLevel,
      nextReviewAt
    };
  }

  /**
   * Handle 'Easy' response - very easy recall
   */
  private handleEasyResponse(item: VocabularyItem, now: Date): SRSCalculationResult {
    const newEase = Math.min(
      this.config.maxEase,
      item.ease + this.config.easyBonus
    );
    
    let interval: number;
    let masteryLevel = item.masteryLevel;
    
    if (item.masteryLevel === MasteryLevel.NEW) {
      interval = this.config.easyInterval;
      masteryLevel = MasteryLevel.REVIEW;
    } else {
      // Apply ease factor with bonus
      interval = item.interval * newEase * 1.3; // Additional easy bonus
      
      // Fast track to mastery
      if (interval >= this.config.masteryThreshold) {
        masteryLevel = MasteryLevel.MASTERED;
      }
    }
    
    const nextReviewAt = this.addDaysToDate(now, interval);
    
    return {
      ease: newEase,
      interval,
      masteryLevel,
      nextReviewAt,
      difficultyAdjustment: Math.max(1, item.difficulty - 1)
    };
  }

  /**
   * Get items due for review
   */
  getDueItems(items: VocabularyItem[]): VocabularyItem[] {
    const now = new Date();
    
    return items.filter(item => {
      if (!item.nextReviewAt) {
        return item.masteryLevel === MasteryLevel.NEW;
      }
      return new Date(item.nextReviewAt) <= now;
    }).sort((a, b) => {
      // Prioritize by due date, then by mastery level
      const aDate = a.nextReviewAt ? new Date(a.nextReviewAt) : new Date(0);
      const bDate = b.nextReviewAt ? new Date(b.nextReviewAt) : new Date(0);
      
      if (aDate.getTime() !== bDate.getTime()) {
        return aDate.getTime() - bDate.getTime();
      }
      
      // Prioritize new and learning items
      const masteryOrder = {
        [MasteryLevel.NEW]: 0,
        [MasteryLevel.LEARNING]: 1,
        [MasteryLevel.REVIEW]: 2,
        [MasteryLevel.MASTERED]: 3
      };
      
      return masteryOrder[a.masteryLevel] - masteryOrder[b.masteryLevel];
    });
  }

  // Utility methods
  private addDaysToDate(date: Date, days: number): Date {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  }

  private shuffleArray<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }
}

// Export singleton instance
export const srsService = new SRSService();

// Export class for custom configurations
export { SRSService };