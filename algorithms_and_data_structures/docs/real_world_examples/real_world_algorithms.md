# Real-World Algorithms: Complete Pseudocode Examples

## Table of Contents
1. [Biology & Medicine](#biology--medicine)
2. [Economics & Trading](#economics--trading)
3. [Creative Arts](#creative-arts)
4. [Environmental Science](#environmental-science)
5. [Linguistics](#linguistics)
6. [Sports Analytics](#sports-analytics)
7. [Everyday Applications](#everyday-applications)

---

## Biology & Medicine

### 🧬 DNA Sequence Alignment (Needleman-Wunsch Algorithm)
**Purpose**: Finds optimal alignment between two DNA sequences to identify mutations
**Real Usage**: BLAST tool, genetic disease diagnosis, evolutionary studies

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Global DNA Sequence Alignment                          ║
║ Time Complexity: O(m × n)  | Space Complexity: O(m × n)          ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  seq1: string        # First DNA sequence (e.g., "ATCG")
  seq2: string        # Second DNA sequence (e.g., "ACCG")
  match_score: int    # Points for matching nucleotides (typically +2)
  mismatch: int       # Penalty for mismatches (typically -1)
  gap_penalty: int    # Penalty for insertions/deletions (typically -1)

▶ OUTPUT:
  alignment_score: int     # Optimal alignment score
  aligned_seq1: string     # First sequence with gaps inserted
  aligned_seq2: string     # Second sequence with gaps inserted

▶ DATA STRUCTURES:
  score_matrix[m+1][n+1]: 2D array  # Dynamic programming table
  traceback[m+1][n+1]: 2D array     # Path reconstruction matrix

▶ ALGORITHM:
FUNCTION alignDNA(seq1, seq2, match_score, mismatch, gap_penalty):
    
    ═══ STEP 1: Initialize matrices ═══
    m ← length(seq1)
    n ← length(seq2)
    
    CREATE score_matrix[m+1][n+1]
    CREATE traceback[m+1][n+1]
    
    # Initialize first row (seq1 gaps)
    FOR j FROM 0 TO n:
        score_matrix[0][j] ← j × gap_penalty
        traceback[0][j] ← "LEFT"  # Indicates insertion in seq1
    
    # Initialize first column (seq2 gaps)
    FOR i FROM 0 TO m:
        score_matrix[i][0] ← i × gap_penalty
        traceback[i][0] ← "UP"    # Indicates insertion in seq2
    
    traceback[0][0] ← "START"
    
    ═══ STEP 2: Fill scoring matrix (Dynamic Programming) ═══
    FOR i FROM 1 TO m:
        FOR j FROM 1 TO n:
            
            # Calculate three possible scores
            IF seq1[i-1] == seq2[j-1]:
                diagonal_score ← score_matrix[i-1][j-1] + match_score
            ELSE:
                diagonal_score ← score_matrix[i-1][j-1] + mismatch
            
            up_score ← score_matrix[i-1][j] + gap_penalty    # Gap in seq2
            left_score ← score_matrix[i][j-1] + gap_penalty  # Gap in seq1
            
            # Choose maximum score
            max_score ← MAX(diagonal_score, up_score, left_score)
            score_matrix[i][j] ← max_score
            
            # Record direction for traceback
            IF max_score == diagonal_score:
                traceback[i][j] ← "DIAGONAL"
            ELSE IF max_score == up_score:
                traceback[i][j] ← "UP"
            ELSE:
                traceback[i][j] ← "LEFT"
    
    ═══ STEP 3: Traceback to build alignment ═══
    aligned_seq1 ← ""
    aligned_seq2 ← ""
    i ← m
    j ← n
    
    WHILE i > 0 OR j > 0:
        current_direction ← traceback[i][j]
        
        IF current_direction == "DIAGONAL":
            aligned_seq1 ← seq1[i-1] + aligned_seq1
            aligned_seq2 ← seq2[j-1] + aligned_seq2
            i ← i - 1
            j ← j - 1
        ELSE IF current_direction == "UP":
            aligned_seq1 ← seq1[i-1] + aligned_seq1
            aligned_seq2 ← "-" + aligned_seq2  # Gap character
            i ← i - 1
        ELSE:  # LEFT
            aligned_seq1 ← "-" + aligned_seq1  # Gap character
            aligned_seq2 ← seq2[j-1] + aligned_seq2
            j ← j - 1
    
    RETURN score_matrix[m][n], aligned_seq1, aligned_seq2
END FUNCTION

▶ EXAMPLE EXECUTION:
  Input: seq1="ATCG", seq2="ACG"
  Output: score=4, "ATCG", "A-CG"
```

---

## Economics & Trading

### 💹 Moving Average Crossover Trading Algorithm
**Purpose**: Generates buy/sell signals based on moving average crossovers
**Real Usage**: Goldman Sachs, JPMorgan algorithmic trading systems

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Dual Moving Average Trading Strategy                   ║
║ Risk Level: Medium | Backtest Required: Yes                       ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  price_history: array[float]  # Historical stock prices
  short_window: int            # Fast MA period (e.g., 50 days)
  long_window: int             # Slow MA period (e.g., 200 days)
  capital: float               # Starting capital in USD
  risk_percent: float          # Max risk per trade (e.g., 0.02 = 2%)
  
▶ OUTPUT:
  signals: array[string]       # "BUY", "SELL", or "HOLD" signals
  portfolio_value: float       # Final portfolio value
  trades: array[Trade]         # Detailed trade history

▶ DATA STRUCTURES:
  Trade: {
    timestamp: datetime
    action: string           # "BUY" or "SELL"
    price: float
    shares: int
    reason: string
  }

▶ ALGORITHM:
FUNCTION tradingStrategy(price_history, short_window, long_window, capital, risk_percent):
    
    ═══ STEP 1: Calculate Moving Averages ═══
    n ← length(price_history)
    short_ma ← array[n]
    long_ma ← array[n]
    
    # Simple Moving Average calculation
    FOR i FROM 0 TO n-1:
        IF i < short_window - 1:
            short_ma[i] ← NULL  # Not enough data
        ELSE:
            sum ← 0
            FOR j FROM (i - short_window + 1) TO i:
                sum ← sum + price_history[j]
            short_ma[i] ← sum / short_window
        
        IF i < long_window - 1:
            long_ma[i] ← NULL  # Not enough data
        ELSE:
            sum ← 0
            FOR j FROM (i - long_window + 1) TO i:
                sum ← sum + price_history[j]
            long_ma[i] ← sum / long_window
    
    ═══ STEP 2: Generate Trading Signals ═══
    signals ← array[n]
    position ← "OUT"  # Current position status
    shares_held ← 0
    cash ← capital
    trades ← []
    
    FOR i FROM long_window TO n-1:  # Start when both MAs available
        previous_short ← short_ma[i-1]
        previous_long ← long_ma[i-1]
        current_short ← short_ma[i]
        current_long ← long_ma[i]
        current_price ← price_history[i]
        
        # Golden Cross: Short MA crosses above Long MA → BUY
        IF previous_short ≤ previous_long AND current_short > current_long:
            IF position == "OUT":
                # Calculate position size based on risk
                stop_loss ← current_price × 0.95  # 5% stop loss
                risk_amount ← cash × risk_percent
                shares_to_buy ← FLOOR(risk_amount / (current_price - stop_loss))
                shares_to_buy ← MIN(shares_to_buy, FLOOR(cash / current_price))
                
                IF shares_to_buy > 0:
                    signals[i] ← "BUY"
                    cash ← cash - (shares_to_buy × current_price)
                    shares_held ← shares_to_buy
                    position ← "LONG"
                    
                    ADD Trade({
                        timestamp: i,
                        action: "BUY",
                        price: current_price,
                        shares: shares_to_buy,
                        reason: "Golden Cross"
                    }) TO trades
                ELSE:
                    signals[i] ← "HOLD"  # Insufficient funds
            ELSE:
                signals[i] ← "HOLD"  # Already in position
        
        # Death Cross: Short MA crosses below Long MA → SELL
        ELSE IF previous_short ≥ previous_long AND current_short < current_long:
            IF position == "LONG":
                signals[i] ← "SELL"
                cash ← cash + (shares_held × current_price)
                
                ADD Trade({
                    timestamp: i,
                    action: "SELL",
                    price: current_price,
                    shares: shares_held,
                    reason: "Death Cross"
                }) TO trades
                
                shares_held ← 0
                position ← "OUT"
            ELSE:
                signals[i] ← "HOLD"
        
        # No crossover → Hold position
        ELSE:
            signals[i] ← "HOLD"
    
    ═══ STEP 3: Calculate Final Portfolio Value ═══
    portfolio_value ← cash + (shares_held × price_history[n-1])
    
    RETURN signals, portfolio_value, trades
END FUNCTION

▶ RISK MANAGEMENT NOTES:
  • Always use stop-loss orders in production
  • Backtest on 5+ years of historical data
  • Consider transaction costs (typically 0.1% per trade)
  • Monitor for false signals in sideways markets
```

---

## Creative Arts

### 🎵 Markov Chain Music Generation
**Purpose**: Generates musical melodies based on learned patterns
**Real Usage**: AIVA, Google Magenta, Spotify's recommendation engine

```pseudocode
╔════════════════════════════════════════════════════════════════════╗
║ ALGORITHM: Probabilistic Music Composition                        ║
║ Style: Classical/Jazz | Output: MIDI-compatible                   ║
╚════════════════════════════════════════════════════════════════════╝

▶ INPUT PARAMETERS:
  training_melodies: array[array[Note]]  # Corpus of existing music
  order: int                             # Markov chain order (typically 2-3)
  length: int                            # Desired melody length in notes
  key_signature: string                  # Musical key (e.g., "C_major")
  tempo: int                             # Beats per minute

▶ OUTPUT:
  generated_melody: array[Note]          # New musical composition
  harmony: array[Chord]                  # Accompanying chord progression

▶ DATA STRUCTURES:
  Note: {
    pitch: int         # MIDI note number (0-127, 60=Middle C)
    duration: float    # Note length in beats (0.25=sixteenth, 1=quarter)
    velocity: int      # Volume/intensity (0-127)
  }
  
  TransitionMatrix: {
    key: tuple[Note]   # Previous note sequence
    value: map[Note, probability]  # Next note probabilities
  }

▶ ALGORITHM:
FUNCTION generateMusic(training_melodies, order, length, key_signature, tempo):
    
    ═══ STEP 1: Build Transition Probability Matrix ═══
    transitions ← new HashMap()
    
    FOR melody IN training_melodies:
        FOR i FROM order TO length(melody)-1:
            # Extract context (previous 'order' notes)
            context ← tuple(melody[i-order:i])
            next_note ← melody[i]
            
            IF context NOT IN transitions:
                transitions[context] ← new HashMap()
            
            # Count occurrences for probability calculation
            IF next_note IN transitions[context]:
                transitions[context][next_note] += 1
            ELSE:
                transitions[context][next_note] ← 1
    
    # Convert counts to probabilities
    FOR context IN transitions.keys():
        total ← SUM(transitions[context].values())
        FOR note IN transitions[context].keys():
            transitions[context][note] ← transitions[context][note] / total
    
    ═══ STEP 2: Generate Initial Seed ═══
    # Select musically appropriate starting notes
    scale_notes ← getScaleNotes(key_signature)
    seed ← []
    
    FOR i FROM 0 TO order-1:
        # Start with tonic, dominant, or subdominant
        IF i == 0:
            seed.append(Note{
                pitch: scale_notes[0],  # Tonic
                duration: 1.0,           # Quarter note
                velocity: 80
            })
        ELSE:
            # Choose from chord tones
            seed.append(Note{
                pitch: RANDOM_CHOICE(scale_notes[0:3]),
                duration: RANDOM_CHOICE([0.5, 1.0]),
                velocity: RANDOM_INT(60, 90)
            })
    
    generated_melody ← seed.copy()
    
    ═══ STEP 3: Generate Melody Using Markov Chain ═══
    WHILE length(generated_melody) < length:
        # Get current context
        current_context ← tuple(generated_melody[-order:])
        
        IF current_context IN transitions:
            # Weighted random selection based on probabilities
            candidates ← transitions[current_context]
            next_note ← weightedRandomChoice(candidates)
            
            # Apply musical constraints
            next_note ← applyMusicalRules(next_note, key_signature, generated_melody)
            
        ELSE:
            # Fallback: generate musically sensible note
            prev_note ← generated_melody[-1]
            next_note ← generateFallbackNote(prev_note, scale_notes)
        
        generated_melody.append(next_note)
    
    ═══ STEP 4: Generate Harmony (Chord Progression) ═══
    harmony ← []
    chord_progression ← getCommonProgression(key_signature)  # e.g., I-IV-V-I
    
    FOR i FROM 0 TO length STEP 4:  # Change chord every measure
        chord_index ← (i / 4) % length(chord_progression)
        chord ← buildChord(chord_progression[chord_index], key_signature)
        harmony.append(chord)
    
    ═══ STEP 5: Apply Musical Post-Processing ═══
    generated_melody ← smoothMelodyTransitions(generated_melody)
    generated_melody ← enforceRhythmicPatterns(generated_melody, tempo)
    generated_melody ← addDynamicExpression(generated_melody)
    
    RETURN generated_melody, harmony
END FUNCTION

▶ HELPER FUNCTIONS:
FUNCTION applyMusicalRules(note, key_signature, melody_so_far):
    # Prevent awkward intervals
    IF abs(note.pitch - melody_so_far[-1].pitch) > 12:  # Octave jump
        note.pitch ← melody_so_far[-1].pitch + RANDOM_INT(-5, 5)
    
    # Ensure note is in key
    IF note.pitch NOT IN getScaleNotes(key_signature):
        note.pitch ← nearestScaleNote(note.pitch, key_signature)
    
    # Resolve leading tones
    IF isLeadingTone(melody_so_far[-1].pitch, key_signature):
        note.pitch ← resolveTone(melody_so_far[-1].pitch, key_signature)
    
    RETURN note
END FUNCTION

▶ MUSICAL CONSTRAINTS:
  • Avoid tritones (augmented 4th) unless in jazz mode
  • Resolve 7th scale degree to tonic
  • Limit range to 2 octaves for singability
  • End phrases on stable tones (1st, 3rd, 5th degree)
```