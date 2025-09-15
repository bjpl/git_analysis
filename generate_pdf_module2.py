from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Add a header with the module title centered at the top
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Module 2: Subtle Social Observation", ln=True, align="C")
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
    "- Identify and interpret fleeting nonverbal cues and micro-expressions.\n"
    "- Understand group dynamics and the overall energy of social spaces.\n"
    "- Enhance listening skills to perceive the rhythm and tone of conversations."
)
pdf.chapter_body(learning_objectives)

# --------------------------
# Exercises & Robust Explanations Section
# --------------------------
pdf.chapter_title("Exercises & Robust Explanations:")

exercises = [
    {
        "title": "Group Dynamics Glance:",
        "activity": ("Activity: In spaces like cafés or public parks, observe overall body language and group formations. "
                     "Note how individuals cluster, interact, and communicate nonverbally."),
        "explanation": ("Explanation: This exercise trains you to quickly assess the social environment. "
                        "By observing group dynamics, you develop an understanding of how collective energy is manifested, "
                        "which can provide insights into the social structure and interpersonal relationships within a space.")
    },
    {
        "title": "Nonverbal Nuance:",
        "activity": ("Activity: Focus on expressive facial gestures and deliberate body language in settings such as grocery stores or public transit. "
                     "Observe brief smiles, nods, or other subtle signals that convey emotion."),
        "explanation": ("Explanation: This exercise sharpens your ability to read individual expressions. "
                        "By concentrating on nonverbal nuances, you enhance your sensitivity to the emotional subtext in social interactions, "
                        "enabling a deeper understanding of unspoken communication.")
    },
    {
        "title": "Micro-Movement Monitoring:",
        "activity": ("Activity: In busy environments like malls or train stations, capture rapid, near-imperceptible movements such as "
                     "slight fidgets or subtle eye twitches."),
        "explanation": ("Explanation: This exercise encourages you to notice micro-level behaviors that are often overlooked. "
                        "Such small movements can reveal underlying emotions or social cues, contributing to a more refined perception of interpersonal dynamics.")
    },
    {
        "title": "Dynamic Dialogues (Listening In):",
        "activity": ("Activity: In events or open-plan offices, listen to the cadence, rhythm, and tone of conversations without focusing on the specific content."),
        "explanation": ("Explanation: This exercise develops your auditory sensitivity by attuning you to the musicality and emotional rhythm of speech. "
                        "It helps you capture the overall mood and energy of social interactions, beyond the literal words being spoken.")
    },
    {
        "title": "Reflective Awareness:",
        "activity": ("Activity: Use reflective surfaces, such as storefront windows, to simultaneously observe the social scene and your own reactions. "
                     "Notice how your feelings align or contrast with the observed environment."),
        "explanation": ("Explanation: This exercise promotes self-awareness by encouraging you to reflect on your internal responses. "
                        "It helps you understand how your perceptions might be influenced by personal biases and enhances your ability to interpret social cues objectively.")
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
    "   - Social Perception:\n"
    "       * Nonverbal Cue Detection: Recognizing facial expressions and gestures.\n"
    "       * Group Dynamics Analysis: Understanding how individuals interact within clusters.\n\n"
    "   - Emotional Intelligence:\n"
    "       * Empathetic Observation: Interpreting the underlying emotional tone.\n"
    "       * Active Listening: Sensing mood through voice intonation and rhythm.\n\n"
    "   - Self-Reflective Awareness:\n"
    "       * Mirror Observations: Using reflections to compare external signals with internal reactions.\n\n"
    "Related Critical Thinking Skills and Subskills:\n"
    "   - Inferential Reasoning:\n"
    "       * Contextual Inference: Drawing conclusions from subtle social cues.\n"
    "       * Deductive Analysis: Assembling brief signals into a coherent social understanding.\n\n"
    "   - Perspective-Taking:\n"
    "       * Empathetic Reasoning: Considering multiple viewpoints in social interactions.\n"
    "       * Bias Evaluation: Questioning personal preconceptions in interpreting social cues.\n\n"
    "Related Drawing/Sketching/Visualization Skills and Subskills:\n"
    "   - Figure Sketching:\n"
    "       * Gesture Drawing: Capturing human posture and movement quickly in varied contexts.\n"
    "       * Expression Studies: Focusing on facial expressions and micro changes in emotion.\n\n"
    "   - Social Scene Composition:\n"
    "       * Group Arrangement Sketches: Visualizing spatial relationships and interactions among groups.\n"
    "       * Dynamic Interaction Rendering: Illustrating the energy and flow of social exchanges.\n\n"
    "   - Observational Sketch Journaling:\n"
    "       * Sequential Sketching: Documenting a series of quick sketches to capture evolving interactions.\n"
    "       * Emotion and Tone Visualization: Using line quality and shading to represent mood."
)
pdf.chapter_body(related_skills)

# Save the PDF to a file
pdf.output("Module2_Subtle_Social_Observation.pdf")
