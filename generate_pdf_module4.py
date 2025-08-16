from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Add a header with the module title centered at the top
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Module 4: Micro-Contextual Observations", ln=True, align="C")
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
    "- Enhance focused attention to capture minute environmental and social details.\n"
    "- Integrate multiple sensory inputs into a cohesive, detailed snapshot.\n"
    "- Recognize the significance of transient, split-second interactions and physical markers."
)
pdf.chapter_body(learning_objectives)

# --------------------------
# Exercises & Robust Explanations Section
# --------------------------
pdf.chapter_title("Exercises & Robust Explanations:")

exercises = [
    {
        "title": "Energy Pulse:",
        "activity": ("Activity: Document surges and lulls in busy settings (e.g., train stations or markets) by noting fluctuations "
                     "in crowd energy."),
        "explanation": ("Explanation: This exercise trains you to capture the rhythmic ebb and flow of human activity. By observing "
                        "energy pulses, you gain insights into the collective mood and behavior patterns of a dynamic environment.")
    },
    {
        "title": "Contextual Intersections:",
        "activity": ("Activity: Observe areas where distinct environments meet (e.g., café entrances or building atriums) to capture immediate "
                     "shifts in behavior and ambiance."),
        "explanation": ("Explanation: This exercise focuses on the boundaries where different influences converge. It helps you notice how "
                        "transitions create unique micro-environments that are rich in detail and change rapidly.")
    },
    {
        "title": "Invisible Social Scripts:",
        "activity": ("Activity: Decode brief, unspoken social norms (e.g., customary nods or pauses) in structured settings like workplaces or "
                     "community meetings."),
        "explanation": ("Explanation: This exercise sharpens your ability to read subtle social signals. Recognizing these unspoken scripts "
                        "enhances your understanding of how implicit rules guide interactions in various settings.")
    },
    {
        "title": "Temporal Micro-Interactions & Hidden Narratives:",
        "activity": ("Activity: Focus on fleeting physical cues and small markers (e.g., faded graffiti, transient glances) that hint at the deeper "
                     "history or character of a place."),
        "explanation": ("Explanation: By observing these minute details, you learn to extract hidden narratives from seemingly insignificant elements. "
                        "This exercise develops your skill in reading between the lines to uncover a place's backstory.")
    },
    {
        "title": "Ambient Detail Weave:",
        "activity": ("Activity: Blend diverse sensory details (colors, sounds, aromas) into one integrated observation, particularly in complex settings "
                     "such as street fairs or markets."),
        "explanation": ("Explanation: This exercise reinforces the art of multi-sensory integration. By weaving together different sensory inputs, "
                        "you create a rich, holistic snapshot that captures the essence of a bustling environment.")
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
    "   - Focused Attention:\n"
    "       * Detail Orientation: Observing and retaining minute visual and auditory cues.\n"
    "       * Rapid Processing: Capturing split-second interactions in busy environments.\n\n"
    "   - Sensory Integration:\n"
    "       * Multi-Sensory Synthesis: Combining visual, auditory, and tactile information for a holistic view.\n"
    "       * Contextual Intersection Recognition: Noticing nuanced changes where environments merge.\n\n"
    "   - Micro-Cue Analysis:\n"
    "       * Subtle Interaction Detection: Identifying barely perceptible signals that hint at larger dynamics.\n"
    "       * Hidden Narrative Extraction: Recognizing small markers that contribute to a broader story.\n\n"
    "Related Critical Thinking Skills and Subskills:\n"
    "   - Synthesis of Information:\n"
    "       * Integrative Analysis: Merging disparate details into a coherent picture.\n"
    "       * Selective Focus: Prioritizing micro-details with broader implications.\n\n"
    "   - Hypothesis Formation:\n"
    "       * Inference from Minimal Data: Formulating interpretations based on fleeting observations.\n"
    "       * Iterative Reflection: Reassessing initial impressions as new data emerges.\n\n"
    "Related Drawing/Sketching/Visualization Skills and Subskills:\n"
    "   - Detail Rendering:\n"
    "       * Close-Up Sketching: Focusing on textures and fine details observed in micro-interactions.\n"
    "       * Precision Drawing: Using fine lines and careful shading to capture subtle elements.\n\n"
    "   - Focused Visual Studies:\n"
    "       * Zoomed-In Compositions: Creating sketches that isolate key micro-details.\n"
    "       * Texture and Pattern Exploration: Experimenting with techniques to depict subtle visual textures.\n\n"
    "   - Integrated Visual Synthesis:\n"
    "       * Composite Sketching: Combining multiple micro-details into a unified image.\n"
    "       * Layering Techniques: Using overlapping elements to convey depth and complexity."
)
pdf.chapter_body(related_skills)

# Save the PDF to a file
pdf.output("Module4_Micro_Contextual_Observations.pdf")
