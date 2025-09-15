from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Header with module title centered at the top
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Module 1: Unobtrusive Environmental Awareness", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        # Chapter title styling
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def chapter_body(self, body):
        # Body text styling with multi-cell for automatic text wrapping
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
    "- Develop an open, receptive sensory field to notice subtle environmental details.\n"
    "- Train the eyes and ears to capture peripheral movements and layered ambient sounds.\n"
    "- Build spatial awareness by mapping static environments and recognizing dynamic transitions."
)
pdf.chapter_body(learning_objectives)

# --------------------------
# Exercises & Robust Explanations Section
# --------------------------
pdf.chapter_title("Exercises & Robust Explanations:")

exercises = [
    {
        "title": "Peripheral Scan:",
        "activity": ("Activity: In a setting such as a bus stop or park, allow your gaze to relax and scan the edges of your vision. "
                     "Notice subtle movements like birds taking flight or branches swaying in the breeze."),
        "explanation": ("Explanation: This exercise trains you to expand your field of awareness beyond a narrow focus. "
                        "By learning to capture peripheral details, you become sensitive to nuances that often go unnoticed, "
                        "thereby enhancing your overall environmental perception.")
    },
    {
        "title": "Soundscape Sampling:",
        "activity": ("Activity: In locations like coffee shops or train stations, sit quietly and listen to the mix of background sounds - "
                     "distant conversations, ambient music, traffic hum, and natural sounds. Avoid zeroing in on a single source."),
        "explanation": ("Explanation: The goal is to develop an ear for complex sound layers, learning to differentiate and appreciate "
                        "the subtleties within the auditory environment. This improves your ability to notice shifts in tone and ambient "
                        "sound quality over time.")
    },
    {
        "title": "Light & Shadow Play:",
        "activity": ("Activity: Observe how light interacts with your surroundings, noting how shadows shift as the day progresses or as you move. "
                     "For example, watch how a lamppost's shadow drifts across a pavement."),
        "explanation": ("Explanation: This exercise sharpens your ability to see dynamic visual effects created by light. It helps you understand "
                        "how changes in illumination can alter the mood or character of an environment, emphasizing the transient nature of visual details.")
    },
    {
        "title": "Spatial Layout Insight:",
        "activity": ("Activity: Choose a static environment such as a café or museum. Mentally map the space - its layout, seating, decor, and focal points. "
                     "Sketch a rough diagram to capture your perception of the space."),
        "explanation": ("Explanation: This activity develops your ability to construct an internal blueprint of an environment. It reinforces spatial awareness "
                        "by challenging you to note structural details and the arrangement of objects, which can inform how people interact within that space.")
    },
    {
        "title": "Environmental Transition:",
        "activity": ("Activity: As you move from one space to another (e.g., stepping from an outdoor area into a lobby), consciously note the changes "
                     "in ambiance such as temperature, lighting, and sound. Record your observations in a journal or quick sketch."),
        "explanation": ("Explanation: This exercise focuses on dynamic shifts rather than static details. It encourages you to be attentive to the subtle cues "
                        "that mark the boundary between different environments, deepening your understanding of how transitions impact perception.")
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
    "Observation Skills:\n"
    "   - Sensory Calibration: Training your eyes to notice peripheral details and your ears to distinguish ambient sounds.\n"
    "   - Visual Perception & Spatial Awareness: Recognizing dynamic light patterns and constructing internal maps of spatial layouts.\n\n"
    "Critical Thinking Skills:\n"
    "   - Analytical Observation: Objectively gathering sensory details and questioning the obvious.\n"
    "   - Reflective Inquiry: Evaluating personal perceptual biases and drawing initial inferences from raw input.\n\n"
    "Drawing/Sketching/Visualization Skills:\n"
    "   - Visual Notetaking & Gesture Sketching: Capturing the essence of movement and ambient details quickly.\n"
    "   - Rendering Light & Shadow: Using shading and contrast to depict dynamic visual effects.\n"
    "   - Color and Mood Visualization: Selecting ambient palettes and creating fast sketches that capture the overall feel of a space."
)
pdf.chapter_body(related_skills)

# Save the PDF to a file
pdf.output("Module1_Unobtrusive_Environmental_Awareness.pdf")
