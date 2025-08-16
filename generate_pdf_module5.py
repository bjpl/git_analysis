from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Add a header with the module title centered at the top
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Module 5: Narrative Synthesis and Situational Storylines", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        # Section title formatting
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
    "- Integrate sensory, temporal, and social observations into coherent, compelling narratives.\n"
    "- Develop skills to articulate and visually present rich situational storylines.\n"
    "- Enhance interpretative abilities by linking discrete observations into broader contexts."
)
pdf.chapter_body(learning_objectives)

# --------------------------
# Exercises & Robust Explanations Section
# --------------------------
pdf.chapter_title("Exercises & Robust Explanations:")

exercises = [
    {
        "title": "Echoes of Movement:",
        "activity": ("Activity: Observe the kinetic energy and rhythmic flow in public spaces (e.g., surges at bus stations) "
                     "and translate this into narrative sketches."),
        "explanation": ("Explanation: This exercise trains you to capture the dynamic movement and energy in a space. "
                        "By translating these kinetic elements into narrative sketches, you develop a skill for transforming raw motion "
                        "into compelling visual storytelling.")
    },
    {
        "title": "Subtle Environmental Markers:",
        "activity": ("Activity: Identify and record understated physical details (e.g., scuffed benches, faded graffiti, abandoned objects) "
                     "that hint at a location's history or character."),
        "explanation": ("Explanation: This exercise sharpens your observational skills by encouraging you to notice the subtle markers "
                        "that reveal a deeper story. These details can serve as clues to a location's past and provide context for its current atmosphere.")
    },
    {
        "title": "Social Topography & Transitional Snapshots:",
        "activity": ("Activity: Map out social layouts and capture transitional moments (e.g., shifts from day to evening) in communal settings, "
                     "emphasizing both spatial arrangement and temporal evolution."),
        "explanation": ("Explanation: This exercise combines spatial observation with temporal awareness. "
                        "By mapping social arrangements and documenting transitions, you develop an ability to narrate the evolving story of a space, "
                        "linking visual details with the passage of time.")
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
    "   - Integrative Thinking:\n"
    "       * Holistic Perception: Merging multiple sensory and contextual strands into one unified view.\n"
    "       * Analytical Integration: Linking observations across time, space, and social dynamics.\n\n"
    "   - Creative Storytelling:\n"
    "       * Narrative Construction: Weaving diverse observations into a compelling story.\n"
    "       * Storyboarding: Organizing visual or sequential representations to map out a narrative.\n\n"
    "   - Interpretative Analysis:\n"
    "       * Contextual Analysis: Connecting subtle cues to broader historical, social, or cultural contexts.\n"
    "       * Creative Synthesis: Transforming raw data into layered, interpretative storylines.\n\n"
    "Related Critical Thinking Skills and Subskills:\n"
    "   - Evaluative Reasoning:\n"
    "       * Critical Synthesis: Assessing multiple data sources to construct a cohesive narrative.\n"
    "       * Judgment and Analysis: Weighing the significance of individual observations within a broader context.\n\n"
    "   - Argumentation and Presentation:\n"
    "       * Coherent Structuring: Organizing observations logically to present a persuasive narrative.\n"
    "       * Reflective Critique: Analyzing and refining narrative interpretations through feedback.\n\n"
    "Related Drawing/Sketching/Visualization Skills and Subskills:\n"
    "   - Narrative Visualization:\n"
    "       * Storyboarding: Planning and sketching sequential frames to visually tell a story.\n"
    "       * Sequential Drawing: Creating a series of images that capture the progression of a narrative.\n\n"
    "   - Integrative Composition:\n"
    "       * Complex Scene Rendering: Combining background, figures, and details into a unified illustration.\n"
    "       * Perspective and Depth: Utilizing overlapping, scale variation, and perspective techniques to build a narrative scene.\n\n"
    "   - Expressive Sketching:\n"
    "       * Mood and Atmosphere: Using line quality, shading, and color to evoke emotion and context.\n"
    "       * Visual Metaphor: Incorporating symbolic elements that hint at a deeper story or theme."
)
pdf.chapter_body(related_skills)

# Save the PDF to a file
pdf.output("Module5_Narrative_Synthesis_and_Situational_Storylines.pdf")
