from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Add a header with the module title centered at the top
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Module 3: Temporal and Contextual Dynamics", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        # Title formatting for sections
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def chapter_body(self, body):
        # Body text formatting with multi-cell for wrapping text
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 8, body)
        self.ln(4)

# Create an instance of PDF and add a page
pdf = PDF()
pdf.add_page()

# --------------------------
# Learning Objectives Section
# --------------------------
pdf.chapter_title("Learning Objectives:")
learning_objectives = (
    "- Recognize and track how environments and social settings evolve over time.\n"
    "- Develop skills to detect subtle shifts in mood, light, and ambient sound.\n"
    "- Understand the role of temporal changes in shaping perception."
)
pdf.chapter_body(learning_objectives)

# --------------------------
# Exercises & Robust Explanations Section
# --------------------------
pdf.chapter_title("Exercises & Robust Explanations:")

exercises = [
    {
        "title": "Temporal Flow Perception:",
        "activity": ("Activity: Observe gradual environmental changes (e.g., morning mist dissipating on a park bench) "
                     "over a defined time period."),
        "explanation": ("Explanation: This exercise trains you to notice slow, progressive changes in your surroundings. "
                        "By documenting these changes, you become adept at recognizing how time influences the atmosphere and mood of a space.")
    },
    {
        "title": "Invisible Interactions:",
        "activity": ("Activity: Note fleeting social cues (e.g., a brief exchange of eye contact) that occur over time, "
                     "emphasizing how they fit into the larger temporal context."),
        "explanation": ("Explanation: This exercise focuses on capturing subtle, transient social interactions within a temporal continuum. "
                        "It helps you understand how even momentary signals contribute to the evolving social fabric of a setting.")
    },
    {
        "title": "Movement Patterns & Environmental Micro-Shifts:",
        "activity": ("Activity: Map pedestrian flow or capture subtle shifts (e.g., a streetlight flickering) "
                     "at busy intersections or campuses."),
        "explanation": ("Explanation: This activity develops your ability to detect and record micro-level changes in dynamic environments. "
                        "Observing movement patterns helps you understand how human activity interacts with environmental cues.")
    },
    {
        "title": "Contextual Focus:",
        "activity": ("Activity: Compare similar spaces (e.g., a bright café vs. a dim bookstore) to understand how differing ambiance affects behavior."),
        "explanation": ("Explanation: This exercise encourages you to analyze how environmental context influences human behavior. "
                        "By contrasting different settings, you sharpen your ability to assess how subtle variations in ambiance impact perception.")
    }
]

for ex in exercises:
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, ex["title"], ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, ex["activity"])
    pdf.multi_cell(0, 8, ex["explanation"])
    pdf.ln(3)

# --------------------------
# Related Skills Section
# --------------------------
pdf.chapter_title("Related Skills:")

related_skills = (
    "Related Observation Skills and Subskills:\n"
    "   - Temporal Awareness:\n"
    "       * Time-Based Observation: Monitoring changes over minutes, hours, or days.\n"
    "       * Pattern Recognition: Identifying trends and shifts over time.\n\n"
    "   - Dynamic Change Detection:\n"
    "       * Mood Shift Analysis: Sensing changes in atmosphere or emotional tone.\n"
    "       * Contextual Contrast Analysis: Comparing different settings for environmental cues.\n\n"
    "   - Situational Awareness:\n"
    "       * Environmental Sensitivity: Recognizing both immediate and gradual shifts in surroundings.\n\n"
    "Related Critical Thinking Skills and Subskills:\n"
    "   - Comparative Analysis:\n"
    "       * Trend Evaluation: Assessing how and why changes occur over time.\n"
    "       * Contrast and Similarity: Drawing parallels and differences between temporal snapshots.\n\n"
    "   - Causal Reasoning:\n"
    "       * Cause-and-Effect Analysis: Evaluating how subtle shifts (lighting, sound) influence overall mood.\n"
    "       * Sequential Reasoning: Understanding the order of events and their impact.\n\n"
    "Related Drawing/Sketching/Visualization Skills and Subskills:\n"
    "   - Sequential Visualization:\n"
    "       * Time-Lapse Sketching: Creating a series of sketches that document the evolution of a scene.\n"
    "       * Comparative Scene Studies: Drawing the same location under different conditions (morning vs. evening).\n\n"
    "   - Dynamic Composition:\n"
    "       * Transitional Sketching: Emphasizing shifts in light, color, and form as time changes.\n"
    "       * Motion Capture Techniques: Using quick strokes to suggest movement within a static scene.\n\n"
    "   - Contextual Rendering:\n"
    "       * Atmospheric Effects: Employing shading and texture to express ambient changes.\n"
    "       * Perspective Shifts: Adjusting spatial viewpoints to reflect evolving conditions."
)
pdf.chapter_body(related_skills)

# Save the PDF to a file
pdf.output("Module3_Temporal_and_Contextual_Dynamics.pdf")
