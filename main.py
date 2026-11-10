from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI()

# Free Gemini API key
client = genai.Client(api_key="AQ.Ab8RN6IxQKLtKl4qJFljaZkn74UBLuwOKOGDIMX4wKuQxxH7ow")

# Placeholder values
class SceneContext(BaseModel):
    sun_angle: Optional[float] = 0.0
    louver_angle: Optional[float] = 0.0
    season: Optional[str] = "Summer"

class StudentData(BaseModel):
    failed_attempts: int
    heart_rate: float
    puzzle_name: str
    student_question: Optional[str] = ""
    scene_context: Optional[SceneContext] = None

@app.post("/tutor")
def get_tutor_help(data: StudentData):
    print(f"Received data: {data.failed_attempts} mistakes, {data.heart_rate} BPM")
    
    # Rule-based learner model for scaffolding
    if data.failed_attempts >= 3 or data.heart_rate > 110:
        scaffold_level = 5  # Give full explanation
    elif data.failed_attempts == 2:
        scaffold_level = 3  # Give hint
    elif data.failed_attempts == 1:
        scaffold_level = 1  # Ask socratic question
    else:
        scaffold_level = 0

    if scaffold_level == 0 and not data.student_question:
        return {"response": ""}

    # Unity scene data
    sun = data.scene_context.sun_angle if data.scene_context else 0
    louver = data.scene_context.louver_angle if data.scene_context else 0
    season = data.scene_context.season if data.scene_context else "Summer"

    # Create Gemini prompt
    q = data.student_question.strip() if data.student_question else ""
    
    if q:
        prompt = (
            f"You are a sustainable construction VR AI tutor. "
            f"The student is on the '{data.puzzle_name}' puzzle. "
            f"Answer this student\'s question about the sustainable building in no more than 3 sentences, and keep the language simple yet informative: '{q}'. "
            f"Context -> Sun angle: {sun}°, Louver angle: {louver}°, Season: {season}. "
            f"Match tone for scaffolding level {scaffold_level}."
            f"Format the text in plain English, do not use coding or markdown formatting in the response."
        )
    else:
        prompt = (
            f"You are a sustainable construction VR AI tutor."
            f"Never invent or hallucinate information outside of the Unity scene or the student data."
            f"The student is stuck on '{data.puzzle_name}'."
            f"They have failed {data.failed_attempts} times and their heart rate is {data.heart_rate} BPM."
            f"Unity scene data context: Sun angle: {sun}°, Louver angle: {louver}°, Season: {season}."
            f"Give a short hint matching the scaffolding level {scaffold_level}."
        )

    # Gemini models available to access
    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.6-flash"
    ]

    for model_name in models_to_try:
        try:
            print(f"Trying model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return {
                "scaffold_level": scaffold_level,
                "response": response.text
            }
        except Exception as error:
            print(f"Model {model_name} didn't work: {error}")
            continue

    return {"response": "Take a deep breath and re-check your answer."}